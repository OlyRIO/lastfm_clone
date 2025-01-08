from flask import Flask, render_template, redirect, url_for, flash, jsonify, request, session
from flask_login import LoginManager
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
        artist_name=artist.name,
        albums=artist.albums,
    )



if __name__ == "__main__":
    app.run(debug=True)
    
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',  # or 'None' for production
    SESSION_COOKIE_SECURE=False,    # False for local development (without HTTPS)
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),  # Set the session lifetime to 7 days
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST=False
)
