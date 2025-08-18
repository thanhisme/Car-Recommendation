# models/breakdown_item.py
from dataclasses import dataclass

@dataclass
class BreakdownItem:
    """
    BreakdownItem
    Đại diện cho một loại chi phí trong breakdown TCO
    """

    value: float         # Giá trị chi phí
    explanation: dict    # Giải thích chi tiết về chi phí

