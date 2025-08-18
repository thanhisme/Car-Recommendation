from dataclasses import dataclass

@dataclass
class Vehicle:
    """
    Vehicle
    Đại diện cho một chiếc xe, có thể lấy từ DB hoặc khởi tạo từ dữ liệu.
    """
    make: str
    model: str
    trim: str
    year: int
    base_price: float
    fuel_type: str
    color: str | None = None
    fuel_efficiency: float | None = None  # mpg hoặc kWh/mi tuỳ loại xe
    mpg: float | None = None  # Chỉ dành cho xe xăng/diesel
    kwh_per_mile: float | None = None
    transmission: str | None = None       # Automatic, Manual, CVT, ...
    body_type: str | None = None          # Sedan, SUV, Hatchback, ...
    seats: int | None = None              # Số chỗ ngồi
    drivetrain: str | None = None         # FWD, RWD, AWD, ...
    description: str | None = None        # Mô tả thêm về xe
