# region_config.py

REGION_CONFIG = {
    "CA": {   # California
        "state": "CA",
        "tax_rate": 0.08,
        "registration_fee": 500,
        "fuel_price": 3.5,         # USD per gallon
        "electricity_price": 0.15, # USD per kWh (EV)
        "insurance_base": 0.05,    # % of price per year
        "parking_fee": 1200,       # per year (California thường cao)
        "toll_fee": 600            # per year
    },
    "NY": {   # New York
        "state": "NY",
        "tax_rate": 0.0875,
        "registration_fee": 550,
        "fuel_price": 3.8,
        "electricity_price": 0.18,
        "insurance_base": 0.06,    # cao hơn CA
        "parking_fee": 2000,       # cực cao ở NYC
        "toll_fee": 1000           # nhiều cầu & tunnel
    },
    "TX": {   # Texas
        "state": "TX",
        "tax_rate": 0.0625,
        "registration_fee": 400,
        "fuel_price": 3.2,
        "electricity_price": 0.12,
        "insurance_base": 0.045,   # thấp hơn
        "parking_fee": 600,        # thấp
        "toll_fee": 300            # ít hơn
    }
}
