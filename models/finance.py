# models/finance.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class Finance:
    payment_method: str   # "cash" | "loan" | "lease"
    cash_budget: Optional[float] = None
    monthly_capacity: Optional[float] = None

    def __str__(self):
        if self.payment_method == "cash" and self.cash_budget is not None:
            return f"Thanh toán tiền mặt, ngân sách ~{self.cash_budget:.2f} USD"
        elif self.payment_method in ["loan", "lease"] and self.monthly_capacity is not None:
            return f"{self.payment_method.capitalize()}, khả năng trả mỗi tháng ~{self.monthly_capacity:.2f} USD"
        else:
            return f"Phương thức {self.payment_method}, chưa có thông tin chi tiết"
