from dataclasses import dataclass
from typing import Optional

@dataclass
class Vehicle:
    id: Optional[int] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    color: Optional[str] = None
    body_type: Optional[str] = None
    engine_type: Optional[str] = None
    horse_power: Optional[int] = None
    driving_environment: Optional[str] = None
    use_case: Optional[str] = None
    eco_friendly: Optional[str] = None
    safety_priority: Optional[str] = None
    environmental_priority: Optional[str] = None
    cargo_need: Optional[str] = None
    features: Optional[str] = None
    price: Optional[float] = None
    monthly_payment: Optional[float] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    fuel_type: Optional[str] = None
    fuel_efficiency: Optional[float] = None  # mpg hoặc kWh/mi tuỳ loại xe
    mpg: Optional[float] = None             # Chỉ dành cho xe xăng/diesel
    kwh_per_mile: Optional[float] = None
    transmission: Optional[str] = None      # Automatic, Manual, CVT, ...
    seats: Optional[int] = None             # Số chỗ ngồi
    drivetrain: Optional[str] = None        # FWD, RWD, AWD, ...
