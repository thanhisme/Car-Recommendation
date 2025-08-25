from configs.strategy_config import STRATEGIES
from utils.vector_utils import safe_float

def auto_pick_strategy(context):
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
