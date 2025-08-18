from dataclasses import dataclass, field, asdict
from typing import List

@dataclass
class Voucher:
    """
    Voucher
    Đại diện cho một ưu đãi/voucher áp dụng cho xe hoặc người dùng.
    """
    id: str                                 # Mã định danh voucher
    title: str                              # Tiêu đề voucher
    description: str                        # Mô tả chi tiết voucher
    conditions_apply_text: str              # Điều kiện áp dụng (text)
    valid_until: str                        # Ngày hết hạn (ISO format)
    type: str                               # Loại voucher
    value: float                            # Giá trị voucher
    applicable_makes: List[str] = field(default_factory=list)      # Hãng xe áp dụng
    applicable_models: List[str] = field(default_factory=list)     # Model xe áp dụng
    applicable_years: List[int] = field(default_factory=list)      # Năm sản xuất xe áp dụng
    excluded_trims: List[str] = field(default_factory=list)        # Phiên bản xe không áp dụng
    member_levels: List[str] = field(default_factory=list)         # Hạng thành viên áp dụng
    min_vehicle_price: float = 0.0           # Giá xe tối thiểu để áp dụng

