from configs.region_expense_config import REGION_CONFIG
from models.breakdown_item import BreakdownItem
from models.profile import Profile
from models.tco_calculator_summary import TCOCalculatorSummary
from models.vehicle import Vehicle
from models.voucher import Voucher


class TCOCalculator:
    """
    TCOCalculator
    Tính toán tổng chi phí sở hữu xe (Total Cost of Ownership) theo cấu hình vùng, profile người dùng, loại xe, voucher, số năm sử dụng.

    Các field:
      - config: cấu hình vùng (tax, phí, ...)
      - profile: thông tin người dùng (bang, số km/năm, ...)
      - annual_miles: số km/năm mặc định hoặc lấy từ profile

    Các phương thức:
      - _apply_voucher: kiểm tra voucher có áp dụng cho xe/năm không, trả về giá trị giảm giá
      - calculate_tco: tính toán chi phí sở hữu xe, trả về breakdown từng loại chi phí và tổng
    """

    def __init__(self, profile: Profile):
        state = profile.state
        if state not in REGION_CONFIG:
            raise ValueError(f"No config found for state {state}")
        self.config = REGION_CONFIG[state]
        self.profile = profile
        self.annual_miles = profile.annual_mileage or 12000

    def summary(self, vehicle: Vehicle = None, voucher: Voucher = None, years: int = 5):
        """
        Trả về thông tin tóm tắt về cấu hình, profile, annual_miles và breakdown chi phí nếu đã tính
        """
        result = {
            "config": self.config,
            "profile": self.profile,
            "annual_miles": self.annual_miles,
        }
        if vehicle:
            tco = self.calculate_tco(vehicle, voucher, years)
            result["tco_total"] = tco["tco_total"]
            result["breakdown"] = tco["breakdown"]
        return TCOCalculatorSummary(result)

    def _apply_voucher(self, vehicle: Vehicle, voucher: Voucher, year: int) -> float:
        if not voucher:
            return 0.0
        if voucher.applicable_makes and vehicle.make not in voucher.applicable_makes:
            return 0.0
        if voucher.applicable_models and vehicle.model not in voucher.applicable_models:
            return 0.0
        if voucher.applicable_years and year not in voucher.applicable_years:
            return 0.0
        if voucher.excluded_trims and vehicle.trim in voucher.excluded_trims:
            return 0.0
        return voucher.value or 0.0

    def calculate_tco(self, vehicle: Vehicle, voucher: Voucher = None, years: int = 5, vouchers: list = None, member_level: str = None):
        breakdown = {}
        breakdown["initial_cost"] = self._calc_initial_cost(vehicle, voucher, years)

        if vehicle.fuel_type == "EV":
            breakdown["energy_cost"] = self._calc_energy_cost(vehicle, years)
        else:
            breakdown["fuel_cost"] = self._calc_fuel_cost(vehicle, years)

        breakdown["insurance"] = self._calc_insurance(vehicle, years)
        breakdown["maintenance"] = self._calc_maintenance(vehicle, years)
        breakdown["parking"] = self._calc_parking(years)
        breakdown["toll"] = self._calc_toll(years)

        total = sum(item.value for item in breakdown.values())

        # Get available vouchers for this vehicle
        available_vouchers = []
        if vouchers is not None and member_level is not None:
            from utils.voucher_utils import get_discount_vouchers
            available_vouchers = get_discount_vouchers(vouchers, vehicle, vehicle.year, member_level)

        return {
            "tco_total": total,
            "breakdown": breakdown,
            "available_vouchers": [v.__dict__ for v in available_vouchers]
        }

    def _calc_initial_cost(self, vehicle: Vehicle, voucher: Voucher, years: int):
        base_price = vehicle.base_price
        applied_voucher = self._apply_voucher(vehicle, voucher, vehicle.year)
        tax = base_price * self.config["tax_rate"]
        reg_fee = self.config["registration_fee"]
        initial_cost = base_price + tax + reg_fee - applied_voucher
        return BreakdownItem(
            value=initial_cost,
            explanation={
                "base_price": base_price,
                "tax": tax,
                "registration_fee": reg_fee,
                "applied_voucher": -applied_voucher,
            },
        )

    def _calc_energy_cost(self, vehicle: Vehicle, years: int):
        annual_cost = (
            self.annual_miles * vehicle.kwh_per_mile * self.config["electricity_price"]
        )
        return BreakdownItem(
            value=annual_cost * years,
            explanation={
                "annual_mileage": self.annual_miles,
                "kwh_per_mile": vehicle.kwh_per_mile,
                "electricity_price": self.config["electricity_price"],
                "years": years,
            },
        )

    def _calc_fuel_cost(self, vehicle: Vehicle, years: int):
        annual_cost = (self.annual_miles / vehicle.mpg) * self.config["fuel_price"]
        return BreakdownItem(
            value=annual_cost * years,
            explanation={
                "annual_mileage": self.annual_miles,
                "mpg": vehicle.mpg,
                "fuel_price": self.config["fuel_price"],
                "years": years,
            },
        )

    def _calc_insurance(self, vehicle: Vehicle, years: int):
        base_price = vehicle.base_price
        insurance = base_price * self.config["insurance_base"] * years
        return BreakdownItem(
            value=insurance,
            explanation={
                "price": base_price,
                "insurance_rate": self.config["insurance_base"],
                "years": years,
            },
        )

    def _calc_maintenance(self, vehicle: Vehicle, years: int):
        brand = vehicle.make
        maint_conf = self.config.get("maintenance", {}).get(
            brand, {"base_maint": 800, "escalation": 1.2}
        )
        base_maint = maint_conf["base_maint"]
        escalation = maint_conf["escalation"]

        maint_cost = 0
        for y in range(1, years + 1):
            maint_cost += base_maint * (escalation ** (y - 1))

        return BreakdownItem(
            value=maint_cost,
            explanation={"base": base_maint, "escalation": escalation, "years": years},
        )

    def _calc_parking(self, years: int):
        parking_base = self.config.get("parking_fee", 0)
        parking_escalation = self.config.get("parking_escalation", 1.0)
        parking_cost = 0
        for y in range(1, years + 1):
            parking_cost += parking_base * (parking_escalation ** (y - 1))
        return BreakdownItem(
            value=parking_cost,
            explanation={
                "base": parking_base,
                "escalation": parking_escalation,
                "years": years,
            },
        )

    def _calc_toll(self, years: int):
        toll_base = self.config.get("toll_fee", 0)
        toll_escalation = self.config.get("toll_escalation", 1.0)
        toll_cost = 0
        for y in range(1, years + 1):
            toll_cost += toll_base * (toll_escalation ** (y - 1))
        return BreakdownItem(
            value=toll_cost,
            explanation={
                "base": toll_base,
                "escalation": toll_escalation,
                "years": years,
            },
        )
