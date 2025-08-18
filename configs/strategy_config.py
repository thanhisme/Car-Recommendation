from typing import Dict, Any
from utils.vector_utils import safe_float

STRATEGIES = {
    "default":   {"wR": 0.5, "wP": 0.3, "wB": 0.2, "gamma_rule": 0.5},
    "sales_boost": {"wR": 0.3, "wP": 0.2, "wB": 0.5, "gamma_rule": 0.4},
    "loyalty":   {"wR": 0.4, "wP": 0.5, "wB": 0.1, "gamma_rule": 0.6},
    "new_launch": {"wR": 0.2, "wP": 0.3, "wB": 0.5, "gamma_rule": 0.4},
}

def auto_pick_strategy(context: Dict[str, Any]) -> str:
    campaign = (context.get("campaign") or "").lower()
    user_tier = (context.get("user_tier") or "regular").lower()
    avg_inv   = safe_float(context.get("avg_inventory_days"), 25.0)

    if "new_launch" in campaign:
        return "new_launch"
    if "sale" in campaign or "clearance" in campaign or "boost" in campaign:
        return "sales_boost"
    if user_tier in ("vip", "loyal"):
        return "loyalty"
    if avg_inv is not None and avg_inv > 35:
        return "sales_boost"
    return "default"
