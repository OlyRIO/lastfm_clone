from db_helper import *

# User class for Flask-Login
class Song():
    def __init__(self, id, title, duration, popularity):
        self.id = id
        self.title = title
        self.duration = duration
        self.popularity = popularity

    @staticmethod
    def find_song(song_id):
        # Query to find the artist that has the album with the specified album_id
        song_data = users_collection.find_one(
            {"albums.songs.song_id": song_id},  # Search for song_id in the songs array within albums
            {"name": 1, "albums.album_name": 1, "albums.songs.$": 1}    # Project the user's name and the matched song in the album
        )

        
        if song_data:
            artist_name = song_data["name"]
            album_name = song_data["albums.album_name"]  # The matched album is returned as the first item in the array
            song = song_data["albums.songs"][0]
            return {"artist": artist_name, "album": album_name, "song": song}
        else:
            return None
    
    def get_id(self):
        return self.id