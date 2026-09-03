import pandas as pd
from typing import List
from models import ReconciliationResult, MatchStatus

class ReconcilerEngine:
    def __init__(self, amount_tolerance: float = 0.5, date_tolerance_days: int = 3):
        # We allow a 50-cent tolerance for rounding/currency drift, and 3 days for bank SLA
        self.amount_tolerance = amount_tolerance
        self.date_tolerance_days = date_tolerance_days

    def reconcile(self, orders_df: pd.DataFrame, payments_df: pd.DataFrame, settlements_df: pd.DataFrame) -> List[ReconciliationResult]:
        results = []
        
        # Loop through every merchant order to track its lifecycle
        for _, order in orders_df.iterrows():
            order_id = order['order_id']
            order_num = order['order_num']
            expected_amt = order['amount']
            gt_label = order.get('ground_truth_label', 'EXACT_MATCH')
            
            # 1. Look for matching payments using the extracted number (e.g., '1001')
            matching_payments = payments_df[payments_df['order_num'] == order_num]
            
            # EDGE CASE: Missing Payment
            if matching_payments.empty:
                results.append(ReconciliationResult(
                    order_id=order_id,
                    expected_amount=expected_amt,
                    status=MatchStatus.MISSING_RECORD,
                    reason="No payment gateway record found for this order.",
                    requires_human_review=True,
                    ground_truth_label=gt_label  # Preserved for validation
                ))
                continue
                
            # EDGE CASE: Duplicate Payment (Double Charge)
            if len(matching_payments) > 1:
                p_ids = matching_payments['payment_id'].tolist()
                results.append(ReconciliationResult(
                    order_id=order_id,
                    payment_id=", ".join(p_ids),
                    expected_amount=expected_amt,
                    status=MatchStatus.DUPLICATE,
                    reason=f"Multiple payment records found: {p_ids}",
                    requires_human_review=True,
                    ground_truth_label=gt_label  # Preserved for validation
                ))
                continue
            
            # If we get here, exactly 1 payment was found. Let's extract its data.
            payment = matching_payments.iloc[0]
            payment_id = payment['payment_id']
            payment_ref_text = payment['order_reference']
            
            # 2. Look for a matching bank settlement using the payment_id
            matching_settlements = settlements_df[settlements_df['payment_reference'] == payment_id]
            
            # EDGE CASE: Missing Settlement
            if matching_settlements.empty:
                results.append(ReconciliationResult(
                    order_id=order_id,
                    payment_id=payment_id,
                    expected_amount=expected_amt,
                    status=MatchStatus.MISSING_RECORD,
                    reason="Payment succeeded but no bank settlement arrived.",
                    requires_human_review=True,
                    ground_truth_label=gt_label  # Preserved for validation
                ))
                continue
            
            # 3. Apply Hard Finance Rules (Amount and Date Checks)
            settlement = matching_settlements.iloc[0]
            settlement_id = settlement['settlement_id']
            actual_settled_amt = settlement['amount']
            
            # Calculate the differences
            discrepancy = round(abs(expected_amt - actual_settled_amt), 2)
            
            date_diff = 0
            if pd.notnull(settlement['settlement_date']) and pd.notnull(payment['payment_date']):
                # Calculate how many days it took the bank to settle the money
                date_diff = (pd.to_datetime(settlement['settlement_date']) - pd.to_datetime(payment['payment_date']).normalize()).days
            
            # EDGE CASE: Amount Mismatch (Hidden fees)
            if discrepancy > self.amount_tolerance:
                results.append(ReconciliationResult(
                    order_id=order_id,
                    payment_id=payment_id,
                    settlement_id=settlement_id,
                    expected_amount=expected_amt,
                    actual_settled_amount=actual_settled_amt,
                    discrepancy=discrepancy,
                    status=MatchStatus.AMOUNT_MISMATCH,
                    reason=f"Settlement differs from order amount by {discrepancy}.",
                    requires_human_review=True,
                    ground_truth_label=gt_label  # Preserved for validation
                ))
            
            # EDGE CASE: Date Mismatch (Late deposit)
            elif date_diff > self.date_tolerance_days:
                results.append(ReconciliationResult(
                    order_id=order_id,
                    payment_id=payment_id,
                    settlement_id=settlement_id,
                    expected_amount=expected_amt,
                    actual_settled_amount=actual_settled_amt,
                    status=MatchStatus.DATE_MISMATCH,
                    reason=f"Settlement took {date_diff} days (SLA limit is {self.date_tolerance_days}).",
                    requires_human_review=True,
                    ground_truth_label=gt_label  # Preserved for validation
                ))
            
            # SUCCESS: Perfect or Fuzzy Match
            else:
                is_fuzzy = (payment_ref_text != order_id) # True if the string was slightly altered like 'REF_ORD-1001'
                results.append(ReconciliationResult(
                    order_id=order_id,
                    payment_id=payment_id,
                    settlement_id=settlement_id,
                    expected_amount=expected_amt,
                    actual_settled_amount=actual_settled_amt,
                    status=MatchStatus.FUZZY_MATCHED if is_fuzzy else MatchStatus.MATCHED,
                    reason="Matched using extracted reference number." if is_fuzzy else "Exact 3-way match.",
                    requires_human_review=False,
                    ground_truth_label=gt_label  # Preserved for validation
                ))
                
        return results