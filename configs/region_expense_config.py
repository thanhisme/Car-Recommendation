# configs/region_config.py
# Cấu hình chi phí theo từng bang

REGION_CONFIG = {
    "CA": {
        "state": "CA",
        "tax_rate": 0.0725,  # 7.25% (state base, chưa gồm city)
        "registration_fee": 600,  # phí đăng ký trung bình
        "fuel_price": 5.2,  # USD/gallon (2025)
        "electricity_price": 0.28,  # USD/kWh (EV, 2025)
        "insurance_base": 0.045,  # 4.5% giá xe/năm
        "parking_fee": 1800,  # trung bình thành phố lớn
        "toll_fee": 900,  # nhiều cầu đường
        "parking_escalation": 1.06,  # tăng 6% mỗi năm
        "toll_escalation": 1.04,  # tăng 4% mỗi năm
        "maintenance": {
            "Toyota": {
                "base_maint": 420, 
                "escalation": 1.12
            },
            "Ford": {
                "base_maint": 950, 
                "escalation": 1.2
            },
            "Honda": {
                "base_maint": 480, 
                "escalation": 1.13
            },
            "Tesla": {
                "base_maint": 350, 
                "escalation": 1.09
            },
            "BMW": {
                "base_maint": 1200, 
                "escalation": 1.25
            },
        },
    },
    "NY": {
        "state": "NY",
        "tax_rate": 0.08875,  # 8.875% (NYC)
        "registration_fee": 750,  # cao hơn CA
        "fuel_price": 4.9,  # USD/gallon
        "electricity_price": 0.32,  # USD/kWh
        "insurance_base": 0.055,  # 5.5% giá xe/năm
        "parking_fee": 3200,  # cực cao ở Manhattan
        "toll_fee": 1800,  # nhiều cầu/tunnel
        "parking_escalation": 1.08,  # tăng 8% mỗi năm
        "toll_escalation": 1.05,  # tăng 5% mỗi năm
        "maintenance": {
            "Toyota": {
                "base_maint": 450, 
                "escalation": 1.13
            },
            "Ford": {
                "base_maint": 1000, 
                "escalation": 1.22
            },
            "Honda": {
                "base_maint": 500, 
                "escalation": 1.15
            },
            "Tesla": {
                "base_maint": 370, 
                "escalation": 1.1
            },
            "BMW": {
                "base_maint": 1300, 
                "escalation": 1.28
            },
        },
    },
    "TX": {
        "state": "TX",
        "tax_rate": 0.0625,  # 6.25%
        "registration_fee": 350,  # thấp
        "fuel_price": 3.7,  # USD/gallon
        "electricity_price": 0.14,  # USD/kWh
        "insurance_base": 0.038,  # 3.8% giá xe/năm
        "parking_fee": 700,  # thấp
        "toll_fee": 400,  # ít cầu đường
        "parking_escalation": 1.03,  # tăng 3% mỗi năm
        "toll_escalation": 1.02,  # tăng 2% mỗi năm
        "maintenance": {
            "Toyota": {
                "base_maint": 390, 
                "escalation": 1.1
            },
            "Ford": {
                "base_maint": 800, 
                "escalation": 1.18
            },
            "Honda": {
                "base_maint": 420, 
                "escalation": 1.12
            },
            "Tesla": {
                "base_maint": 340, 
                "escalation": 1.08
            },
            "BMW": {
                "base_maint": 1100, 
                "escalation": 1.22
            },
        },
    },
}
