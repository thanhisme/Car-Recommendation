import pandas as pd
import numpy as np

def attach_business_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gắn thêm tín hiệu kinh doanh nếu thiếu:
      - marginUSD: lợi nhuận/xe (mock theo phân khúc/brand)
      - inventory_days: số ngày tồn kho
      - brand_priority: mức ưu tiên nhãn hàng (0..1)
    Bạn có thể thay bằng dữ liệu thật nếu có.
    """
    df = df.copy()

    if "marginUSD" not in df.columns:
        base = {
            "Toyota": 3800, "Honda": 3600, "Tesla": 5500, "Ford": 4200,
            "Chevrolet": 3200, "Jeep": 4000, "BMW": 7000, "Subaru": 3500,
            "Hyundai": 3000, "Kia": 2900
        }
        df["marginUSD"] = df["Make"].map(base).fillna(3000) + np.random.randint(-500, 500, size=len(df))

    if "inventory_days" not in df.columns:
        # Giả lập: xe phổ thông tồn kho lâu hơn xe hot
        df["inventory_days"] = np.clip(np.random.normal(loc=28, scale=10, size=len(df)).astype(int), 3, 90)

    if "brand_priority" not in df.columns:
        brand_boost = {
            "Toyota": 0.7, "Honda": 0.6, "Tesla": 0.5, "Ford": 0.55,
            "Chevrolet": 0.5, "Jeep": 0.55, "BMW": 0.4, "Subaru": 0.5,
            "Hyundai": 0.45, "Kia": 0.45
        }
        df["brand_priority"] = df["Make"].map(brand_boost).fillna(0.4)

    return df
