from flask import Flask, render_template, redirect, url_for, flash, jsonify, request, session
from flask_login import LoginManager
from pymongo import MongoClient
from data_generator import generate_spotify_data
import config
from auth import auth_blueprint, login_manager
from datetime import timedelta


app = Flask(__name__)
app.secret_key = config.secret_key

@app.before_request
def make_session_permanent():
    session.permanent = True

# MongoDB configuration
mongo_uri = f"mongodb+srv://{config.DB_USER}:{config.DB_PASS}@lastfmclone.8ogsa.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["LastfmClone"]
artist_collection = db["artists"]

# Register the authentication blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

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

if __name__ == "__main__":
    app.run(debug=True)
    
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',  # or 'None' for production
    SESSION_COOKIE_SECURE=False,    # False for local development (without HTTPS)
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)  # Set the session lifetime to 7 days
)
