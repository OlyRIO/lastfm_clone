from db_helper import users_collection
from flask_login import UserMixin
from bson.objectid import ObjectId

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password, liked_artists=None, liked_albums=None, liked_songs=None,
                 saved_artists=None, saved_albums=None, saved_songs=None):
        self.id = id
        self.username = username
        self.password = password
        self.liked_artists = liked_artists or []
        self.liked_albums = liked_albums or []
        self.liked_songs = liked_songs or []
        self.saved_artists = saved_artists or []
        self.saved_albums = saved_albums or []
        self.saved_songs = saved_songs or []

    @staticmethod
    def get(user_id):
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if user_data:
            return User(
                id=str(user_data["_id"]),
                username=user_data["username"],
                password=user_data["password"],
                liked_artists=user_data.get("liked_artists", []),
                liked_albums=user_data.get("liked_albums", []),
                liked_songs=user_data.get("liked_songs", []),
                saved_artists=user_data.get("saved_artists", []),
                saved_albums=user_data.get("saved_albums", []),
                saved_songs=user_data.get("saved_songs", [])
            )
        return None

    def get_id(self):
        return self.id

    def like_item(self, item_type, item_id):
        field = f"liked_{item_type}s"
        users_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$addToSet": {field: item_id}}
        )

    def save_item(self, item_type, item_id):
        field = f"saved_{item_type}s"
        users_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$addToSet": {field: item_id}}
        )

