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
    """

    def __init__(self, profile: Profile):
        """
        Khởi tạo đối tượng TCOCalculator.

        Parameters:
            profile (Profile): Đối tượng chứa thông tin người dùng và cấu hình vùng.
        
        Raises:
            ValueError: Nếu cấu hình không tồn tại cho khu vực của người dùng.
        """
        state = profile.state
        if state not in REGION_CONFIG:
            raise ValueError(f"No config found for state {state}")
        self.config = REGION_CONFIG[state]
        self.profile = profile
        self.annual_miles = profile.annual_mileage or 12000


    def _apply_voucher(self, vehicle: Vehicle, voucher: Voucher) -> float:
        """
        Áp dụng voucher giảm giá cho xe, nếu có điều kiện phù hợp.

        Parameters:
            vehicle (Vehicle): Đối tượng xe cần tính toán.
            voucher (Voucher): Đối tượng voucher cần áp dụng cho xe.

        Returns:
            float: Giá trị giảm giá áp dụng cho xe, nếu voucher hợp lệ.
        
        Notes:
            Nếu voucher không hợp lệ với xe, hàm trả về giá trị 0.0.
        """
        if not voucher:
            return 0.0
        if voucher.applicable_makes and vehicle.make not in voucher.applicable_makes:
            return 0.0
        if voucher.applicable_models and vehicle.model not in voucher.applicable_models:
            return 0.0
        if voucher.applicable_years and vehicle.year not in voucher.applicable_years:
            return 0.0
        if voucher.excluded_trims and vehicle.trim in voucher.excluded_trims:
            return 0.0
        return voucher.value or 0.0

    def calculate_tco(self, vehicle: Vehicle, voucher: Voucher = None, years: int = 5, vouchers: list = None, member_level: str = None):
        """
        Tính toán tổng chi phí sở hữu xe (TCO) trong một khoảng thời gian cụ thể.

        Parameters:
            vehicle (Vehicle): Đối tượng xe cần tính toán.
            voucher (Voucher, optional): Voucher giảm giá áp dụng cho xe. Mặc định là None.
            years (int, optional): Số năm sử dụng xe. Mặc định là 5 năm.
            vouchers (list, optional): Danh sách voucher có sẵn. Mặc định là None.
            member_level (str, optional): Mức độ thành viên của người dùng. Mặc định là None.

        Returns:
            dict: Tổng chi phí sở hữu xe và chi tiết từng khoản chi phí (breakdown).
        
        Notes:
            Nếu có voucher và thành viên hợp lệ, danh sách các voucher sẽ được trả về trong kết quả.
        """
        breakdown = {}
        breakdown["initial_cost"] = self._calc_initial_cost(vehicle, voucher)

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
            from features.vouchers import get_discount_vouchers
            available_vouchers = get_discount_vouchers(vouchers, vehicle, vehicle.year, member_level)

        return {
            "tco_total": total,
            "breakdown": breakdown,
            "available_vouchers": [v.__dict__ for v in available_vouchers]
        }

    def _calc_initial_cost(self, vehicle: Vehicle, voucher: Voucher):
        """
        Tính toán chi phí ban đầu của xe, bao gồm giá xe, thuế, phí đăng ký và voucher giảm giá.

        Parameters:
            vehicle (Vehicle): Đối tượng xe cần tính toán chi phí ban đầu.
            voucher (Voucher): Đối tượng voucher giảm giá áp dụng.

        Returns:
            BreakdownItem: Chi phí ban đầu của xe được tính toán, bao gồm giá trị và giải thích chi tiết.
        """
        base_price = vehicle.base_price
        applied_voucher = self._apply_voucher(vehicle, voucher)
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
        """
        Tính toán chi phí năng lượng (điện) cho xe điện trong một khoảng thời gian sử dụng.

        Parameters:
            vehicle (Vehicle): Đối tượng xe cần tính toán chi phí năng lượng.
            years (int): Số năm sử dụng xe.

        Returns:
            BreakdownItem: Chi phí năng lượng trong suốt thời gian sử dụng xe.
        """
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
        """
        Tính toán chi phí nhiên liệu cho xe xăng/diesel trong một khoảng thời gian sử dụng.

        Parameters:
            vehicle (Vehicle): Đối tượng xe cần tính toán chi phí nhiên liệu.
            years (int): Số năm sử dụng xe.

        Returns:
            BreakdownItem: Chi phí nhiên liệu trong suốt thời gian sử dụng xe.
        """
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
        """
        Tính toán chi phí bảo hiểm cho xe trong một khoảng thời gian sử dụng.

        Parameters:
            vehicle (Vehicle): Đối tượng xe cần tính toán chi phí bảo hiểm.
            years (int): Số năm sử dụng xe.

        Returns:
            BreakdownItem: Chi phí bảo hiểm trong suốt thời gian sử dụng xe.
        """
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
        """
        Tính toán chi phí bảo trì xe trong suốt thời gian sử dụng, có thể tăng dần theo năm.

        Parameters:
            vehicle (Vehicle): Đối tượng xe cần tính toán chi phí bảo trì.
            years (int): Số năm sử dụng xe.

        Returns:
            BreakdownItem: Tổng chi phí bảo trì trong suốt thời gian sử dụng xe.
        """
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
        """
        Tính toán chi phí gửi xe trong suốt thời gian sử dụng, có thể tăng dần theo năm.

        Parameters:
            years (int): Số năm sử dụng xe.

        Returns:
            BreakdownItem: Tổng chi phí gửi xe trong suốt thời gian sử dụng xe.
        """
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
        """
        Tính toán chi phí cầu đường trong suốt thời gian sử dụng xe, có thể tăng dần theo năm.

        Parameters:
            years (int): Số năm sử dụng xe.

        Returns:
            BreakdownItem: Tổng chi phí cầu đường trong suốt thời gian sử dụng xe.
        """
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