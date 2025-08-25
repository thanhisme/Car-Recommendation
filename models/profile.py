# models/profile.py

from dataclasses import dataclass, field
from typing import Optional, List
from models.finance import Finance

@dataclass
class Profile:
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
    car_condition_preference: Optional[str] = "both"
    memberLevel: Optional[str] = None
    engine_type: Optional[str] = None

    def __str__(self):
        parts = [f"Người dùng ở bang {self.state}"]
        if self.zip: parts.append(f"Zip code: {self.zip}")
        if self.finance: parts.append(f"Tài chính: {self.finance}")
        if self.habit: parts.append(f"Thói quen lái xe: {self.habit}")
        if self.colors: parts.append(f"Màu xe yêu thích: {', '.join(self.colors)}")
        if self.age: parts.append(f"Tuổi: {self.age}")
        if self.family_size: parts.append(f"Gia đình {self.family_size} người")
        if self.driving_experience: parts.append(f"Kinh nghiệm lái: {self.driving_experience} năm")
        if self.accident_history: 
            parts.append("Đã từng gặp tai nạn" if self.accident_history else "Chưa từng gặp tai nạn")
        if self.annual_mileage: parts.append(f"Quãng đường chạy hàng năm: {self.annual_mileage} km")
        if self.parking: parts.append(f"Thường đậu xe: {self.parking}")
        if self.cargo_need: parts.append(f"Nhu cầu chở hàng: {self.cargo_need}")
        if self.brand_preference: parts.append(f"Thích các hãng: {', '.join(self.brand_preference)}")
        if self.body_type: parts.append(f"Kiểu xe ưa thích: {', '.join(self.body_type)}")
        if self.features: parts.append(f"Tính năng cần: {', '.join(self.features)}")
        if self.safety_priority: parts.append(f"Ưu tiên an toàn: {self.safety_priority}")
        if self.environmental_priority: parts.append(f"Ưu tiên môi trường: {self.environmental_priority}")
        if self.eco_friendly is not None: 
            parts.append("Muốn xe tiết kiệm nhiên liệu/điện" if self.eco_friendly else "Không quan trọng tiết kiệm nhiên liệu/điện")
        if self.car_condition_preference: parts.append(f"Muốn mua xe: {self.car_condition_preference}")
        if self.memberLevel: parts.append(f"Khách hàng hạng: {self.memberLevel}")
        if self.engine_type: parts.append(f"Động cơ mong muốn: {self.engine_type}")
        return ". ".join(parts)

