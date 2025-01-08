from db_helper import *
from bson import ObjectId
import pprint

# User class for Flask-Login
class Song():
    def __init__(self, id, title, duration, popularity):
        self.id = id
        self.title = title
        self.duration = duration
        self.popularity = popularity

    @staticmethod
    def get(song_id):
        song_data_cursor = artists_collection.aggregate([
            {"$match": {"albums.songs.id": song_id}},  # Match documents containing the song ID
            {"$unwind": "$albums"},                   # Deconstruct the albums array
            {"$unwind": "$albums.songs"},             # Deconstruct the songs array within albums
            {"$match": {"albums.songs.id": song_id}}, # Match the specific song ID
            {
                "$project": {
                    "name": 1,                        # Include the artist's name
                    "album_title": "$albums.title",   # Include the title of the album
                    "song": "$albums.songs"           # Include the matched song details
                }
            }
        ])

        for song_data in song_data_cursor:
            artist_name = song_data["name"]
            album_title = song_data["album_title"]
            song_details = song_data["song"]

            return {"artist": artist_name, "album": album_title, "song": song_details}
    
    def get_id(self):
        return self.id