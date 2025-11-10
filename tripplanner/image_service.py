import requests
import os

def get_unsplash_image(query):
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 1,
        "orientation": "landscape",
        "client_id": access_key
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            results = response.json().get("results")
            if results:
                return results[0]["urls"]["regular"]
    except Exception as e:
        print("❌ Lỗi lấy ảnh Unsplash:", e)

    return "/static/default.jpg"
