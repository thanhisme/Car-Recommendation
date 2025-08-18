from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from models.profile import Profile
from models.finance import Finance
from tco_calculator import TCOCalculator

app = FastAPI()


# -----------------------------
# Mock helper functions
# -----------------------------
def semantic_search_from_profile(profile: Profile, useMock: bool = False) -> Dict[str, Any]:
    """
    Semantic search trong vector DB từ payload -> gợi ý danh sách xe (dùng HybridCarRecommender)
    """
    if (useMock):
        return {
            "suggested_cars": [
                {
                    "year": 2022,
                    "make": "Honda",
                    "model": "Civic",
                    "trim": "EX Sedan",
                    "reason": "Phù hợp với ngân sách, tiết kiệm nhiên liệu và kiểu dáng sedan"
                },
                {
                    "year": 2023,
                    "make": "Tesla",
                    "model": "Model 3",
                    "trim": "Long Range AWD",
                    "reason": "Xe điện, có Autopilot, thân thiện môi trường, phù hợp với nhu cầu EV"
                },
                {
                    "year": 2021,
                    "make": "Honda",
                    "model": "Accord",
                    "trim": "Sport Special Edition",
                    "reason": "Không gian rộng rãi cho gia đình, nhiều tính năng an toàn"
                }
            ]
        }
    from recommender import HybridCarRecommender
    from configs.strategy_config import auto_pick_strategy
    import numpy as np
    CSV_PATH = "data/vehicle_raw_vector_db.csv"
    TOP_K = 15
    rec = HybridCarRecommender(CSV_PATH)

    # Build user_pref from profile
    user_pref = {
        "EngineType": getattr(profile, "engine_type", None),
        "BodyType": profile.body_type[0] if profile.body_type else None,
        "PriceMax": profile.finance.cash_budget if profile.finance else None,
        "PreferredMakes": profile.brand_preference,
        "PreferredModels": [],
        "UseCaseKeyword": getattr(profile, "habit", None),
        "DrivingEnvironment": getattr(profile, "parking", None),
    }
    pref_text = f"{user_pref['EngineType']} {user_pref['BodyType']} under ${user_pref['PriceMax']} for {user_pref['UseCaseKeyword']} in {user_pref['DrivingEnvironment']}"

    # Context for strategy
    context = {
        "campaign": getattr(profile, "campaign", ""),
        "user_tier": getattr(profile, "memberLevel", "regular"),
        "avg_inventory_days": float(np.mean(rec.df["inventory_days"]))
    }
    strategy = auto_pick_strategy(context)

    business_cfg = {
        "promoted_brands": [b for b in profile.brand_preference],
        "promoted_models": [],
    }

    hits = rec.retrieve(pref_text, top_k=TOP_K)
    ranked = rec.hybrid_rerank(
        hits=hits,
        user_pref=user_pref,
        pref_text=pref_text,
        strategy=strategy,
        business_cfg=business_cfg
    )

    # Build response schema
    suggested_cars = []
    for h in ranked[:5]:
        p = h.payload
        suggested_cars.append({
            "year": p.get("Year"),
            "make": p.get("Make"),
            "model": p.get("Model"),
            "trim": p.get("Trim"),
            "reason": "; ".join(h.reasons[:3])
        })
    return {"suggested_cars": suggested_cars}


def get_finance_offers(profile: Profile) -> Dict[str, Any]:
    """
    Return khả năng tài chính + các ưu đãi/voucher dựa vào customer_segment
    """

    return {
        "payment_capacity": {
            "cash_budget": profile.finance.cash_budget,
            "monthly_capacity": profile.finance.monthly_capacity,
        }
    }


def filter_and_calculate_tco(profile, semantic_result, finance_result):
    from utils.db import get_vehicles_from_db
    from utils.voucher_utils import get_discount_vouchers

    vehicles = get_vehicles_from_db()

    cars_with_tco = []
    
    for pref in semantic_result["suggested_cars"]:
        matches = [
            v for v in vehicles
            if v.year == pref["year"]
            and v.make == pref["make"]
            and v.model == pref["model"]
            and v.trim == pref["trim"]
        ]
        for vehicle in matches:
            # Voucher check
            discount_vouchers = get_discount_vouchers(
                finance_result.get("special_offers", []), vehicle, vehicle.year, getattr(profile, "memberLevel", None)
            )
            discount_voucher = discount_vouchers[0] if discount_vouchers else None
            voucher_discount = discount_voucher.value if discount_voucher else 0

            # Price filter (±2300$ + voucher)
            if not (profile.finance.cash_budget - 2300 <= (vehicle.base_price - voucher_discount) <= profile.finance.cash_budget + 2300):
                continue

            # TCO calc
            calc = TCOCalculator(profile)
            tco_info = calc.calculate_tco(vehicle=vehicle, voucher=discount_voucher)

            car_info = {
                "year": vehicle.year,
                "make": vehicle.make,
                "model": vehicle.model,
                "trim": vehicle.trim,
                "color": getattr(vehicle, "color", None),
                "reason": f"{pref['reason']} + phù hợp với khả năng tài chính (voucher áp dụng: {voucher_discount}$)"
            }
            # Merge all tco_info fields
            car_info.update(tco_info)
            cars_with_tco.append(car_info)
    return cars_with_tco


# -----------------------------
# Endpoint
# -----------------------------
@app.post("/recommend")
def recommend_cars(profile: Profile):
    semantic_result = semantic_search_from_profile(profile, useMock=True)
    finance_result = get_finance_offers(profile)
    car_recommendations = filter_and_calculate_tco(profile, semantic_result, finance_result)
    return {
        "summary": "We found cars that match your preferences, budget, and lifestyle.",
        "your_profile": {
            "location": f"{profile.state}, {getattr(profile, 'zip', '')}",
            "budget": {
                "cash_budget": profile.finance.cash_budget,
                "monthly_capacity": profile.finance.monthly_capacity,
                "payment_method": profile.finance.payment_method
            },
            "eco_friendly": getattr(profile, 'eco_friendly', None),
            "preferences_from_semantic_search": semantic_result["suggested_cars"]
        },
        "finance_info": {
            "payment_capacity": f"You can afford cars up to ${profile.finance.cash_budget} in cash "
                                f"or around ${profile.finance.monthly_capacity}/month if financed.",
        },
        "recommended_cars": [car for car in car_recommendations],
        # "next_step": "You can compare detailed specifications or request dealership offers."
    }
