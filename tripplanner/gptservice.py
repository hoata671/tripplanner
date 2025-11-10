import openai, os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def build_prompt(data):
    preferences = ", ".join(data.get('preferences', [])) or "không có"
    return f"""
Bạn là trợ lý AI chuyên lập kế hoạch dữ liệu thực du lịch tại Việt Nam. Hãy lập kế hoạch chi tiết cho chuyến đi theo đầu vào sau:

- Tên chuyến đi: {data['trip_name']}
- Ngày bắt đầu: {data['start_date']} ({data['num_days']} ngày)
- Xuất phát: {data['departure']}
- Điểm đến: {data['destinations']}
- Ngân sách: {data['budget']} VND
- Số người: {data['people']}
- Phương tiện: {data['transport']}
- Sở thích: {preferences}
- Ghi chú thêm: {data['notes']}

📌 YÊU CẦU CHẶT CHẼ:
1. `itinerary` phải gồm ĐẦY ĐỦ {data['num_days']} ngày.
2. Mỗi ngày nên có từ 2–4 điểm đến khác nhau.
3. `accommodations` phải trả về ít nhất 3 gợi ý khách sạn hoặc homestay thực tế.
4. `destination_image_url` nếu không thể cung cấp ảnh thật thì thay bằng: `"search: <tên điểm đến>"` để backend xử lý.

Trả về kết quả dưới dạng JSON CHÍNH XÁC như sau, không giải thích:

{{
  "main_destination": "string",
  "destination_description": "string",
  "destination_image_url": "string",
  "accommodations": [
    {{
      "name": "string",
      "image": "string",
      "location": "string",
      "link": "string"
    }}
    ,...
  ],
  "itinerary": [
    {{
      "day": "Day ...",
      "stops": [
        {{
          "name": "string",
          "description": "string",
          "map_query": "string",
          "estimated_time": "string"
        }}
      ]
    }}
    ,...
  ],
  "cost": {{
    "accommodation": int,
    "food": int,
    "transport": int,
    "activities": int
  }}
}}
Chỉ trả về JSON, không có bất kỳ lời mở đầu hoặc chú thích nào, lưu ý URL hình ảnh trả về là những hình ảnh từ các trang web du lịch (không phải từ example, upflash,..).
"""

def ask_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia du lịch Việt Nam, tạo JSON kế hoạch rõ ràng, chính xác."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1800
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print("❌ GPT API Error:", e)
        return None
