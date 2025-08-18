# tco_calculator.py
import math
from typing import Dict, Any, Optional
from region_config import REGION_CONFIG


class TCOCalculator:
    def __init__(self, profile: Dict[str, Any]):
        state = profile.state
        if state not in REGION_CONFIG:
            raise ValueError(f"No config found for state {state}")
        self.config = REGION_CONFIG[state]
        self.profile = profile
        self.annual_miles = profile.annual_mileage or 12000

    def _apply_voucher(self, vehicle: Dict, voucher: Optional[Dict], year: int) -> float:
        """Check voucher applicability, return discount value"""
        if not voucher:
            return 0.0
        if voucher.get("applicable_makes") and vehicle["make"] not in voucher["applicable_makes"]:
            return 0.0
        if voucher.get("applicable_models") and vehicle["model"] not in voucher["applicable_models"]:
            return 0.0
        if voucher.get("applicable_years") and year not in voucher["applicable_years"]:
            return 0.0
        if voucher.get("excluded_trims") and vehicle["trim"] in voucher["excluded_trims"]:
            return 0.0
        return voucher.get("value", 0.0)

    def calculate_tco(self, vehicle: Dict[str, Any], voucher: Optional[Dict], years: int = 5) -> Dict[str, Any]:
        breakdown = {}
        base_price = vehicle["base_price"]

        # 1. Initial cost (price + tax + reg - voucher)
        applied_voucher = self._apply_voucher(vehicle, voucher, vehicle["year"])
        tax = base_price * self.config["tax_rate"]
        reg_fee = self.config["registration_fee"]
        initial_cost = base_price + tax + reg_fee - applied_voucher
        breakdown["initial_cost"] = {
            "value": initial_cost,
            "explanation": {
                "base_price": base_price,
                "tax": tax,
                "registration_fee": reg_fee,
                "applied_voucher": -applied_voucher,
            }
        }

        # 2. Fuel / EV energy
        if vehicle["fuel_type"] == "EV":
            annual_cost = self.annual_miles * vehicle["kwh_per_mile"] * self.config["electricity_price"]
            breakdown["energy_cost"] = {
                "value": annual_cost * years,
                "explanation": {
                    "annual_mileage": self.annual_miles,
                    "kwh_per_mile": vehicle["kwh_per_mile"],
                    "electricity_price": self.config["electricity_price"],
                    "years": years
                }
            }
        else:
            annual_cost = (self.annual_miles / vehicle["mpg"]) * self.config["fuel_price"]
            breakdown["fuel_cost"] = {
                "value": annual_cost * years,
                "explanation": {
                    "annual_mileage": self.annual_miles,
                    "mpg": vehicle["mpg"],
                    "fuel_price": self.config["fuel_price"],
                    "years": years
                }
            }

        # 3. Insurance
        insurance = base_price * self.config["insurance_base"] * years
        breakdown["insurance"] = {
            "value": insurance,
            "explanation": {
                "price": base_price,
                "insurance_rate": self.config["insurance_base"],
                "years": years
            }
        }

        # 4. Maintenance
        base_maint = 400 if vehicle["make"] == "Toyota" else 800
        escalation = 1.1 if vehicle["make"] == "Toyota" else 1.2
        maint_cost = sum(base_maint * (escalation ** (y - 1)) for y in range(1, years + 1))
        breakdown["maintenance"] = {
            "value": maint_cost,
            "explanation": {"base": base_maint, "escalation": escalation, "years": years}
        }

        # 5. Parking
        parking = self.config.get("parking_fee", 0) * years
        breakdown["parking"] = {
            "value": parking,
            "explanation": {"annual_fee": self.config.get("parking_fee", 0), "years": years}
        }

        # 6. Toll
        toll = self.config.get("toll_fee", 0) * years
        breakdown["toll"] = {
            "value": toll,
            "explanation": {"annual_toll": self.config.get("toll_fee", 0), "years": years}
        }

        total = sum(item["value"] for item in breakdown.values())
        return {"tco_total": total, "breakdown": breakdown}
