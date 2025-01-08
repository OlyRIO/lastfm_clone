from flask import Blueprint, request, render_template
from pymongo import MongoClient
import config 
import pprint

search_bp = Blueprint('search', __name__, template_folder='templates')

mongo_uri = config.mongo_uri
client = MongoClient(mongo_uri)
db = client[config.DB_NAME]

@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    
    # Uzmi parametre za sortiranje iz URL-a, ako nisu prisutni, zadano je 'asc'
    sort_artists = request.args.get('sort_artists', 'asc')
    sort_albums = request.args.get('sort_albums', 'asc')
    sort_songs = request.args.get('sort_songs', 'asc')
    
    # Pretvori "asc" u 1, a "desc" u -1 za MongoDB sortiranje
    sort_artists = 1 if sort_artists == 'asc' else -1
    sort_albums = 1 if sort_albums == 'asc' else -1
    sort_songs = 1 if sort_songs == 'asc' else -1

    if not query:
        return render_template('search.html', artists=[], albums=[], songs=[], query=query, 
                               sort_artists=sort_artists, sort_albums=sort_albums, sort_songs=sort_songs)

    # Sortiranje umjetnika
    artist_results = list(db.artists.find({"name": {"$regex": query, "$options": "i"}}).sort("name", sort_artists))

    # Sortiranje albuma
    album_results = list(db.artists.aggregate([
    {"$unwind": "$albums"},
    {"$match": {"albums.title": {"$regex": query, "$options": "i"}}},
    {"$sort": {"albums.title": sort_albums}},
    {"$project": {
        "_id": 0,
        "artist_name": "$name",
        "album": {
            "id": "$albums.id",  # Explicitly include `id`
            "title": "$albums.title",
            "release_date": "$albums.release_date"
            }
        }}
    ]))


    # Sortiranje pjesama
    song_results = list(db.artists.aggregate([
    {"$unwind": "$albums"},
    {"$unwind": "$albums.songs"},
    {"$match": {"albums.songs.title": {"$regex": query, "$options": "i"}}},
    {"$sort": {"albums.songs.title": sort_songs}},
    {"$project": {
        "_id": 0,
        "artist_name": "$name",
        "album_title": "$albums.title",
        "song": {
            "id": "$albums.songs.id",  # Explicitly include `id` here
            "title": "$albums.songs.title",
            "duration": "$albums.songs.duration"
            }
        }}
    ]))

    pprint.pp(album_results)
    pprint.pp(song_results)
    
    return render_template(
        'search.html',
        artists=artist_results,
        albums=album_results,
        songs=song_results,
        query=query,
        sort_artists=sort_artists,
        sort_albums=sort_albums,
        sort_songs=sort_songs
    )
