from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime,timedelta
from dotenv import load_dotenv
from gptservice import build_prompt, ask_gpt
from image_service import get_unsplash_image
from model.trip_model import add_favorite, get_favorite_trip_ids, get_user_trips, is_favorite, remove_favorite, save_trip, get_trip_by_id, search_trips_by_location
import json, uuid, os
from hotel_service import fetch_booking_hotels
from model.trip_model import get_latest_trips, get_random_recommended_trips

app = Flask(__name__)
load_dotenv()

@app.route('/')
def home():
    recommended = get_random_recommended_trips(limit=5)
    latest = get_latest_trips(limit=6)

    for trip in recommended + latest:
        trip["_id"] = str(trip["_id"])

    return render_template("main.html",
        recommended_trips=recommended,
        latest_trips=latest,
        testimonials=[
            {"text": "Tôi đã có chuyến đi Đà Lạt tuyệt vời nhờ trang web này!",
             "image": "https://randomuser.me/api/portraits/women/65.jpg",
             "name": "Thảo Nguyễn"},
            {"text": "Rất tiện lợi và dễ sử dụng!",
             "image": "https://randomuser.me/api/portraits/men/44.jpg",
             "name": "Minh Quân"},
            {"text": "Giao diện thân thiện, gợi ý lịch trình cực hợp lý.",
             "image": "https://randomuser.me/api/portraits/women/21.jpg",
             "name": "Lan Phương"}
        ]
    )

@app.route('/create-trip', methods=['POST'])
def create_trip():
    form = request.form

    data = {
        "trip_name": form['trip_name'],
        "start_date": form['start_date'],
        "num_days": int(form['num_days']),
        "departure": form['departure'],
        "destinations": form['destinations'],
        "budget": int(form['budget']),
        "people": int(form['people']),
        "transport": form['transport'],
        "preferences": form.getlist('preferences'),
        "notes": form['notes']
    }

    user_id = request.cookies.get('user_id') or str(uuid.uuid4())
    data['user_id'] = user_id

    prompt = build_prompt(data)
    gpt_response = ask_gpt(prompt)

    if gpt_response is None:
        return "❌ GPT không phản hồi", 500

    with open("gpt_response_log.txt", "w", encoding="utf-8") as f:
        f.write(gpt_response)

    try:
        trip_json = json.loads(gpt_response)
        dest_img = trip_json.get("destination_image_url", "")
        if not dest_img or dest_img.startswith("search:"):
            keyword = dest_img.replace("search:", "").strip() if dest_img else trip_json.get('main_destination', 'vietnam')
            trip_json['destination_image_url'] = resolve_image(keyword)

        # Xử lý ảnh accommodations nếu thiếu hoặc "search:"
        for hotel in trip_json.get("accommodations", []):
            if not hotel.get("image") or hotel["image"].startswith("search:"):
                keyword = hotel.get("name", "hotel")
                hotel["image"] = resolve_image(keyword)

    except json.JSONDecodeError as e:
        with open("gpt_error_log.txt", "a", encoding="utf-8") as log:
            log.write(f"[LỖI JSON] {str(e)}\n")
        return "❌ GPT trả về dữ liệu không hợp lệ", 400

    # Gắn thêm dữ liệu form
    trip_json.update({
        "trip_name": data['trip_name'],
        "start_date": data['start_date'],
        "num_days": data['num_days'],
        "user_id": user_id
    })

    trip_id = save_trip(trip_json)

    resp = redirect(url_for('trip_detail', trip_id=trip_id))
    resp.set_cookie('user_id', user_id)
    return resp


@app.route('/trip/<trip_id>')
def trip_detail(trip_id):
    trip = get_trip_by_id(trip_id)
    user_id = request.cookies.get('user_id')
    is_fav = is_favorite(user_id, str(trip['_id'])) if user_id else False
    return render_template("trip_detail.html", trip=trip, is_favorite=is_fav)


@app.route('/favorite/<trip_id>', methods=['POST'])
def favorite_trip(trip_id):
    user_id = request.cookies.get('user_id')
    if user_id:
        add_favorite(user_id, trip_id)
    return redirect(url_for('trip_detail', trip_id=trip_id))

@app.route('/unfavorite/<trip_id>', methods=['POST'])
def unfavorite_trip(trip_id):
    user_id = request.cookies.get('user_id')
    if user_id:
        remove_favorite(user_id, trip_id)
    return redirect(url_for('trip_detail', trip_id=trip_id))

@app.route('/favorites')
def favorites():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    # Lấy danh sách trip_id mà user đã yêu thích
    favorite_trip_ids = get_favorite_trip_ids(user_id)

    # Lấy thông tin từng trip từ collection trips
    trips = [get_trip_by_id(trip_id) for trip_id in favorite_trip_ids if trip_id]

    return render_template("favorites.html", trips=trips)

@app.route('/history')
def history():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    trips = get_user_trips(user_id)
    return render_template("history.html", trips=trips)

@app.route('/search')
def search():
    keyword = request.args.get('q', '').strip()
    trips = search_trips_by_location(keyword) if keyword else []
    return render_template("search_results.html", trips=trips, keyword=keyword)

def resolve_image(query):
    """Trả về ảnh từ Unsplash (nếu có), fallback nếu không có"""
    return get_unsplash_image(query)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

