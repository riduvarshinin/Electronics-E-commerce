
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Product, CartItem

cart = Blueprint("cart", __name__)


@cart.route("/cart")
@login_required
def view_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()

    total = sum(
        item.product.price * item.quantity
        for item in items
    )

    return render_template(
        "cart.html",
        items=items,
        total=total
    )


@cart.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    try:
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        quantity = 0

    if quantity < 1:
        flash("Invalid quantity.")
    elif quantity > product.stock:
        flash("Not enough stock available.")
    else:
        item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_id=product.id
        ).first()

        if item:
            if item.quantity + quantity > product.stock:
                flash("Requested quantity exceeds stock.")
                return redirect(url_for("cart.view_cart"))

            item.quantity += quantity
        else:
            item = CartItem(
                user_id=current_user.id,
                product_id=product.id,
                quantity=quantity
            )
            db.session.add(item)

        db.session.commit()
        flash("Product added to cart!")

    return redirect(url_for("cart.view_cart"))


@cart.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(item)
    db.session.commit()

    flash("Item removed from cart.")
    return redirect(url_for("cart.view_cart"))
