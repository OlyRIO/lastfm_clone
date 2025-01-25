from flask import Flask, render_template, redirect, url_for, flash, jsonify, request, session
from flask_login import LoginManager, login_required, current_user
from db_helper import *
from data_generator import generate_spotify_data
import config
from auth import auth_blueprint, login_manager
from datetime import timedelta
from search import search_bp
from bson import ObjectId
from models.Artist import Artist
from models.Album import Album
from models.Song import Song
from models.User import User


mongo_uri = f"mongodb+srv://{config.DB_USER}:{config.DB_PASS}@lastfmclone.8ogsa.mongodb.net/"

app = Flask(__name__)
app.secret_key = config.secret_key

# Register the authentication blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

app.register_blueprint(search_bp)

# Initialize Flask-Login
login_manager.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/populate', methods=['GET'])
def populate_data():
    spotify_data = generate_spotify_data()
    try:
        result = artists_collection.insert_many(spotify_data)
        flash(f"Inserted {len(result.inserted_ids)} documents into MongoDB!", "success")
    except Exception as e:
        flash(f"Error inserting data: {e}", "danger")
    return render_template('index.html')

@app.route('/artists', methods=['GET'])
def get_users():
    artists = list(artists_collection.find({}, {"_id": 0}))
    return jsonify(artists)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        artist_name = request.form['artist-name']
        artist_description = request.form['artist-description']
        if not artist_name:
            flash('Artist name is required!', "danger")
        else:
            artist = {"name": artist_name, "description": artist_description}
            artists_collection.insert_one(artist)
            flash('Artist added successfully!', "success")
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/dropdatabase', methods=['GET'])
def dropdb():
    artists_collection.delete_many({})
    flash("Deleted all documents of type artist.", "info")
    return render_template('index.html')

@app.route('/song/<song_id>')
def song_detail(song_id):
    
    song_data = Song.get(song_id)
    song = song_data["song"]
    
    return render_template('song_detail.html', 
                           song=song,
                           artist = song_data["artist"],
                           album = song_data["album"],
                           scrobbles = song["scrobbles"],
                           duration = song["duration"],
                        
                           )

from flask import render_template

@app.route('/album/<album_id>')
def album_view(album_id):
    # Example data for testing (replace with a database query)
    album_data = Album.get(album_id)
    album = album_data["album"]

    return render_template(
        "album_detail.html",
        album=album,
        album_title=album["title"],
        artist_name= album_data["artist"],
        release_date=album["release_date"],
        songs=album["songs"]
    )
    
@app.route('/artist/<artist_id>')
def artist_view(artist_id):
    # Example data for testing (replace with a database query)
    artist = Artist.get(artist_id)
    
    return render_template(
        "artist_detail.html",
        artist=artist,
        artist_name=artist.name,
        albums=artist.albums,
    )

@app.route('/like/<item_type>/<item_id>', methods=['POST'])
@login_required
def like_item(item_type, item_id):
    current_user.like_item(item_type, item_id)
    return jsonify({"message": f"Successfully liked {item_type} with ID {item_id}"}), 200

@app.route('/save/<item_type>/<item_id>', methods=['POST'])
@login_required
def save_item(item_type, item_id):
    current_user.save_item(item_type, item_id)
    return jsonify({"message": f"Successfully saved {item_type} with ID {item_id}"}), 200

@app.route('/profile')
@login_required
def profile_view():
    # Fetch user and their liked/saved items
    user = User.get(current_user.id)
    
    # Initialize empty lists to hold detailed data
    liked_songs_details = []
    saved_songs_details = []
    liked_albums_details = []
    saved_albums_details = []
    liked_artists_details = []
    saved_artists_details = []

    # Fetch detailed information for liked songs
    for song_id in user.liked_songs:
        song_details = Song.get(song_id)
        if song_details:  # Only append if the song exists
            liked_songs_details.append(song_details)

    # Fetch detailed information for saved songs
    for song_id in user.saved_songs:
        song_details = Song.get(song_id)
        if song_details:  # Only append if the song exists
            saved_songs_details.append(song_details)

    # Fetch detailed information for liked albums
    for album_id in user.liked_albums:
        album_details = Album.get(album_id)
        if album_details:  # Only append if the album exists
            liked_albums_details.append(album_details)

    # Fetch detailed information for saved albums
    for album_id in user.saved_albums:
        album_details = Album.get(album_id)
        if album_details:  # Only append if the album exists
            saved_albums_details.append(album_details)

    # Fetch detailed information for liked artists
    for artist_id in user.liked_artists:
        artist_details = Artist.get(artist_id)
        if artist_details:  # Only append if the artist exists
            liked_artists_details.append(artist_details)

    # Fetch detailed information for saved artists
    for artist_id in user.saved_artists:
        artist_details = Artist.get(artist_id)
        if artist_details:  # Only append if the artist exists
            saved_artists_details.append(artist_details)

    # Debugging output
    print(f"Liked Songs Details: {liked_songs_details}")
    print(f"Saved Songs Details: {saved_songs_details}")
    print(f"Liked Albums Details: {liked_albums_details}")
    print(f"Saved Albums Details: {saved_albums_details}")
    print(f"Liked Artists Details: {liked_artists_details}")
    print(f"Saved Artists Details: {saved_artists_details}")
    print(f"Current user ID: {user.id}")
    print(f"Current user username: {current_user.username}")

    # Render profile.html with detailed data
    return render_template(
        "profile.html",
        username=current_user.username,
        liked_songs=liked_songs_details,  # Pass detailed liked songs
        saved_songs=saved_songs_details,  # Pass detailed saved songs
        liked_albums=liked_albums_details,  # Pass detailed liked albums
        saved_albums=saved_albums_details,  # Pass detailed saved albums
        liked_artists=liked_artists_details,  # Pass detailed liked artists
        saved_artists=saved_artists_details,  # Pass detailed saved artists
    )




    


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
    
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',  # or 'None' for production
    SESSION_COOKIE_SECURE=False,    # False for local development (without HTTPS)
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),  # Set the session lifetime to 7 days
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST=False
)
