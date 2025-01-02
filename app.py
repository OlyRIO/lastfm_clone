from flask import Flask, jsonify, render_template, request, url_for, flash, redirect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from data_generator import *
import config
from werkzeug.exceptions import abort


app = Flask(__name__)
app.secret_key = config.secret_key

# MongoDB configuration
mongo_uri = f"mongodb+srv://{config.DB_USER}:{config.DB_PASS}@lastfmclone.8ogsa.mongodb.net/"  # Replace with your MongoDB URI if hosted
client = MongoClient(mongo_uri)
db = client["LastfmClone"]  # Database name
artist_collection = db["artists"]  # Collection name
users_collection = db["users"]

# setup bcrypt for password encription
bcrypt = Bcrypt(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        user_data = users_collection.find_one({"_id": user_id})
        if user_data:
            return User(str(user_data["_id"]), user_data["username"])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirmed_password = request.form["repeat-password"]

        if username == "":
            flash("Please enter a username.", "danger")
            return redirect(url_for("register"))
        
        if users_collection.find_one({"username": username}):
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))
        
        if (password == ""):
            flash("Please enter a password.", "danger")
            return redirect(url_for("register"))
        
        if (confirmed_password == ""):
            flash("Please confirm the password.", "danger")
            return redirect(url_for("register"))
        
        if (password != confirmed_password):
            flash("Passwords must match!", "danger")
            return redirect(url_for("register"))
        
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        users_collection.insert_one({"username": username, "password": hashed_password})
        flash("Registration successful!", "success")
        
        return redirect(url_for("login"))
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if (username == "" or password == ""):
            flash("Please enter credentials.", "danger")
            return redirect(url_for("login"))
        
        user_data = users_collection.find_one({"username": username})
        
        if user_data and bcrypt.check_password_hash(user_data["password"], password):
            user = User(str(user_data["_id"]), user_data["username"])
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("User not found!", "danger")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return f"Welcome {current_user.username}! <a href='/logout'>Logout</a>"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", "info")
    return redirect(url_for("login"))

# Route to insert fake data
@app.route('/populate', methods=['GET'])
def populate_data():
    # # Create fake data
    spotify_data = generate_spotify_data()
    
    # Insert data into MongoDB
    try:
        result = artist_collection.insert_many(spotify_data)
        flash(f"Inserted {len(result.inserted_ids)} documents into MongoDB!")
    except Exception as e:
        flash(f"Error inserting data: {e}")
        
    message = request.args.get("msg")
    
    return render_template('index.html')

# Route to retrieve data
@app.route('/artists', methods=['GET'])
def get_users():
    artists = list(artist_collection.find({}, {"_id": 0}))  # Exclude MongoDB's default `_id` field
    return jsonify(artists)

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
            result = artist_collection.insert_one(artist)
            return redirect(url_for('index.html'))

    return render_template('create.html')


@app.route('/dropdatabase', methods=['GET'])
def dropdb():
    artist_collection.delete_many({})
    
    flash("Deleted all documents of type artist.")
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)


