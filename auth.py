from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
import config

auth_blueprint = Blueprint('auth', __name__, template_folder='templates')

# Setup Flask-Login and Bcrypt
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

# MongoDB configuration
mongo_uri = f"mongodb+srv://{config.DB_USER}:{config.DB_PASS}@lastfmclone.8ogsa.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["LastfmClone"]
users_collection = db["users"]

# User class for Flask-Login
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

@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirmed_password = request.form["repeat-password"]

        if not username:
            flash("Please enter a username.", "danger")
            return redirect(url_for("auth.register"))
        
        if users_collection.find_one({"username": username}):
            flash("Username already exists!", "danger")
            return redirect(url_for("auth.register"))
        
        if not password:
            flash("Please enter a password.", "danger")
            return redirect(url_for("auth.register"))
        
        if not confirmed_password:
            flash("Please confirm the password.", "danger")
            return redirect(url_for("auth.register"))
        
        if password != confirmed_password:
            flash("Passwords must match!", "danger")
            return redirect(url_for("auth.register"))
        
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        users_collection.insert_one({"username": username, "password": hashed_password})
        flash("Registration successful!", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("register.html")

@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Check if the user exists and credentials are valid
        user_data = users_collection.find_one({"username": username})
        if user_data and bcrypt.check_password_hash(user_data["password"], password):
            user = User(str(user_data["_id"]), user_data["username"])
            login_user(user)
            
            # Debug: print the session contents to check if it's properly set
            print(f"Session after login: {session}")  # Inspect session object
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials!", "danger")
    
    return render_template("login.html")



@auth_blueprint.route("/logout", methods=["POST"])
@login_required
def logout():
    """Log out the user and redirect to the login page."""
    logout_user()  # Logs out the current user
    flash("You have been logged out!", "info")  # Display a message
    return redirect(url_for("auth.login"))  # Redirect to the login page

@auth_blueprint.route("/dashboard")
@login_required
def dashboard():
    return f"Welcome {current_user.username}! <a href='{url_for('auth.logout')}'>Logout</a>"



@auth_blueprint.route("/check_login")
def check_login():
    if current_user.is_authenticated:
        return f"User {current_user.username} is logged in."
    else:
        return "No user is logged in."

