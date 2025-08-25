from configs.strategy_config import STRATEGIES

BUSINESS_CONFIGS = {
    "default": {"campaign": "default", "promoted_brands": [], "high_margin_models": [], "inventory_days": 20,
                "seasonal_discount": 1.0, "priority_region": [], "campaign_multiplier": 1.0},
    "sales_boost": {"campaign": "sales_boost", "promoted_brands": ["Honda", "Toyota"], "high_margin_models": [],
                    "inventory_days": 15, "seasonal_discount": 0.9, "priority_region": ["CA", "NY"],
                    "campaign_multiplier": 1.0},
    "new_launch": {"campaign": "new_launch", "promoted_brands": ["Toyota"], "high_margin_models": ["Corolla Hybrid 2022"],
                   "inventory_days": 10, "seasonal_discount": 1.0, "priority_region": ["CA", "TX"],
                   "campaign_multiplier": 1.2},
    "loyalty": {"campaign": "loyalty", "promoted_brands": ["Toyota", "Honda"], "high_margin_models": [],
                "inventory_days": 25, "seasonal_discount": 0.95, "priority_region": [], "campaign_multiplier": 0.9}
}

class StrategyConfigManager:
    @staticmethod
    def get_strategy_config(strategy_name: str) -> dict:
        return STRATEGIES.get(strategy_name, STRATEGIES["default"])

    @staticmethod
    def get_business_config(strategy_name: str, override_cfg: dict = None) -> dict:
        default_cfg = BUSINESS_CONFIGS.get(strategy_name.lower(), BUSINESS_CONFIGS["default"])
        merged_cfg = default_cfg.copy()
        if override_cfg:
            merged_cfg.update(override_cfg)
        return merged_cfg
