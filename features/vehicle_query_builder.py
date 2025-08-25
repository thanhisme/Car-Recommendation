from models.profile import Profile
from qdrant_client.models import FieldCondition, MatchValue, Filter, Range

class VehicleQueryBuilder:
    @staticmethod
    def build(profile: Profile):
        semantic_parts = []
        if profile.habit: semantic_parts.append(profile.habit)
        if profile.colors: semantic_parts.extend(profile.colors)
        if profile.features: semantic_parts.extend(profile.features)
        if profile.safety_priority: semantic_parts.append(f"Ưu tiên an toàn {profile.safety_priority}")
        if profile.environmental_priority: semantic_parts.append(f"Ưu tiên môi trường {profile.environmental_priority}")
        if profile.cargo_need: semantic_parts.append(profile.cargo_need)
        query_text = " ".join(semantic_parts) if semantic_parts else "tìm xe phù hợp"

        must_filters = []
        if profile.state:
            must_filters.append(FieldCondition(key="state", match=MatchValue(value=profile.state)))
        if profile.zip:
            must_filters.append(FieldCondition(key="zip", match=MatchValue(value=profile.zip)))
        if profile.engine_type:
            must_filters.append(FieldCondition(key="engine_type", match=MatchValue(value=profile.engine_type)))
        if profile.eco_friendly is not None:
            must_filters.append(FieldCondition(key="eco_friendly", match=MatchValue(value=profile.eco_friendly)))
        if profile.car_condition_preference and profile.car_condition_preference != "both":
            must_filters.append(FieldCondition(key="condition", match=MatchValue(value=profile.car_condition_preference)))

        if profile.finance:
            delta = 500
            if profile.finance.payment_method == "cash" and profile.finance.cash_budget is not None:
                min_price = max(0, profile.finance.cash_budget - delta)
                max_price = profile.finance.cash_budget + delta
                must_filters.append(FieldCondition(
                    key="price",
                    range=Range(gte=min_price, lte=max_price)  # Dùng Range thay vì MatchValue dict
                ))
            elif profile.finance.payment_method in ["loan", "lease"] and profile.finance.monthly_capacity is not None:
                min_payment = max(0, profile.finance.monthly_capacity - delta)
                max_payment = profile.finance.monthly_capacity + delta
                must_filters.append(FieldCondition(
                    key="monthly_payment",
                    range=Range(gte=min_payment, lte=max_payment)  # Dùng Range thay vì MatchValue dict
                ))

        should_filters = []
        if profile.brand_preference:
            should_filters.extend([FieldCondition(key="brand", match=MatchValue(value=b)) for b in profile.brand_preference])
        if profile.body_type:
            should_filters.extend([FieldCondition(key="body_type", match=MatchValue(value=b)) for b in profile.body_type])

        qfilter = Filter(
            must=must_filters if must_filters else None,
            should=should_filters if should_filters else None
        ) if (must_filters or should_filters) else None

        return query_text, qfilter
