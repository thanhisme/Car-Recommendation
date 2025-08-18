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
