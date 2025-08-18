import uuid
import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import openai
from business_signals import attach_business_signals
from utils.vector_utils import minmax_scale, safe_float
from configs.strategy_config import STRATEGIES
from models.car_hit import CarHit
from sentence_transformers import util

# Set up your OpenAI API key
openai.api_key = "key-placeholder"  # Replace with your actual OpenAI API key

class HybridCarRecommender:
    def __init__(self, csv_path: str):
        import pandas as pd
        self.df = attach_business_signals(pd.read_csv(csv_path))
        self.dim = 1536  # OpenAI's text-embedding-ada-002 has a 1536 dimensional output
        self.qdrant = QdrantClient(path="./qdrant_storage")
        self._init_collection()
        self._upsert()

    def _init_collection(self):
        self.qdrant.recreate_collection(
            collection_name="cars",
            vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE)
        )

    def _row_text(self, row):
        parts = [
            f"{row.get('Year','')} {row.get('Make','')} {row.get('Model','')} {row.get('Trim','')}",
            f"Type {row.get('BodyType','')}",
            f"Engine {row.get('EngineType','')} {row.get('HorsePower','')} HP",
            f"Driving {row.get('DrivingEnvironment','')}",
            f"UseCase {row.get('UseCase','')}",
            f"{row.get('Description','')}"
        ]
        return " | ".join([p for p in parts if p])

    def _get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI's API."""
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        # Extract the embedding from the response
        return response.data[0].embedding

    def _upsert(self):
        points = []
        for _, row in self.df.iterrows():
            text = self._row_text(row)
            vec = self._get_openai_embedding(text)  # Get OpenAI embedding
            payload = row.to_dict()
            points.append(PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload))
        self.qdrant.upsert(collection_name="cars", points=points)
        print(f"✅ Upserted {len(points)} cars into Qdrant (:path:)")

    def retrieve(self, user_query: str, top_k: int = 15,
                 filters: Optional[Dict[str, Any]] = None) -> List[CarHit]:
        qvec = self._get_openai_embedding(user_query)  # Get OpenAI embedding for the query
        qfilter = None
        if filters:
            must = []
            for k, v in filters.items():
                must.append(FieldCondition(key=k, match=MatchValue(value=v)))
            qfilter = Filter(must=must)
        results = self.qdrant.search(
            collection_name="cars",
            query_vector=qvec,
            limit=top_k,
            query_filter=qfilter
        )
        hits = [CarHit(id=str(r.id), vec_score=float(r.score), payload=r.payload) for r in results]
        return hits

    def rule_personal_score(self, car: Dict[str, Any], pref: Dict[str, Any], reasons: List[str]) -> float:
        score = 0.0
        eng = pref.get("EngineType")
        if eng and str(car.get("EngineType","")).lower() == str(eng).lower():
            score += 3.0
            reasons.append(f"EngineType match: {eng}")
        bt = pref.get("BodyType")
        if bt and str(car.get("BodyType","")).lower() == str(bt).lower():
            score += 2.0
            reasons.append(f"BodyType match: {bt}")
        price_cap = safe_float(pref.get("PriceMax"), None)
        price = safe_float(car.get("PriceUSD"), None)
        if price_cap is not None and price is not None and price <= price_cap:
            score += 2.0
            reasons.append(f"Price ≤ {price_cap}")
        pm = [x.lower() for x in pref.get("PreferredMakes", [])]
        if pm and str(car.get("Make","")).lower() in pm:
            score += 1.5
            reasons.append(f"Preferred make: {car.get('Make')}")
        pmdl = [x.lower() for x in pref.get("PreferredModels", [])]
        if pmdl and str(car.get("Model","")).lower() in pmdl:
            score += 1.0
            reasons.append(f"Preferred model: {car.get('Model')}")
        uc_kw = (pref.get("UseCaseKeyword") or "").lower()
        if uc_kw and uc_kw in str(car.get("Description","")).lower():
            score += 1.5
            reasons.append(f"UseCase contains '{uc_kw}'")
        env = (pref.get("DrivingEnvironment") or "").lower()
        if env and env in str(car.get("DrivingEnvironment","")).lower():
            score += 1.0
            reasons.append(f"Driving environment: {env}")
        return score

    def emb_personal_score(self, car: Dict[str, Any], pref_text_vec, reasons: List[str]) -> float:
        desc = car.get("Description", "") or ""
        meta = f"{car.get('EngineType','')} {car.get('BodyType','')} {car.get('UseCase','')}"
        txt = f"{desc} | {meta}".strip(" |")
        car_vec = self._get_openai_embedding(txt)  # Get OpenAI embedding for the car description
        sim = float(util.cos_sim(pref_text_vec, car_vec).item())
        return sim

    def business_score(self, car: Dict[str, Any], biz_cfg: Dict[str, Any], reasons: List[str]) -> float:
        brand_priority = safe_float(car.get("brand_priority"), 0.4)
        margin = safe_float(car.get("marginUSD"), 3000.0)
        inv_days = safe_float(car.get("inventory_days"), 20.0)
        margin_clip = (1500, 9000)
        inv_clip = (5, 90)
        m_scaled = (np.clip(margin, *margin_clip) - margin_clip[0]) / (margin_clip[1] - margin_clip[0] + 1e-9)
        i_scaled = (np.clip(inv_days, *inv_clip) - inv_clip[0]) / (inv_clip[1] - inv_clip[0] + 1e-9)
        score = 0.4 * brand_priority + 0.3 * m_scaled + 0.3 * i_scaled
        promoted_brands = [b.lower() for b in biz_cfg.get("promoted_brands", [])]
        promoted_models = [(m.lower()) for m in biz_cfg.get("promoted_models", [])]
        car_brand = str(car.get("Make","")).lower()
        car_model = str(car.get("Model","")).lower()
        if car_brand in promoted_brands:
            score += 0.15
            reasons.append(f"Promoted brand: {car.get('Make')}")
        if car_model in promoted_models:
            score += 0.2
            reasons.append(f"Promoted model: {car.get('Model')}")
        return float(score)

    def hybrid_rerank(self,
        hits: List[CarHit],
        user_pref: Dict[str, Any],
        pref_text: str,
        strategy: str = "default",
        business_cfg: Dict[str, Any] = None
    ) -> List[CarHit]:
        cfg = STRATEGIES.get(strategy, STRATEGIES["default"])
        wR, wP, wB = cfg["wR"], cfg["wP"], cfg["wB"]
        gamma_rule = cfg["gamma_rule"]
        business_cfg = business_cfg or {}
        pref_vec = self._get_openai_embedding(pref_text)  # Get OpenAI embedding for preferences
        for h in hits:
            h.reasons = []
            h.rule_score = self.rule_personal_score(h.payload, user_pref, h.reasons)
            h.emb_score = self.emb_personal_score(h.payload, pref_vec, h.reasons)
            h.biz_score = self.business_score(h.payload, business_cfg, h.reasons)
        v_scaled = minmax_scale([h.vec_score for h in hits])
        r_scaled = minmax_scale([h.rule_score for h in hits])
        e_scaled = minmax_scale([h.emb_score for h in hits])
        b_scaled = minmax_scale([h.biz_score for h in hits])
        for i, h in enumerate(hits):
            p_part = gamma_rule * r_scaled[i] + (1 - gamma_rule) * e_scaled[i]
            h.final_score = wR * v_scaled[i] + wP * p_part + wB * b_scaled[i]
        ranked = sorted(hits, key=lambda x: x.final_score, reverse=True)
        return ranked

    def explain_hit(self, h: CarHit) -> str:
        p = h.payload
        parts = [
            f"{p.get('Year')} {p.get('Make')} {p.get('Model')} {p.get('Trim')}",
            f"vec={h.vec_score:.3f}",
            f"rule={h.rule_score:.2f}",
            f"emb={h.emb_score:.3f}",
            f"biz={h.biz_score:.3f}",
            f"final={h.final_score:.3f}"
        ]
        reason_str = "; ".join(h.reasons[:4])
        return f"- {' | '.join(parts)}\n  Reasons: {reason_str}"
