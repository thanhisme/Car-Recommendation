from typing import Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class CarHit:
    id: int
    payload: Dict[str, Any]
    vec_score: float
    rule_score: float = 0.0
    emb_score: float = 0.0
    biz_score: float = 0.0
    final_score: float = 0.0
    reasons: List[str] = field(default_factory=list)

    def __str__(self):
        name = self.payload.get("name", "Unknown")
        price = self.payload.get("price", "N/A")
        brand = self.payload.get("brand", "N/A")
        body_type = self.payload.get("body_type", "N/A")
        return (
            f"CarHit(id={self.id}, name={name}, brand={brand}, body_type={body_type}, price={price} USD)\n"
            f"Scores -> vec: {self.vec_score:.3f}, rule: {self.rule_score:.3f}, "
            f"emb: {self.emb_score:.3f}, biz: {self.biz_score:.3f}, final: {self.final_score:.3f}\n"
            f"Reasons: {', '.join(self.reasons) if self.reasons else 'None'}"
        )
