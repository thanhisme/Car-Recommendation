from datetime import datetime
from models.voucher import Voucher
from typing import List

def get_discount_vouchers(vouchers: List[Voucher], vehicle, year: int, member_level: str) -> List[Voucher]:
    """
    Helper: filter các voucher giảm giá, chỉ lấy voucher còn hạn sử dụng
    """
    today = datetime.today().date()
    result = []
    for v in vouchers:
        if v.type != "discount":
            continue
        if not is_voucher_applicable(v, vehicle, year, member_level):
            continue
        try:
            valid_until = datetime.strptime(v.valid_until, "%Y-%m-%d").date()
            if valid_until < today:
                continue
        except Exception:
            continue
        result.append(v)
    return result


def is_voucher_applicable(voucher, vehicle, year: int, member_level: str) -> bool:
    """
    Kiểm tra voucher có áp dụng cho xe, năm, hạng thành viên không
    """
    # Kiểm tra hãng xe
    if voucher.applicable_makes and not (
        "*" in voucher.applicable_makes
        or "all" in voucher.applicable_makes
        or vehicle.make in voucher.applicable_makes
    ):
        return False

    # Kiểm tra model xe
    if voucher.applicable_models and not (
        "*" in voucher.applicable_models
        or "all" in voucher.applicable_models
        or vehicle.model in voucher.applicable_models
    ):
        return False

    # Kiểm tra năm
    if voucher.applicable_years and year not in voucher.applicable_years:
        return False

    # Kiểm tra trim loại trừ
    if voucher.excluded_trims and vehicle.trim in voucher.excluded_trims:
        return False

    # Kiểm tra hạng thành viên
    if voucher.member_levels and member_level not in voucher.member_levels:
        return False

    # Kiểm tra giá xe tối thiểu
    if vehicle.base_price < voucher.min_vehicle_price:
        return False

    return True
