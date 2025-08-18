# models/profile.py

from dataclasses import dataclass, field
from typing import Optional, List
from models.finance import Finance

@dataclass
class Profile:
    """
    Profile
    Đại diện cho thông tin người dùng (kết hợp đầy đủ các trường)
    """
    state: str
    zip: Optional[str] = None
    finance: Optional[Finance] = None
    habit: Optional[str] = None
    colors: Optional[List[str]] = field(default_factory=list)
    age: Optional[int] = None
    family_size: Optional[int] = None
    driving_experience: Optional[int] = None
    accident_history: Optional[bool] = None
    annual_mileage: Optional[int] = None
    parking: Optional[str] = None
    cargo_need: Optional[str] = None
    brand_preference: Optional[List[str]] = field(default_factory=list)
    body_type: Optional[List[str]] = field(default_factory=list)
    features: Optional[List[str]] = field(default_factory=list)
    safety_priority: Optional[str] = None
    environmental_priority: Optional[str] = None
    eco_friendly: Optional[bool] = None
    car_condition_preference: Optional[str] = "both"  # "new" | "used" | "both"
    memberLevel: Optional[str] = None
