from recommender import HybridCarRecommender
from configs.strategy_config import auto_pick_strategy
import numpy as np

CSV_PATH = "data/vehicle_raw_vector_db.csv"
TOP_K = 15

if __name__ == "__main__":
    # 1) Khởi tạo
    rec = HybridCarRecommender(CSV_PATH)

    # 2) Truy vấn ban đầu (Vector Top-K) 
    user_query = "fuel efficient compact car for daily urban commute, safe and reliable"
    hits = rec.retrieve(user_query, top_k=TOP_K)

    print("\n=== Top-K by Vector Similarity ===")
    for h in hits[:5]:
        p = h.payload
        print(f"- {p.get('Year')} {p.get('Make')} {p.get('Model')} {p.get('Trim')} | vec_score={h.vec_score:.4f}")

    # 3) Ngữ cảnh & chiến lược động
    context = {
        "campaign": "clearance sale",     # "new_launch" / "clearance sale" / ""
        "user_tier": "regular",           # "vip" / "loyal" / "regular" / "new"
        "avg_inventory_days": float(np.mean(rec.df["inventory_days"]))
    }
    strategy = auto_pick_strategy(context)
    print(f"\n>>> Auto-picked strategy: {strategy}")

    # 4) Preference & Business config
    user_pref = {
        "EngineType": "Hybrid",
        "BodyType": "SUV",
        "PriceMax": 33000,
        "PreferredMakes": ["Toyota", "Honda"],
        "UseCaseKeyword": "family",
        "DrivingEnvironment": "Urban",
        # "Zip": "90046",
    }
    pref_text = "Hybrid SUV under $33,000 for family trips in urban areas, reliable and efficient"

    business_cfg = {
        # đẩy brand hoặc model cụ thể
        "promoted_brands": ["Toyota"],
        "promoted_models": ["rav4", "model 3"],  # lowercase so khớp đơn giản
    }

    # 5) Hybrid re-ranking
    ranked = rec.hybrid_rerank(
        hits=hits,
        user_pref=user_pref,
        pref_text=pref_text,
        strategy=strategy,
        business_cfg=business_cfg
    )

    # 6) In kết quả & lý do
    print("\n=== Re-ranked (Hybrid) ===")
    for h in ranked[:10]:
        print(rec.explain_hit(h))
