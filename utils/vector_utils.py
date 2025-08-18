import math
import numpy as np
from typing import List, Optional
from sentence_transformers import util

def minmax_scale(values: List[float]) -> List[float]:
    if not values:
        return values
    vmin, vmax = min(values), max(values)
    if math.isclose(vmax - vmin, 0.0):
        return [0.5 for _ in values]
    return [(v - vmin) / (vmax - vmin) for v in values]

def safe_float(x, default=None) -> Optional[float]:
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return default
        return float(x)
    except Exception:
        return default

def cosine(a, b) -> float:
    return float(util.cos_sim(a, b).item())

