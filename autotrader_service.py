from typing import Dict, Any
import json

from models.profile import Profile
from features.tco_calculator import TCOCalculator
from utils.db import get_vehicles_from_db, load_raw_vehicles
from features.vouchers import get_discount_vouchers
from managers.openai_client_manager import OpenAIClientManager
from managers.qdrant_client_manager import QdrantClientManager
from features.vehicle_searcher import VehicleSearcher
from qdrant_client.models import PointStruct

class AutoTraderService:
    def __init__(self, api_key: str = "YOUR_API_KEY"):
        """
        Initialize the AutoTraderService.
        
        Parameters:
            api_key (str): OpenAI API key for embeddings generation.
        """
        # Initialize OpenAI and Qdrant clients
        self.openai_manager = OpenAIClientManager(api_key="open-ai-key")
        self.qdrant_manager = QdrantClientManager()
        
        # Initialize sample vehicle data and upsert to Qdrant only if empty
        self._initialize_vehicle_data()
    
    def recommend_with_profile(self, profile: Profile):
        """
        Shared recommendation flow for a given profile:
        - semantic search → finance → budget/match filter → TCO → response dict
        """
        semantic_result = self.semantic_search_from_profile(profile, useMock=False)
        finance_result = self.get_finance_info(profile)
        filtered_vehicles = self.filter_vehicles_by_budget_and_match(profile, semantic_result, finance_result)
        vehicles_with_tco = self.calculate_tco_for_vehicles(profile, filtered_vehicles)

        return {
            "summary": "We found vehicles that match your preferences, budget, and lifestyle.",
            "your_profile": {
                "location": f"{profile.state}, {getattr(profile, 'zip', '')}",
                "budget": {
                    "cash_budget": profile.finance.cash_budget if profile.finance else None,
                    "monthly_capacity": profile.finance.monthly_capacity if profile.finance else None,
                    "payment_method": profile.finance.payment_method if profile.finance else None
                },
                "preferences_from_semantic_search": semantic_result["suggested_vehicles"]
            },
            "finance_info": {
                "payment_capacity": f"You can afford vehicles up to ${profile.finance.cash_budget} in cash "
                                     f"or around ${profile.finance.monthly_capacity}/month if financed."
                if profile.finance else None,
            },
            "recommended_vehicles": vehicles_with_tco,
        }

    def build_default_profile(self, state: str) -> Profile:
        from models.finance import Finance
        return Profile(
            state=state,
            finance=Finance(payment_method="cash", cash_budget=10**9, monthly_capacity=10**9)
        )

    def vehicle_details_with_tco(self, vin: str, profile: Profile):
        """
        Look up a vehicle by VIN (mapped to id in demo data) and compute TCO using the profile.
        """
        vehicles = get_vehicles_from_db()
        vehicle = next((v for v in vehicles if str(v.id) == str(vin)), None)
        if not vehicle:
            return {"error": "Vehicle not found"}

        finance_result = self.get_finance_info(profile)
        discount_vouchers = get_discount_vouchers(
            finance_result.get("special_offers", []),
            vehicle,
            vehicle.year,
            getattr(profile, "memberLevel", None)
        )
        discount_voucher = discount_vouchers[0] if discount_vouchers else None

        calc = TCOCalculator(profile)
        tco_info = calc.calculate_tco(vehicle=vehicle, voucher=discount_voucher)

        details = {
            "id": vehicle.id,
            "year": vehicle.year,
            "make": vehicle.make,
            "model": vehicle.model,
            "trim": vehicle.trim,
            "color": getattr(vehicle, "color", None),
            "state": getattr(vehicle, "state", None),
            "zip": getattr(vehicle, "zip", None),
            "engine_type": getattr(vehicle, "engine_type", None),
            "body_type": getattr(vehicle, "body_type", None),
            "price": getattr(vehicle, "price", None) or getattr(vehicle, "base_price", None),
            "base_price": getattr(vehicle, "base_price", None),
        }
        details.update(tco_info)
        return details
    def _initialize_vehicle_data(self):
        """
        Initialize sample vehicle data and upsert to Qdrant database.
        This is done once during service initialization.
        """
        # Skip if data already present
        try:
            if self.qdrant_manager.collection_has_data():
                print("🔍 Vehicle data already present in Qdrant")
                return
        except Exception:
            pass

        vehicles = load_raw_vehicles()
        
        # Insert vehicles into Qdrant with embeddings
        for vehicle in vehicles:
            emb = self.openai_manager.get_embedding(vehicle["desc"])
            self.qdrant_manager.upsert([PointStruct(id=vehicle["id"], vector=emb, payload=vehicle)])

    def semantic_search_from_profile(self, profile: Profile, useMock: bool = False) -> Dict[str, Any]:
        """
        Perform semantic search to suggest vehicles based on user profile.
        Uses mock data if `useMock` is True.
        """
        if useMock:
            # Load mock suggested vehicles
            with open("data/mock_suggested_vehicles.json", "r", encoding="utf-8") as f:
                return json.load(f)

        # Perform semantic search using pre-initialized clients
        searcher = VehicleSearcher(openai_manager=self.openai_manager, qdrant_manager=self.qdrant_manager)
        results = searcher.search(profile, strategy_name="new_launch")
        return {"suggested_vehicles": results}

    def get_finance_info(self, profile: Profile) -> Dict[str, Any]:
        """
        Return finance offers based on user's profile.
        """
        return {
            "payment_capacity": {
                "cash_budget": profile.finance.cash_budget,
                "monthly_capacity": profile.finance.monthly_capacity,
            }
        }
        
    def filter_vehicles_by_budget_and_match(self, profile: Profile, semantic_result: Dict[str, Any], finance_result: Dict[str, Any]):
        """
        Lọc các xe từ DB dựa trên kết quả semantic search và khả năng tài chính của người dùng.
        Trả về danh sách xe thỏa điều kiện.
        """
        vehicles = get_vehicles_from_db()
        filtered_vehicles = []

        for pref in semantic_result["suggested_vehicles"]:
            # Tìm xe khớp hoàn toàn theo year, make, model, trim
            matches = [
                v for v in vehicles
                if v.year == pref["year"]
                and v.make == pref["make"]
                and v.model == pref["model"]
                and v.trim == pref["trim"]
                and v.color == pref["color"]
                and v.zip == pref["zip"]
            ]

            for vehicle in matches:
                # Lấy voucher giảm giá áp dụng nếu có
                discount_vouchers = get_discount_vouchers(
                    finance_result.get("special_offers", []),
                    vehicle,
                    vehicle.year,
                    getattr(profile, "memberLevel", None)
                )
                discount_voucher = discount_vouchers[0] if discount_vouchers else None
                voucher_discount = discount_voucher.value if discount_voucher else 0

                # Kiểm tra xe có phù hợp với cash budget (+/- 500 USD) hay không
                if profile.finance.cash_budget - 500 <= (vehicle.base_price - voucher_discount) <= profile.finance.cash_budget + 500:
                    filtered_vehicles.append((vehicle, pref, discount_voucher))

        return filtered_vehicles

    def calculate_tco_for_vehicles(self, profile: Profile, filtered_vehicles: list):
        """
        Tính TCO cho danh sách xe đã lọc và trả về danh sách xe kèm thông tin TCO.
        """
        vehicles_with_tco = []

        for vehicle, pref, discount_voucher in filtered_vehicles:
            # Tính TCO
            calc = TCOCalculator(profile)
            tco_info = calc.calculate_tco(vehicle=vehicle, voucher=discount_voucher)

            # Chuẩn bị thông tin xe cuối cùng
            voucher_discount = discount_voucher.value if discount_voucher else 0
            vehicle_info = {
                "year": vehicle.year,
                "make": vehicle.make,
                "model": vehicle.model,
                "trim": vehicle.trim,
                "color": getattr(vehicle, "color", None),
                "reason": f"{pref['reason']} + phù hợp với khả năng tài chính (voucher áp dụng: {voucher_discount}$)"
            }
            vehicle_info.update(tco_info)
            vehicles_with_tco.append(vehicle_info)

        return vehicles_with_tco

