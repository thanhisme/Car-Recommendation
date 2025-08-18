from dataclasses import dataclass

@dataclass
class TCOCalculatorSummary:
    """
    TCOCalculatorSummary
    Đại diện cho thông tin tóm tắt kết quả tính toán TCO
    """
    config: dict         # Cấu hình chi phí, thông tin vùng/bang
    profile: dict        # Thông tin người dùng
    annual_miles: int    # Số km đi hàng năm
    tco_total: float     # Tổng chi phí sở hữu xe
    breakdown: dict      # Chi tiết các loại chi phí
