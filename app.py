
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_connection, create_table

app = Flask(__name__)
app.secret_key = "electronics_profile_secret_key"

create_table()


@app.route("/")
def home():
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE id = 1"
    ).fetchone()
    conn.close()

    return render_template("profile.html", user=user)


@app.route("/update", methods=["POST"])
def update_profile():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()

    if not name or not email:
        flash("Name and email are required.", "error")
        return redirect(url_for("home"))

    conn = get_connection()

    try:
        conn.execute("""
            UPDATE users
            SET name = ?, email = ?, phone = ?, address = ?
            WHERE id = 1
        """, (name, email, phone, address))

        conn.commit()
        flash("Profile updated successfully!", "success")

    except Exception:
        flash("Email already exists or could not be updated.", "error")

    finally:
        conn.close()

    return redirect(url_for("home"))


@app.route("/change-password", methods=["POST"])
def change_password():
    old_password = request.form.get("old_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    conn = get_connection()

    user = conn.execute(
        "SELECT password FROM users WHERE id = 1"
    ).fetchone()

    if not user or not check_password_hash(user["password"], old_password):
        flash("Current password is incorrect.", "error")

    elif len(new_password) < 6:
        flash("New password must contain at least 6 characters.", "error")

    elif new_password != confirm_password:
        flash("New passwords do not match.", "error")

    else:
        hashed_password = generate_password_hash(new_password)

        conn.execute(
            "UPDATE users SET password = ? WHERE id = 1",
            (hashed_password,)
        )
        conn.commit()

        flash("Password changed successfully!", "success")

    conn.close()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
