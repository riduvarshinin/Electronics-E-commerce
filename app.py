
import re

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from extensions import db, login_manager
from models import User


app = Flask(__name__)

# Application configuration
app.config["SECRET_KEY"] = "my_authentication_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Redirect unauthenticated users to login
login_manager.login_view = "login"
login_manager.login_message = "Please login to access your dashboard."
login_manager.login_message_category = "error"


# USER SESSION MANAGEMENT
@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


# HOME PAGE
@app.route("/")
def home():
    return render_template("home.html")


# USER REGISTRATION
@app.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validate empty fields
        if not username or not email or not password:
            flash("All fields are required!", "error")
            return redirect(url_for("register"))

        # Validate username
        if len(username) > 100:
            flash("Username must be below 100 characters.", "error")
            return redirect(url_for("register"))

        # Validate email
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.", "error")
            return redirect(url_for("register"))

        # Validate password
        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("register"))

        # Check duplicate email
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered! Please login.", "error")
            return redirect(url_for("login"))

        # Create new user
        new_user = User(
            username=username,
            email=email
        )

        # Securely hash password
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


# USER LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Check empty fields
        if not email or not password:
            flash("Please enter your email and password.", "error")
            return redirect(url_for("login"))

        # Find user by email
        user = User.query.filter_by(email=email).first()

        # Verify password
        if user and user.check_password(password):

            login_user(user)

            flash("Login successful!", "success")

            return redirect(url_for("home"))

        flash("Invalid email or password!", "error")

        return redirect(url_for("login"))

    return render_template("login.html")


# USER DASHBOARD
@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html",
        username=current_user.username,
        email=current_user.email
    )


# USER LOGOUT
@app.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash("You have logged out successfully!", "success")

    return redirect(url_for("login"))


# CREATE DATABASE AND RUN APPLICATION
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
