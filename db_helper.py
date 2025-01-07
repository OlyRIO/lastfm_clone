import config
from pymongo import MongoClient

# MongoDB configuration
mongo_uri = config.mongo_uri
client = MongoClient(mongo_uri)
db = client[config.DB_NAME]
users_collection = db["users"]
artists_collection = db["artists"]