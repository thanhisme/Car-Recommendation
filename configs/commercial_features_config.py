"""
Cấu hình các đặc tính thương mại (commercial features) cho từng hãng xe.

- MARGIN_USD: Lợi nhuận dự kiến trên mỗi xe (USD) theo từng hãng.
- BRAND_PRIORITY: Mức ưu tiên thương hiệu (0..1), dùng cho logic gợi ý xe.
- DEFAULT_MARGIN: Giá trị mặc định nếu hãng xe chưa có cấu hình.
- DEFAULT_PRIORITY: Giá trị mặc định nếu hãng xe chưa có cấu hình.
"""

MARGIN_USD = {
    "Toyota": 3800,
    "Honda": 3600,
    "Tesla": 5500,
    "Ford": 4200,
    "Chevrolet": 3200,
    "Jeep": 4000,
    "BMW": 7000,
    "Subaru": 3500,
    "Hyundai": 3000,
    "Kia": 2900
}

BRAND_PRIORITY = {
    "Toyota": 0.7,
    "Honda": 0.6,
    "Tesla": 0.5,
    "Ford": 0.55,
    "Chevrolet": 0.5,
    "Jeep": 0.55,
    "BMW": 0.4,
    "Subaru": 0.5,
    "Hyundai": 0.45,
    "Kia": 0.45
}

DEFAULT_MARGIN = 3000
DEFAULT_PRIORITY = 0.4