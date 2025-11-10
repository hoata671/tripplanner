from db import get_db
from bson import ObjectId
import random

def save_trip(data):
    db = get_db()
    return str(db.trips.insert_one(data).inserted_id)

def get_trip_by_id(trip_id):
    db = get_db()
    return db.trips.find_one({"_id": ObjectId(trip_id)})

def get_user_trips(user_id):
    db = get_db()
    return list(db.trips.find({"user_id": user_id}))

def get_latest_trips(limit=6):
    db = get_db()
    return list(db.trips.find().sort("_id", -1).limit(limit))

def get_random_recommended_trips(limit=5):
    db = get_db()
    total = db.trips.estimated_document_count()
    if total < limit:
        return list(db.trips.find().limit(limit))
    skip_list = random.sample(range(total), limit)
    return [db.trips.find().skip(s).limit(1).next() for s in skip_list]


def add_favorite(user_id, trip_id):
    db = get_db()
    db.favorites.update_one(
        {"user_id": user_id, "trip_id": trip_id},
        {"$set": {"user_id": user_id, "trip_id": trip_id}},
        upsert=True
    )

def remove_favorite(user_id, trip_id):
    db = get_db()
    db.favorites.delete_one({"user_id": user_id, "trip_id": trip_id})

def is_favorite(user_id, trip_id):
    db = get_db()
    return db.favorites.find_one({"user_id": user_id, "trip_id": trip_id}) is not None

def get_favorite_trip_ids(user_id):
    db = get_db()
    return [f['trip_id'] for f in db.favorites.find({"user_id": user_id})]

def get_user_trips(user_id):
    db = get_db()
    return list(db.trips.find({"user_id": user_id}))

def search_trips_by_location(keyword):
    db = get_db()
    if not keyword:
        return []
    regex = {"$regex": keyword, "$options": "i"}  # tìm không phân biệt hoa thường
    return list(db.trips.find({
        "$or": [
            {"main_destination": regex},
            {"destinations": regex}
        ]
    }))
