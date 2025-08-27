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
        print("🔍 Query text:", query_text)
        print("🔍 Query filter:", qfilter)
        business_cfg = StrategyConfigManager.get_business_config(strategy_name, business_cfg_override)

        query_emb = self.openai_manager.get_embedding(query_text)
        hits_raw = self.qdrant_manager.search(query_vector=query_emb, top_k=top_k, query_filter=qfilter)
        
        # Use LLM rerank with full raw hits
        reranked_vehicles = self._llm_rerank(hits_raw, profile, strategy_name, business_cfg)
        
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
    
    def _llm_rerank(self, hits_raw: list, profile: Profile, strategy_name: str, strategy_conf: dict):
        """
        Rerank vehicles using LLM based on user profile and business strategy.
        """
        
        # Convert full hits to JSON context (id, score, full payload)
        full_hits_context = [
            {
                "id": getattr(h, "id", None),
                "score": getattr(h, "score", None),
                "payload": getattr(h, "payload", None)
            }
            for h in hits_raw
        ]
        context = json.dumps(full_hits_context, ensure_ascii=False)
        print("\n\n\n🔍 Rerank context:", context)
        
        response = self.openai_manager.chat_completion(
            messages=[
                {"role": "system", "content": "Bạn là trợ lý gợi ý xe."},
                {"role": "user", "content": f"""
                Người dùng có profile: {str(profile)}

                Chiến lược doanh nghiệp đang dùng: {strategy_name}
                Cấu hình strategy: {strategy_conf}

                Danh sách xe tìm thấy (đầy đủ payload, đã qua filter): 
                {context}

                Hãy chọn ra nhiều xe! phù hợp nhất với profile (nên chú ý thêm vào profile của người dùng) này, 
                có cân nhắc strategy (trọng số wR, wP, wB, gamma_rule).

                Trả về JSON dạng:
                [
                {{"year": "...", "make": "...", "model": "...", "trim": "...", "color": "...", "zip": "...", "score": "...","reason": "..."}}
                ]
                không giải thích gì thêm.
                """}
            ],
            model="gpt-4o-mini"
        )

        try:
            raw_output = response.choices[0].message.content.strip()
            if raw_output.startswith("```"):
                raw_output = re.sub(r"^```[a-zA-Z]*\n?", "", raw_output)
                raw_output = re.sub(r"\n?```$", "", raw_output)
            
            llm_results = json.loads(raw_output)
            print("\n\n\n✅ LLM Rerank results:", llm_results)
            return llm_results
        except Exception as e:
            print("⚠️ Parse JSON fail:", raw_output if 'raw_output' in locals() else "No output")
            print("⚠️ Error:", str(e))
            # Fallback: convert hits_raw to simplified vehicle list in original order
            fallback = [
                {
                    "year": (getattr(h, "payload", {}) or {}).get("year"),
                    "make": (getattr(h, "payload", {}) or {}).get("make"),
                    "model": (getattr(h, "payload", {}) or {}).get("model"),
                    "trim": (getattr(h, "payload", {}) or {}).get("trim"),
                    "color": (getattr(h, "payload", {}) or {}).get("color"),
                    "zip": (getattr(h, "payload", {}) or {}).get("zip"),
                    "reason": f"Vector similarity score: {getattr(h, 'score', 0) if isinstance(getattr(h, 'score', 0), (int, float)) else 0:.3f}"
                }
                for h in hits_raw
            ]
            return fallback  # Return original order if LLM fails
    

