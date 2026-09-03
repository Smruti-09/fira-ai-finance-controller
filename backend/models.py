from pydantic import BaseModel
from typing import Optional
from enum import Enum

# 1. Define the possible outcomes for a transaction
class MatchStatus(str, Enum):
    MATCHED = "MATCHED"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    DATE_MISMATCH = "DATE_MISMATCH"
    MISSING_RECORD = "MISSING_RECORD"
    DUPLICATE = "DUPLICATE"
    FUZZY_MATCHED = "FUZZY_MATCHED"
    UNRESOLVED = "UNRESOLVED"

# 2. Define the exact structure of our final output
class ReconciliationResult(BaseModel):
    order_id: str
    payment_id: Optional[str] = None
    settlement_id: Optional[str] = None
    
    expected_amount: float
    actual_settled_amount: Optional[float] = None
    discrepancy: float = 0.0
    
    status: MatchStatus
    reason: str
    requires_human_review: bool = False
    ground_truth_label: Optional[str] = "EXACT_MATCH"