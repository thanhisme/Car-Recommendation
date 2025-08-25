from models.profile import Profile
from models.car_hit import CarHit
from .vehicle_query_builder import VehicleQueryBuilder
from managers.strategy_config_manager import StrategyConfigManager
from .vehicle_reranker import VehicleReranker
import json
import re

class VehicleSearcher:
    def __init__(self, openai_manager, qdrant_manager):
        self.openai_manager = openai_manager
        self.qdrant_manager = qdrant_manager

    def search(self, profile: Profile, strategy_name: str, business_cfg_override: dict = None, top_k: int = 10):
        query_text, qfilter = VehicleQueryBuilder.build(profile)
        business_cfg = StrategyConfigManager.get_business_config(strategy_name, business_cfg_override)

        query_emb = self.openai_manager.get_embedding(query_text)
        hits_raw = self.qdrant_manager.search(query_vector=query_emb, top_k=top_k, query_filter=qfilter)
        
        # Convert hits to vehicles list
        vehicles = [
            {
                "id": h.id,
                "year": h.payload.get("year"),
                "make": h.payload.get("make"),
                "model": h.payload.get("model"),
                "trim": h.payload.get("trim"),
                "color": h.payload.get("color"),
                "zip": h.payload.get("zip"),
                "price": h.payload.get("price"),
                "reason": f"Vector similarity score: {h.score:.3f}"
            } for h in hits_raw
        ]
        
        # Use LLM rerank
        reranked_vehicles = self._llm_rerank(vehicles, profile, strategy_name, business_cfg)
        
        # Convert back to original format
        return [
            {
                "year": v.get("year"),
                "make": v.get("make"),
                "model": v.get("model"),
                "trim": v.get("trim"),
                "color": v.get("color"),
                "zip": v.get("zip"),
                "reason": v.get("reason", "No reason provided")
            } for v in reranked_vehicles
        ]
    
    def _llm_rerank(self, vehicles: list, profile: Profile, strategy_name: str, strategy_conf: dict):
        """
        Rerank vehicles using LLM based on user profile and business strategy.
        """
        
        # Convert vehicles to context string
        context = "\n".join([
            f"- {v['year']} {v['make']} {v['model']} {v['trim']} ({v['color']}) - ${v.get('price', 'N/A')} - {v.get('reason', 'No reason provided')}"
            for v in vehicles
        ])
        
        response = self.openai_manager.chat_completion(
            messages=[
                {"role": "system", "content": "Bạn là trợ lý gợi ý xe."},
                {"role": "user", "content": f"""
                Người dùng có profile: {str(profile)}

                Chiến lược doanh nghiệp đang dùng: {strategy_name}
                Cấu hình strategy: {strategy_conf}

                Danh sách xe tìm thấy (đã qua filter): 
                {context}

                Hãy chọn ra xe phù hợp nhất với profile này, 
                có cân nhắc strategy (trọng số wR, wP, wB, gamma_rule).

                Trả về JSON dạng:
                [
                {{"id": ..., "name": "...", "reason": "..."}}
                ]
                không giải thích gì thêm.
                """}
            ],
            model="gpt-4o-mini"
        )

        try:
            raw_output = response.choices[0].message.content.strip()
            print("🔍 Raw LLM output:", raw_output)
            if raw_output.startswith("```"):
                raw_output = re.sub(r"^```[a-zA-Z]*\n?", "", raw_output)
                raw_output = re.sub(r"\n?```$", "", raw_output)
            
            llm_results = json.loads(raw_output)
            # Map LLM results back to original vehicles
            reranked_vehicles = []
            for llm_result in llm_results:
                vehicle_id = llm_result.get("id")
                # Find original vehicle by ID
                for vehicle in vehicles:
                    if vehicle["id"] == vehicle_id:
                        vehicle["reason"] = llm_result.get("reason", vehicle.get("reason", "No reason provided"))
                        reranked_vehicles.append(vehicle)
                        break
            return reranked_vehicles
        except Exception as e:
            print("⚠️ Parse JSON fail:", raw_output if 'raw_output' in locals() else "No output")
            print("⚠️ Error:", str(e))
            return vehicles  # Return original order if LLM fails
    

