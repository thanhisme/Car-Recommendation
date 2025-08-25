import pandas as pd
import numpy as np
from configs.commercial_features_config import MARGIN_USD, BRAND_PRIORITY, DEFAULT_MARGIN, DEFAULT_PRIORITY

def attach_commercial_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gắn thêm đặc tính thương mại (commercial features) nếu thiếu:
      - marginUSD: lợi nhuận/xe (theo phân khúc/brand từ config)
      - inventory_days: số ngày tồn kho
      - brand_priority: mức ưu tiên nhãn hàng (0..1 từ config)
    """
    df = df.copy()

    if "marginUSD" not in df.columns:
        df["marginUSD"] = df["Make"].map(MARGIN_USD).fillna(DEFAULT_MARGIN) + np.random.randint(-500, 500, size=len(df))

    if "inventory_days" not in df.columns:
        df["inventory_days"] = np.clip(np.random.normal(loc=28, scale=10, size=len(df)).astype(int), 3, 90)

    if "brand_priority" not in df.columns:
        df["brand_priority"] = df["Make"].map(BRAND_PRIORITY).fillna(DEFAULT_PRIORITY)

    return df