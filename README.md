# AutoTrader-Api: Car Recommendation System

## Giới thiệu

AutoTrader-Api là hệ thống API gợi ý xe ô tô thông minh, sử dụng công nghệ tìm kiếm ngữ nghĩa, vector database và các chiến lược kinh doanh để cá nhân hóa kết quả cho từng người dùng. Dự án này phù hợp cho các nền tảng thương mại điện tử ô tô, đại lý xe, hoặc các ứng dụng tư vấn mua xe.

## Tính năng chính

- **Gợi ý xe cá nhân hóa:** Dựa trên hồ sơ người dùng (Profile), thói quen, ngân sách, sở thích, nhu cầu sử dụng, v.v.
- **Tìm kiếm ngữ nghĩa:** Sử dụng mô hình embedding và vector database để tìm xe phù hợp nhất với mô tả, nhu cầu thực tế.
- **Chiến lược kinh doanh động:** Tích hợp các chiến dịch khuyến mãi, ưu đãi, ưu tiên thương hiệu/model, và các chiến lược bán hàng.
- **Tính toán TCO (Total Cost of Ownership):** Đánh giá chi phí sở hữu xe dựa trên hồ sơ tài chính và các voucher/ưu đãi.
- **API RESTful:** Dễ dàng tích hợp với các hệ thống frontend hoặc ứng dụng khác.

## Hướng dẫn sử dụng

1. **Cài đặt môi trường:**
   - Tạo virtualenv và cài đặt các package từ `requirements.txt`.
2. **Chạy server:**
   - Sử dụng lệnh: `uvicorn main:app --reload`
3. **Test API:**
   - Sử dụng file `client.http` hoặc công cụ như Postman để gửi request tới endpoint `/recommend`.
   - Payload cần cung cấp đầy đủ thông tin hồ sơ người dùng.
4. **Tùy chỉnh logic:**
   - Sửa các file trong `configs/`, `models/`, hoặc logic trong `langchain.py`/`recommender.py` để phù hợp nhu cầu thực tế.

## Ví dụ request

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
			},
			{
				"year": 2021,
				"make": "Honda",
				"model": "Accord",
				"trim": "Sport Special Edition",
				"reason": "Không gian rộng rãi cho gia đình, nhiều tính năng an toàn"
			}
		]
	},
	"finance_info": {
		"payment_capacity": "You can afford cars up to $20000.0 in cash or around $500.0/month if financed."
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
					"value": 10146.767328000002,
					"explanation": {
						"base": 1800,
						"escalation": 1.06,
						"years": 5
					}
				},
				"toll": {
					"value": 4874.690304000001,
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
