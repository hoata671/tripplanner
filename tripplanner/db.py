from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

def get_db():
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    return client["Tripplanner"]
