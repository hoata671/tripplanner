import requests, os
from dotenv import load_dotenv
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
}

def get_destination_id(city):
    url = "https://booking-com.p.rapidapi.com/v1/hotels/locations"
    params = {"name": city, "locale": "en-gb"}
    res = requests.get(url, headers=HEADERS, params=params)
    data = res.json()
    return data[0]["dest_id"] if data else None

def get_hotels(dest_id, checkin, checkout):
    url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
    params = {
        "dest_id": dest_id,
        "dest_type": "city",
        "checkin_date": checkin,
        "checkout_date": checkout,
        "adults_number": "2",
        "order_by": "popularity",
        "locale": "en-gb",
        "units": "metric",
        "room_number": "1",
        "filter_by_currency": "VND"
    }
    res = requests.get(url, headers=HEADERS, params=params)
    return res.json()

def fetch_booking_hotels(city, checkin, checkout):
    dest_id = get_destination_id(city)
    if not dest_id:
        return []
    data = get_hotels(dest_id, checkin, checkout)
    hotels = []
    for h in data.get("result", [])[:5]:
        hotels.append({
            "name": h.get("hotel_name"),
            "location": h.get("address", "Không rõ"),
            "image": h.get("max_1440_photo", ""),
            "link": f"https://www.booking.com/hotel/{h.get('hotel_id')}.html"
        })
    return hotels
