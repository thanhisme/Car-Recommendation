import json
import pandas as pd
from dacite import from_dict
from models.voucher import Voucher
from models.vehicle import Vehicle
from typing import List, Dict, Any

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

def load_raw_vehicles(csv_path: str = "data/vehicle.raw.csv") -> List[Dict[str, Any]]:
    """
    Load vehicle data from CSV file using pandas (for building vector database).
    
    Parameters:
        csv_path (str): Path to the CSV file containing vehicle data.
        
    Returns:
        List[Dict[str, Any]]: List of vehicle dictionaries with processed data.
    """
    # Load data from CSV file
    df = pd.read_csv(csv_path)
    
    # Convert DataFrame to list of dictionaries
    cars = []
    for index, row in df.iterrows():
        # Clean price data (remove $ and convert to int)
        price_str = str(row['Price']).replace('$', '').replace(',', '')
        price = int(price_str) if price_str.isdigit() else 0
        
        # Clean monthly payment data
        monthly_str = str(row['MonthlyPayment']).replace('$', '').replace(',', '')
        monthly_payment = int(monthly_str) if monthly_str.isdigit() else 0
        
        # Parse features from string to list
        features_str = str(row['Features'])
        features = [f.strip() for f in features_str.split(',') if f.strip()]
        
        car = {
            "id": int(row['ID']) if 'ID' in row else index + 1,  # Use ID from CSV if available
            "year": int(row['Year']),
            "make": str(row['Make']),
            "model": str(row['Model']),
            "trim": str(row['Trim']),
            "color": str(row['Color']),
            "desc": str(row['Description']),
            "state": str(row['State']),
            "zip": str(row['Zip']),
            "engine_type": str(row['EngineType']).lower(),
            "body_type": str(row['BodyType']).lower(),
            "brand": str(row['Make']),
            "features": features,
            "price": price,
            "monthly_payment": monthly_payment,
            "horsepower": int(row['HorsePower']) if pd.notna(row['HorsePower']) else 0,
            "driving_environment": str(row['DrivingEnvironment']),
            "use_case": str(row['UseCase']),
            "eco_friendly": str(row['EcoFriendly']).lower() == 'high',
            "safety_priority": str(row['SafetyPriority']).lower() == 'high',
            "environmental_priority": str(row['EnvironmentalPriority']).lower() == 'high',
            "cargo_need": str(row['CargoNeed']).lower()
        }
        cars.append(car)
    
    return cars
