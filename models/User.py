from db_helper import *
from flask_login import UserMixin


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        user_data = users_collection.find_one({"_id": user_id})
        
        if user_data:
            return User(str(user_data["_id"]), user_data["username"], user_data["password"])
        return None
    
    def get_id(self):
        return self.id