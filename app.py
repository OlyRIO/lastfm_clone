from flask import Flask, jsonify, render_template
from pymongo import MongoClient
from data_generator import *
from config import *

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
@app.route('/users', methods=['GET'])
def get_users():
    artists = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's default `_id` field
    return jsonify(artists)

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/')
def index():
    return render_template('index.html')


