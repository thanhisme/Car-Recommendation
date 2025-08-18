from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class CarHit:
    id: str
    vec_score: float
    payload: Dict[str, Any]
    rule_score: float = 0.0
    emb_score: float = 0.0
    biz_score: float = 0.0
    final_score: float = 0.0
    reasons: List[str] = None