from db_helper import *
from bson import ObjectId

# User class for Flask-Login
class Artist():
    def __init__(self, id, name, genre, followers, albums):
        self.id = id
        self.name = name
        self.genre = genre
        self.followers = followers
        self.albums = albums

    @staticmethod
    def get(user_id):
        artist_data = artists_collection.find_one({"id": user_id})
        print(artist_data)
        if artist_data:
            return Artist(
                artist_data["id"],
                artist_data["name"],
                artist_data["genre"],
                artist_data["followers"],
                artist_data["albums"])
        return None
    
    def get_id(self):
        return self.id