from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g, abort
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import timedelta
from bson import ObjectId
from models.User import *

auth_blueprint = Blueprint('auth', __name__, template_folder='templates')

# Setup Flask-Login and Bcrypt
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
        
    
@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    
    if user_data:
        return User(str(user_data['_id']), user_data['username'], user_data['password'])
    return None


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
        remember_me = request.form.getlist("remember").__contains__('on')
        print(remember_me)
        
        # Check if the user exists and credentials are valid
        user_data = users_collection.find_one({"username": username})
        if user_data and bcrypt.check_password_hash(user_data["password"], password):

            user = User(str(user_data['_id']), user_data['username'], user_data['password'])
            result = login_user(user, remember=remember_me, duration=timedelta(days=7), force=True)
            

            if result:
                flash("Login successful!", "success")
                return redirect(url_for("index"))
            else:
                print("Something went wrong :(")
                
                return redirect(url_for("auth.login"))
            
            # if not helpers.url_has_allowed_host_and_scheme(next, request.host):
            #     return abort(400)
            
        else:
            flash("Invalid credentials!", "danger")
    
    return render_template("login.html")



@auth_blueprint.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()  # Logs out the current user
    flash("You have been logged out!", "info")  # Display a message
    return redirect(url_for("index"))  # Redirect to the login page

@auth_blueprint.route("/dashboard")
@login_required
def dashboard():
    return f"Welcome {current_user.username}! <a href='{url_for('auth.logout')}'>Logout</a>"

@auth_blueprint.route("/check_login")
def check_login():
    print(f'Is user authenticated in check_login function: {current_user._get_current_object().is_authenticated}')
    print(type(current_user._get_current_object()))
    if current_user._get_current_object().is_authenticated:
        return f"User {current_user.username} is logged in."
    else:
         return "No user is logged in."

