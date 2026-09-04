import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid
import os

def generate_synthetic_finance_data(total_records=500, seed=42):
    np.random.seed(seed)
    random.seed(seed)

    base_date = datetime(2026, 3, 1, 10, 0, 0)

    merchant_rows = []
    payment_rows = []
    bank_rows = []

    customers = [f"Customer_{i:03d}" for i in range(1, 100)]

    for i in range(1, total_records + 1):
        order_id = f"ORD-{1000 + i}"
        cust = random.choice(customers)
        base_amount = round(random.uniform(500.0, 50000.0), 2)
        txn_date = base_date + timedelta(minutes=random.randint(0, 1440 * 30)) # 30-day spread

        if i <= 370:
            category = "EXACT_MATCH"
        elif i <= 420:
            category = "AMOUNT_MISMATCH"
        elif i <= 455:
            category = "MISSING_RECORD"
        elif i <= 480:
            category = "DATE_MISMATCH"
        elif i <= 490:
            category = "DUPLICATE"
        else:
            category = "FUZZY_REFERENCE"

        # 1. Merchant Order
        merchant_rows.append({
            "order_id": order_id,
            "customer_id": cust,
            "order_amount": base_amount,
            "order_date": txn_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "COMPLETED",
            "ground_truth_label": category
        })

        # 2. Payment Gateway Record
        pay_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        pay_amount = base_amount
        pay_date = txn_date + timedelta(seconds=random.randint(10, 300))
        pay_ref = order_id
        pay_status = "SUCCESS"

        if category == "AMOUNT_MISMATCH":
            # Gateway fee deduction or delta, including some high-risk values > 5000
            pay_amount = round(base_amount - random.choice([49.50, 150.00, 320.50, 1250.00, 6200.00]), 2)
        elif category == "FUZZY_REFERENCE":
            pay_ref = random.choice([order_id.replace("-", ""), f"REF_{order_id}", order_id.lower()])

        if category != "MISSING_RECORD" or random.random() > 0.5:
            payment_rows.append({
                "payment_id": pay_id,
                "order_ref": pay_ref,
                "paid_amount": pay_amount,
                "payment_date": pay_date.strftime("%Y-%m-%d %H:%M:%S"),
                "gateway_status": pay_status
            })

            # Add duplicate edge case
            if category == "DUPLICATE":
                payment_rows.append({
                    "payment_id": f"PAY-{uuid.uuid4().hex[:8].upper()}",
                    "order_ref": pay_ref,
                    "paid_amount": pay_amount,
                    "payment_date": (pay_date + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S"),
                    "gateway_status": pay_status
                })

        # 3. Bank Settlement Record
        bank_ref = pay_id
        bank_amount = pay_amount
        bank_date = pay_date + timedelta(days=random.randint(1, 2))

        if category == "DATE_MISMATCH":
            bank_date = pay_date + timedelta(days=random.randint(8, 25)) # Exceeds 3-day SLA
        elif category == "AMOUNT_MISMATCH" and random.random() > 0.5:
            bank_amount = round(pay_amount - random.choice([15.0, 50.0, 200.0]), 2) # Secondary bank processing fee delta

        if category != "MISSING_RECORD" or random.random() > 0.6:
            bank_rows.append({
                "settlement_id": f"STL-{uuid.uuid4().hex[:8].upper()}",
                "payment_ref": bank_ref,
                "settled_amount": bank_amount,
                "settlement_date": bank_date.strftime("%Y-%m-%d %H:%M:%S"),
                "bank_code": random.choice(["HDFC_01", "ICICI_CORP", "SBI_SETTL", "AXIS_BULK"])
            })

    df_merchant = pd.DataFrame(merchant_rows)
    df_payments = pd.DataFrame(payment_rows)
    df_bank = pd.DataFrame(bank_rows)

    return df_merchant, df_payments, df_bank

if __name__ == "__main__":
    os.makedirs("../data", exist_ok=True)
    df_m, df_p, df_b = generate_synthetic_finance_data(500)
    df_m.to_csv("../data/merchant_orders.csv", index=False)
    df_p.to_csv("../data/payment_records.csv", index=False)
    df_b.to_csv("../data/bank_settlements.csv", index=False)
    print(f"Enterprise Data generated successfully: {len(df_m)} Orders, {len(df_p)} Payments, {len(df_b)} Bank records.")