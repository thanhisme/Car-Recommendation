from pydantic import BaseModel
from typing import Any, Dict, List, Optional

# -----------------------------
# Sub-models
# -----------------------------
class Finance(BaseModel):
    payment_method: str   # "cash" | "loan" | "lease"
    cash_budget: Optional[float] = None
    monthly_capacity: Optional[float] = None


class Profile(BaseModel):
    state: str
    zip: str
    finance: Finance
    habit: str
    colors: Optional[List[str]] = []

    age: Optional[int] = None
    family_size: Optional[int] = None
    driving_experience: Optional[int] = None
    accident_history: Optional[bool] = None

    annual_mileage: Optional[int] = None
    parking: Optional[str] = None
    cargo_need: Optional[str] = None

    brand_preference: Optional[List[str]] = []
    body_type: Optional[List[str]] = []
    features: Optional[List[str]] = []
    safety_priority: Optional[str] = None
    environmental_priority: Optional[str] = None
    eco_friendly: Optional[bool] = None
    customer_segment: Optional[str] = "first_time_buyer", # "standard" | "premium" | "first_time_buyer"
    car_condition_preference: Optional[str] = "both"  # "new" | "used" | "both"