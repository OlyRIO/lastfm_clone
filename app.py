from flask import Flask, render_template, redirect, url_for, flash, jsonify, request, session
from flask_login import LoginManager
from pymongo import MongoClient
from data_generator import generate_spotify_data
import config
from auth import auth_blueprint, login_manager
from datetime import timedelta
from search import search_bp


mongo_uri = f"mongodb+srv://{config.DB_USER}:{config.DB_PASS}@lastfmclone.8ogsa.mongodb.net/"

app = Flask(__name__)
app.secret_key = config.secret_key

# MongoDB configuration

client = MongoClient(mongo_uri)
db = client["LastfmClone"]
artist_collection = db["artists"]

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
        result = artist_collection.insert_many(spotify_data)
        flash(f"Inserted {len(result.inserted_ids)} documents into MongoDB!", "success")
    except Exception as e:
        flash(f"Error inserting data: {e}", "danger")
    return render_template('index.html')

@app.route('/artists', methods=['GET'])
def get_users():
    artists = list(artist_collection.find({}, {"_id": 0}))
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
            artist_collection.insert_one(artist)
            flash('Artist added successfully!', "success")
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/dropdatabase', methods=['GET'])
def dropdb():
    artist_collection.delete_many({})
    flash("Deleted all documents of type artist.", "info")
    return render_template('index.html')

@app.route('/song/<song_id>')
def song_detail(song_id):
    # Fetch song data (e.g., title, length, listeners) from the database
    song_data = {
        "title": "The Prodigy - Breathe",
        "listeners": "887.3K",
        "scrobbles": "6M",
        "length": "5:38",
        "lyrics": "Come play my game, I'll test ya.",
        "tags": ["electronic", "techno", "dance", "industrial", "big beat"],
        "album": "The Fat of the Land - Expanded Edition",
    }
    return render_template('song_detail.html', **song_data)

from flask import render_template

@app.route('/album/<album_id>')
def album_view(album_id):
    # Example data for testing (replace with a database query)
    album = {
        "title": "The Fat of the Land",
        "artist": "The Prodigy",
        "cover_url": "https://example.com/album-cover.jpg",
        "release_date": "1997-06-30",
        "songs": [
            {"title": "Smack My B**** Up", "duration": "5:43"},
            {"title": "Breathe", "duration": "5:39"},
            {"title": "Diesel Power", "duration": "4:17"},
        ]
    }
    return render_template(
        "album_detail.html",
        album_title=album["title"],
        artist_name=album["artist"],
        album_cover_url=album["cover_url"],
        release_date=album["release_date"],
        songs=album["songs"]
    )
    
@app.route('/artist/<artist_id>')
def artist_view(artist_id):
    # Example data for testing (replace with a database query)
    artist = {
        "name": "Sean Paul",
        "albums": [
            {
                "title": "The Trinity",
                "cover_url": "https://example.com/album-cover.jpg",
                "release_date": "1997-06-30",
                "songs": [
                    {"title": "Fire Links Intro", "duration": "5:43"},
                    {"title": "Head in the Zone", "duration": "5:39"},
                    {"title": "We Be Burnin'", "duration": "4:17"},
                ]
            },
            {
                "title": "Dutty Rock",
                "cover_url": "https://example.com/album-cover.jpg",
                "release_date": "2002-11-12",
                "songs": [
                    {"title": "Dutty Rock Intro", "duration": "5:43"},
                    {"title": "Shout (Street Respect)", "duration": "5:39"},
                    {"title": "Gimme the Light", "duration": "4:17"},
                ]
            },
        ],
        
    }
    return render_template(
        "artist_detail.html",
        artist_name=artist["name"],
        albums=artist["albums"],
    )



if __name__ == "__main__":
    app.run(debug=True)
    
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',  # or 'None' for production
    SESSION_COOKIE_SECURE=False,    # False for local development (without HTTPS)
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),  # Set the session lifetime to 7 days
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST=False
)
