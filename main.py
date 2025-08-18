from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from offers_db import OFFERS_DB
import json
from models import Profile, Finance
from tco_calculator import TCOCalculator

app = FastAPI()


# -----------------------------
# Mock helper functions
# -----------------------------
def semantic_search_from_profile(profile: Profile) -> Dict[str, Any]:
    """
    Semantic search trong vector DB từ payload -> gợi ý danh sách xe
    """
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


def get_finance_offers(profile: Profile) -> Dict[str, Any]:
    """
    Return khả năng tài chính + các ưu đãi/voucher dựa vào customer_segment
    """
    offers = OFFERS_DB.get(profile.customer_segment, OFFERS_DB["default"])

    return {
        "payment_capacity": {
            "cash_budget": profile.finance.cash_budget,
            "monthly_capacity": profile.finance.monthly_capacity,
        },
        "offers": offers,
    }


def filter_and_calculate_tco(profile, semantic_result, finance_result):
    import json
    with open("car_data.json", "r") as f:
        car_db = json.load(f)

    cars_with_tco = []
    for pref in semantic_result["suggested_cars"]:
        matches = [
            car for car in car_db
            if car["year"] == pref["year"]
            and car["make"] == pref["make"]
            and car["model"] == pref["model"]
            and car["trim"] == pref["trim"]
        ]

        for car in matches:
            # Voucher check
            applicable_voucher = None
            for offer in finance_result.get("special_offers", []):
                if (not offer.get("applicable_makes") or car["make"] in offer["applicable_makes"]) \
                   and (not offer.get("applicable_years") or car["year"] in offer["applicable_years"]):
                    applicable_voucher = offer
                    break

            voucher_discount = applicable_voucher["value"] if applicable_voucher else 0

            # Price filter (±2300$ + voucher)
            if not (profile.finance.cash_budget - 2300 <= (car["base_price"] - voucher_discount) <= profile.finance.cash_budget + 2300):
                continue

            # TCO calc
            calc = TCOCalculator(profile)
            tco_info = calc.calculate_tco(vehicle=car, voucher=applicable_voucher)

            cars_with_tco.append({
                "year": car["year"],
                "make": car["make"],
                "model": car["model"],
                "trim": car["trim"],

                # Initial cost chi tiết
                "estimated_initial_cost": f"${tco_info['breakdown']['initial_cost']['value']}",

                # TCO 5 năm (cả tổng + breakdown)
                "TCO_5_years": {
                    "total": tco_info["tco_total"],
                    "breakdown": tco_info["breakdown"]
                },

                # Reason
                "reason": f"{pref['reason']} + phù hợp với khả năng tài chính"
                          f" (voucher áp dụng: {voucher_discount}$)"
            })

    return cars_with_tco


# -----------------------------
# Endpoint
# -----------------------------
@app.post("/recommend")
def recommend_cars(profile: Profile):
    # Step 1: semantic search
    semantic_result = semantic_search_from_profile(profile)

    # Step 2: finance offers
    finance_result = get_finance_offers(profile)

    # Step 3: filter + TCO calc
    car_recommendations = filter_and_calculate_tco(profile, semantic_result, finance_result)

    # Build user-friendly response
    return {
        "summary": "We found cars that match your preferences, budget, and lifestyle.",
        "your_profile": {
            "location": f"{profile.state}, {profile.zip}",
            "budget": {
                "cash_budget": profile.finance.cash_budget,
                "monthly_capacity": profile.finance.monthly_capacity,
                "payment_method": profile.finance.payment_method
            },
            "eco_friendly": profile.eco_friendly,
            "preferences_from_semantic_search": semantic_result["suggested_cars"]
        },
        "finance_info": {
            "payment_capacity": f"You can afford cars up to ${profile.finance.cash_budget} in cash "
                                f"or around ${profile.finance.monthly_capacity}/month if financed.",
            "special_offers": finance_result.get("offers", [])
        },
        "recommended_cars": [
            {
                "year": car["year"],
                "make": car["make"],
                "model": car["model"],
                "trim": car["trim"],
                "estimated_initial_cost": f"${car['estimated_initial_cost']}",
                "estimated_TCO_5_years": f"${car['TCO_5_years']:,}",
                "why_this_car": car["reason"]
            }
            for car in car_recommendations
        ],
        "next_step": "You can compare detailed specifications or request dealership offers."
    }
