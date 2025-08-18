# offers_db.py
OFFERS_DB = {
    "premium": [
        {
            "id": "offer_001",
            "title": "$1000 Voucher",
            "description": "Get $1000 off for purchases above $30,000",
            "discount_type": "cashback",
            "value": 1000,
            "conditions": "Applicable for new cars only",
            "valid_until": "2025-12-31",
            "applicable_makes": ["BMW", "Mercedes-Benz"],
            "applicable_models": None,
            "applicable_years": [2023, 2024, 2025],
            "excluded_trims": ["Base"]
        },
        {
            "id": "offer_002",
            "title": "0.9% APR",
            "description": "Special low interest rate financing",
            "discount_type": "apr",
            "value": 0.9,
            "conditions": "36 months loan term",
            "valid_until": "2025-06-30",
            "applicable_makes": ["Lexus", "Toyota"],
            "applicable_models": ["RX", "Camry"],
            "applicable_years": None,
            "excluded_trims": []
        },
    ],
    "standard": [
        {
            "id": "offer_004",
            "title": "$500 Voucher",
            "description": "Save $500 on vehicles above $20,000",
            "discount_type": "cashback",
            "value": 500,
            "conditions": "Applicable for both new & used cars",
            "valid_until": "2025-12-31",
            "applicable_makes": ["Honda", "Hyundai", "Toyota"],
            "applicable_models": None,
            "applicable_years": None,
            "excluded_trims": []
        }
    ],
    "first_time_buyer": [
        {
            "id": "offer_006",
            "title": "$300 Voucher",
            "description": "Save $300 for your first purchase",
            "discount_type": "cashback",
            "value": 300,
            "conditions": "Only for first-time buyers",
            "valid_until": "2025-12-31",
            "applicable_makes": None,
            "applicable_models": None,
            "applicable_years": None,
            "excluded_trims": []
        }
    ],
    "default": [
        {
            "id": "offer_008",
            "title": "Seasonal Discount",
            "description": "General promotion available to all customers",
            "discount_type": "percentage",
            "value": 5,
            "conditions": "Applicable to all cars",
            "valid_until": "2025-08-31",
            "applicable_makes": None,
            "applicable_models": None,
            "applicable_years": None,
            "excluded_trims": []
        }
    ]
}
