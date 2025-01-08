from db_helper import *
from bson import ObjectId

# User class for Flask-Login
class Album():
    def __init__(self, id, title, release_date, songs):
        self.id = id
        self.title = title
        self.release_date = release_date
        self.songs = songs

    @staticmethod
    def get(album_id):
        # Query to find the artist that has the album with the specified album_id
        artist_data = artists_collection.find_one(
            {"albums.id": album_id},  # Search for album_id in the albums array
            {"name": 1, "albums.$": 1}      # Project only the artist's name and the matched album
        )
        
        if artist_data:
            artist_name = artist_data["name"]
            album = artist_data["albums"][0]  # The matched album is returned as the first item in the array
            return {"artist": artist_name, "album": album}
        else:
            return None
    
    def get_id(self):
        return self.id