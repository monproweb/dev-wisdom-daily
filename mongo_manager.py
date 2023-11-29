from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

uri = f"mongodb+srv://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@devwisdomdaily.6gziorw.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri, server_api=ServerApi("1"))

try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["devwisdomdaily"]
quotes_collection = db["quotes"]


def insert_quote(quote_text):
    quotes_collection.insert_one({"quote": quote_text})
    quotes_count = quotes_collection.count_documents({})

    if quotes_count > 50:
        oldest_quote = quotes_collection.find_one(sort=[("_id", 1)])
        quotes_collection.delete_one({"_id": oldest_quote["_id"]})


def get_last_50_quotes():
    last_50_quotes = quotes_collection.find().sort([("_id", -1)]).limit(50)
    return [quote["quote"] for quote in last_50_quotes]
