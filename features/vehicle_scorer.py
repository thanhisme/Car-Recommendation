from typing import Dict, Any, List
from sentence_transformers import util
from utils.vector_utils import safe_float


class VehicleScorer:
    @staticmethod
    def rule_score(car: Dict[str, Any], pref: Dict[str, Any], reasons: List[str]) -> float:
        score = 0.0
        eng = pref.get("engine_type")
        if eng and str(car.get("engine_type","")).lower() == str(eng).lower():
            score += 3.0; reasons.append(f"EngineType match: {eng}")
        bt = pref.get("body_type")
        if bt and str(car.get("body_type","")).lower() in [x.lower() for x in (bt if isinstance(bt,list) else [bt])]:
            score += 2.0; reasons.append(f"BodyType match: {bt}")
        price_cap = safe_float(pref.get("PriceMax"), None)
        price = safe_float(car.get("price"), None)
        if price_cap is not None and price is not None and price <= price_cap:
            score += 2.0; reasons.append(f"Price ≤ {price_cap}")
        pm = [x.lower() for x in pref.get("brand_preference",[])]
        if pm and str(car.get("brand","")).lower() in pm:
            score += 1.5; reasons.append(f"Preferred make: {car.get('brand')}")
        return score

    @staticmethod
    def emb_score(car: Dict[str, Any], pref_text_vec, reasons: List[str], openai_manager) -> float:
        desc = car.get("desc","")
        meta = f"{car.get('engine_type','')} {car.get('body_type','')}".strip()
        txt = f"{desc} | {meta}".strip(" |")
        car_vec = openai_manager.get_embedding(txt)
        return float(util.cos_sim(pref_text_vec, car_vec).item())

    @staticmethod
    def business_score(car: Dict[str, Any], biz_cfg: Dict[str, Any], reasons: List[str]) -> float:
        score = 0.0
        if car.get("brand","").lower() in [b.lower() for b in biz_cfg.get("promoted_brands", [])]:
            score += 0.2; reasons.append(f"Promoted brand: {car.get('brand')}")
        if car.get("name","") in biz_cfg.get("high_margin_models", []):
            score += 0.2; reasons.append(f"High margin model: {car.get('name')}")
        multiplier = safe_float(biz_cfg.get("campaign_multiplier", 1.0),1.0)
        return score * multiplier
