
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)

app.secret_key = "electromart-development-secret"

# Make current_user available in all HTML templates

class TemplateUser:

    @property
    def is_authenticated(self):
        return "user_email" in session

    @property
    def username(self):
        return session.get("username")

    @property
    def email(self):
        return session.get("user_email")


@app.context_processor
def inject_current_user():
    return {"current_user": TemplateUser()}


# Temporary user storage (for testing only)
users = {}


# HOME
@app.route("/")
def home():
    if "user_email" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# REGISTRATION
@app.route("/register", methods=["GET", "POST"])
def register():

    if "user_email" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([username, email, password, confirm_password]):
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if len(username) > 100:
            flash("Username is too long.", "error")
            return redirect(url_for("register"))

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.", "error")
            return redirect(url_for("register"))

        if email in users:
            flash("Email already registered. Please login.", "error")
            return redirect(url_for("login"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        users[email] = {
            "username": username,
            "email": email,
            "password": generate_password_hash(password)
        }

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_email" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = users.get(email)

        if user and check_password_hash(user["password"], password):

            session["user_email"] = email
            session["username"] = user["username"]

            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "user_email" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["username"],
        email=session["user_email"]
    )


# LOGOUT
@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
