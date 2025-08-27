# AutoTrader-Api: Car Recommendation System

## Business Overview

AutoTrader-Api is an intelligent car recommendation system that helps users find the perfect vehicle based on their personal preferences, financial situation, and specific needs. The system leverages semantic search, vector databases, and business strategies to deliver personalized vehicle recommendations.

## Business Flow

1. **User Profile Creation**

   - User provides information about their location, budget, driving habits, preferences
   - System processes this information to create a comprehensive user profile

2. **Vehicle Recommendation Process**

   - Semantic search matches user's needs with available vehicles
   - Financial offers are generated based on user's budget and payment preferences
   - Vehicles are filtered by compatibility with user's financial constraints
   - TCO (Total Cost of Ownership) is calculated for each potential match
   - Applicable vouchers and discounts are automatically applied

3. **Vehicle Details & Analysis**

   - Users can request detailed information about specific vehicles using their VIN
   - System provides comprehensive TCO analysis including maintenance, insurance, and depreciation
   - Comparisons between vehicles help users make informed decisions

4. **Default Recommendations**
   - For quick browsing, users can get recommendations with minimal input (just their state)
   - These recommendations use a default profile with broad parameters

## Configurable Settings

### Business Strategy Configuration

- **Strategy Config (`configs/strategy_config.py`)**
  - Configure weights for different recommendation factors
  - Set brand priorities for promotional campaigns
  - Define business rules for vehicle scoring and ranking

### Regional Settings

- **Region Expense Config (`configs/region_expense_config.py`)**
  - Configure state-specific tax rates
  - Set insurance cost modifiers by region
  - Define regional maintenance cost factors

### Commercial Features

- **Commercial Features Config (`configs/commercial_features_config.py`)**
  - Set up promotional campaigns
  - Configure discount voucher rules and eligibility
  - Define member level benefits and special offers

## API Endpoints

### Vehicle Recommendations

- `POST /recommend` - Get personalized vehicle recommendations based on detailed profile
- `GET /recommend/default?state={state}` - Get basic recommendations filtered by state

### Vehicle Details

- `POST /vehicle/details` - Get detailed vehicle information with TCO by VIN and profile
- `GET /vehicle/details/default/{vin}?state={state}` - Get vehicle details with default profile

## Example Request

```http
POST http://127.0.0.1:8000/recommend
Content-Type: application/json
{
  "state": "CA",
  "zip": "94105",
  "finance": {
    "payment_method": "loan",
    "cash_budget": 20000,
    "monthly_capacity": 500
  },
  "habit": "I drive daily in urban areas, prefer eco-friendly vehicles, and need space for a small family.",
  "colors": ["red", "black", "white"],
  "age": 28,
  "family_size": 4,
  "driving_experience": 10,
  "accident_history": false,
  "annual_mileage": 12000,
  "parking": "garage",
  "cargo_need": "medium",
  "brand_preference": ["Honda", "Tesla"],
  "body_type": ["sedan", "EV"],
  "features": ["autopilot", "bluetooth", "backup camera"],
  "safety_priority": "very high",
  "environmental_priority": "very high",
  "eco_friendly": true,
  "car_condition_preference": "new",
  "memberLevel": "premium",
  "engine_type": "Hybrid",
  "campaign": "clearance sale"
}
```

## Example Response

```json
{
	"summary": "We found cars that match your preferences, budget, and lifestyle.",
	"your_profile": {
		"location": "CA, 94105",
		"budget": {
			"cash_budget": 20000.0,
			"monthly_capacity": 500.0,
			"payment_method": "loan"
		},
		"eco_friendly": true,
		"preferences_from_semantic_search": [
			{
				"year": 2022,
				"make": "Honda",
				"model": "Civic",
				"trim": "EX Sedan",
				"reason": "Phù hợp với ngân sách, tiết kiệm nhiên liệu và kiểu dáng sedan"
			},
			{
				"year": 2023,
				"make": "Tesla",
				"model": "Model 3",
				"trim": "Long Range AWD",
				"reason": "Xe điện, có Autopilot, thân thiện môi trường, phù hợp với nhu cầu EV"
			}
		]
	},
	"finance_info": {
		"payment_capacity": "You can afford cars up to $20000 in cash or around $500/month if financed."
	},
	"recommended_cars": [
		{
			"year": 2022,
			"make": "Honda",
			"model": "Civic",
			"trim": "EX Sedan",
			"color": "Blue",
			"reason": "Phù hợp với ngân sách, tiết kiệm nhiên liệu và kiểu dáng sedan + phù hợp với khả năng tài chính (voucher áp dụng: 0$)",
			"tco_total": 50179.4875248,
			"breakdown": {
				"initial_cost": {
					"value": 23122.5,
					"explanation": {
						"base_price": 21000,
						"tax": 1522.5,
						"registration_fee": 600,
						"applied_voucher": -0.0
					}
				},
				"energy_cost": {
					"value": 4200.000000000001,
					"explanation": {
						"annual_mileage": 12000,
						"kwh_per_mile": 0.25,
						"electricity_price": 0.28,
						"years": 5
					}
				},
				"insurance": {
					"value": 4725.0,
					"explanation": {
						"price": 21000,
						"insurance_rate": 0.045,
						"years": 5
					}
				},
				"maintenance": {
					"value": 3110.5298927999993,
					"explanation": {
						"base": 480,
						"escalation": 1.13,
						"years": 5
					}
				},
				"parking": {
					"value": 10146.77,
					"explanation": {
						"base": 1800,
						"escalation": 1.06,
						"years": 5
					}
				},
				"toll": {
					"value": 4874.69,
					"explanation": {
						"base": 900,
						"escalation": 1.04,
						"years": 5
					}
				}
			},
			"available_vouchers": []
		}
	]
}
```

## Setup & Development

1. **Environment Setup**:
   - Install dependencies: `pip install -r requirements.txt`
2. **Running the API**:

   - Start the server: `uvicorn main:app --reload`
   - Access the API documentation at: `http://127.0.0.1:8000/docs`

3. **Configuration Files**:
   - Adjust business logic and regional settings in the `configs/` directory
   - Modify vehicle scoring algorithms in the `features/` directory
