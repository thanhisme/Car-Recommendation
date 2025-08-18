# models/finance.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class Finance:
    payment_method: str   # "cash" | "loan" | "lease"
    cash_budget: Optional[float] = None
    monthly_capacity: Optional[float] = None