
# utils/vector_utils.py
# Các hàm tiện ích xử lý vector cho bài toán gợi ý xe, tìm kiếm ngữ nghĩa, chuẩn hóa điểm số.
#
# - minmax_scale: Chuẩn hóa danh sách giá trị về khoảng [0, 1].
# - safe_float: Chuyển đổi giá trị sang float an toàn, tránh lỗi dữ liệu.
# - cosine: Tính độ tương đồng cosine giữa hai vector embedding.

import math
import numpy as np
from typing import List, Optional
from sentence_transformers import util

def minmax_scale(values: List[float]) -> List[float]:
    """
    Chuẩn hóa danh sách giá trị về khoảng [0, 1].
    Nếu tất cả giá trị giống nhau, trả về 0.5 cho mỗi phần tử.
    """
    if not values:
        return values
    vmin, vmax = min(values), max(values)
    if math.isclose(vmax - vmin, 0.0):
        return [0.5 for _ in values]
    return [(v - vmin) / (vmax - vmin) for v in values]

def safe_float(x, default=None) -> Optional[float]:
    """
    Chuyển đổi giá trị sang float an toàn, trả về default nếu lỗi hoặc dữ liệu không hợp lệ.
    """
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return default
        return float(x)
    except Exception:
        return default

def cosine(a, b) -> float:
    """
    Tính độ tương đồng cosine giữa hai vector embedding.
    """
    return float(util.cos_sim(a, b).item())

