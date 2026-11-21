from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db

profile = Blueprint("profile", __name__)

@profile.route("/profile", methods=["GET", "POST"])
@login_required
def view_profile():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        if not username:
            flash("Name cannot be empty.", "error")
        elif len(username) > 100:
            flash("Name is too long.", "error")
        else:
            current_user.username = username
            current_user.phone = phone
            current_user.address = address
            db.session.commit()
            flash("Profile updated.", "success")
        return redirect(url_for("profile.view_profile"))
    return render_template("form.html", title="My profile", action=url_for("profile.view_profile"),
        fields=[("username", "Full name", "text", current_user.username),
                ("email_display", "Email (cannot be changed here)", "text", current_user.email),
                ("phone", "Phone", "text", current_user.phone or ""),
                ("address", "Delivery address", "textarea", current_user.address or "")],
        link_text="Back to products", link_url=url_for("products.list_products"), readonly_fields=["email_display"])
