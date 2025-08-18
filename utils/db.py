import json
from dacite import from_dict
from models.voucher import Voucher
from models.vehicle import Vehicle
from typing import List

def get_vouchers_from_db(json_path: str = "data/vouchers.json") -> List[Voucher]:
    """
    Load vouchers from JSON file and parse to Voucher dataclass list.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        vouchers_data = json.load(f)
    return [from_dict(data_class=Voucher, data=v) for v in vouchers_data]

def get_vehicles_from_db(json_path: str = "data/vehicles.json") -> List[Vehicle]:
    """
    Load vehicles from JSON file and parse to Vehicle dataclass list.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        vehicles_data = json.load(f)
    return [from_dict(data_class=Vehicle, data=v) for v in vehicles_data]
