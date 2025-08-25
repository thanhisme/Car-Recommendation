from utils.vector_utils import minmax_scale
from .vehicle_scorer import VehicleScorer
from managers.strategy_config_manager import StrategyConfigManager

class VehicleReranker:
    @staticmethod
    def hybrid_rerank(hits, user_pref, pref_text, strategy, business_cfg, openai_manager):
        strategy_conf = StrategyConfigManager.get_strategy_config(strategy)
        wR, wP, wB = strategy_conf["wR"], strategy_conf["wP"], strategy_conf["wB"]
        gamma_rule = strategy_conf["gamma_rule"]
        pref_vec = openai_manager.get_embedding(pref_text)

        for h in hits:
            h.reasons = []
            h.rule_score = VehicleScorer.rule_score(h.payload, user_pref, h.reasons)
            h.emb_score = VehicleScorer.emb_score(h.payload, pref_vec, h.reasons, openai_manager)
            h.biz_score = VehicleScorer.business_score(h.payload, business_cfg, h.reasons)

        v_scaled = minmax_scale([h.vec_score for h in hits])
        r_scaled = minmax_scale([h.rule_score for h in hits])
        e_scaled = minmax_scale([h.emb_score for h in hits])
        b_scaled = minmax_scale([h.biz_score for h in hits])

        for i,h in enumerate(hits):
            p_part = gamma_rule*r_scaled[i] + (1-gamma_rule)*e_scaled[i]
            h.final_score = wR*v_scaled[i] + wP*p_part + wB*b_scaled[i]

        return sorted(hits, key=lambda x:x.final_score, reverse=True)
