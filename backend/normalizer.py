import pandas as pd
import re
from pathlib import Path

class DataNormalizer:
    @staticmethod
    def clean_id(val: str) -> str:
        """Strip whitespaces and standardize casing."""
        if pd.isna(val):
            return ""
        return str(val).strip().upper()

    @staticmethod
    def extract_order_num(val: str) -> str:
        """Extract core numeric reference from fuzzy IDs like 'REF_ORD-1001' -> '1001'."""
        if pd.isna(val):
            return ""
        val = str(val).strip()
        # Find the first sequence of numbers in the string
        match = re.search(r'(\d+)', val)
        return match.group(1) if match else val

    @classmethod
    def load_and_normalize(cls, data_dir: str = "../data"):
        data_path = Path(data_dir)
        
        # 1. Load the CSVs you just generated
        orders_df = pd.read_csv(data_path / "merchant_orders.csv")
        payments_df = pd.read_csv(data_path / "payment_records.csv")
        settlements_df = pd.read_csv(data_path / "bank_settlements.csv")

        # 2. Normalize Orders
        orders_df["order_id"] = orders_df["order_id"].apply(cls.clean_id)
        orders_df["order_num"] = orders_df["order_id"].apply(cls.extract_order_num)
        orders_df["amount"] = orders_df["order_amount"].astype(float).round(2)
        orders_df["order_date"] = pd.to_datetime(orders_df["order_date"]).dt.date

        # 3. Normalize Payments
        payments_df["payment_id"] = payments_df["payment_id"].apply(cls.clean_id)
        payments_df["order_reference"] = payments_df["order_ref"].apply(cls.clean_id)
        payments_df["order_num"] = payments_df["order_reference"].apply(cls.extract_order_num)
        payments_df["amount"] = payments_df["paid_amount"].astype(float).round(2)
        payments_df["payment_date"] = pd.to_datetime(payments_df["payment_date"])

        # 4. Normalize Settlements
        settlements_df["settlement_id"] = settlements_df["settlement_id"].apply(cls.clean_id)
        settlements_df["payment_reference"] = settlements_df["payment_ref"].apply(cls.clean_id)
        settlements_df["amount"] = settlements_df["settled_amount"].astype(float).round(2)
        settlements_df["settlement_date"] = pd.to_datetime(settlements_df["settlement_date"]).dt.date

        return orders_df, payments_df, settlements_df