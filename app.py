from flask import Flask, jsonify, render_template, request, url_for, flash, redirect
from pymongo import MongoClient
from data_generator import *
from config import *
from werkzeug.exceptions import abort


app = Flask(__name__)

# MongoDB configuration
mongo_uri = f"mongodb+srv://{DB_USER}:{DB_PASS}@lastfmclone.8ogsa.mongodb.net/"  # Replace with your MongoDB URI if hosted
client = MongoClient(mongo_uri)
db = client["LastfmClone"]  # Database name
collection = db["artists"]  # Collection name

# Route to insert fake data
@app.route('/populate', methods=['GET'])
def populate_data():
    # # Create fake data
    spotify_data = generate_spotify_data()
    
    # Insert data into MongoDB
    try:
        result = collection.insert_many(spotify_data)
        return jsonify(f"Inserted {len(result.inserted_ids)} documents into MongoDB!")
    except Exception as e:
        return jsonify(f"Error inserting data: {e}")

# Route to retrieve data
@app.route('/artists', methods=['GET'])
def get_users():
    artists = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's default `_id` field
    return jsonify(artists)

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        artist_name = request.form['artist-name']
        artist_description = request.form['artist-description']

        if not artist_name:
            flash('Artist name is required!')
        else:
            artist = {
            "name": artist_name,
            "desription": artist_description,
            }
            result = collection.insert_one(artist)
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/dropdatabase', methods=['GET'])
def dropdb():
    data = []
    artists = list(collection.find({}, {"_id": 0}))
    for _ in artists:
        data.append(_)
        
    collection.delete_many(data)


