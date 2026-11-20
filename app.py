
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
import re
import os

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "electromart-development-secret"
)


# CURRENT USER FOR HTML TEMPLATES
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


# HOME
@app.route("/")
def home():
    if "user_email" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# REGISTRATION
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        password_hash = generate_password_hash(password)

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            sql = """
                INSERT INTO users (full_name, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(sql, (
                username,
                email,
                password_hash,
                'customer'
            ))

            connection.commit()

            print("Inserted rows:", cursor.rowcount)
            print("New user ID:", cursor.lastrowid)

            flash("Registration successful!", "success")
            return redirect(url_for('login'))

        except Exception as e:
            if connection:
                connection.rollback()

            print("REGISTRATION DATABASE ERROR:", e)
            flash("Registration failed. Please try again.", "danger")

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    return render_template('register.html')

# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_email" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT user_id, full_name, email, password_hash, role
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

            if user and check_password_hash(
                user["password_hash"], password
            ):

                session.clear()
                session["user_id"] = user["user_id"]
                session["user_email"] = user["email"]
                session["username"] = user["full_name"]
                session["role"] = user["role"]

                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))

            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))

        except Exception:
            app.logger.exception("Login database error")
            flash("Login failed. Please try again.", "error")
            return redirect(url_for("login"))

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

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


@app.route("/products")
def products():

    if "user_email" not in session:
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                product_id,
                product_name,
                brand,
                description,
                price,
                stock_quantity,
                image_url
            FROM products
            ORDER BY product_id DESC
        """)

        products = cursor.fetchall()

        return render_template(
            "products.html",
            products=products
        )

    except Exception:
        app.logger.exception("Unable to load products")
        flash("Unable to load products.", "error")
        return redirect(url_for("dashboard"))

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# LOGOUT
@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
