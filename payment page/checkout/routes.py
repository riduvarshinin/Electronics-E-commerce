import re
import secrets
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models import Delivery, Order, OrderItem, utc_now


checkout_bp = Blueprint("checkout", __name__)
DELIVERY_CHARGE = Decimal("499.00")
FREE_DELIVERY_THRESHOLD = Decimal("10000.00")
MONEY = Decimal("0.01")


def _money(value):
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount <= 0 or amount > Decimal("1000000"):
            return None
        rounded = amount.quantize(MONEY, rounding=ROUND_HALF_UP)
        return rounded if amount == rounded else None
    except (InvalidOperation, ValueError, TypeError):
        return None


@checkout_bp.post("/")
def create_order():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify(error="A JSON checkout form is required."), 400

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    phone = str(data.get("phone", "")).strip()
    address = str(data.get("address", "")).strip()
    product_name = str(data.get("product_name", "")).strip()
    price = _money(data.get("price"))
    quantity_value = data.get("quantity")

    if not 2 <= len(name) <= 120:
        return jsonify(error="Enter a name between 2 and 120 characters."), 400
    if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify(error="Enter a valid email address."), 400
    digits = re.sub(r"\D", "", phone)
    if not re.fullmatch(r"[+0-9() .-]{7,30}", phone) or not 10 <= len(digits) <= 15:
        return jsonify(error="Enter a valid phone number with 10 to 15 digits."), 400
    if not 8 <= len(address) <= 500:
        return jsonify(error="Enter a delivery address between 8 and 500 characters."), 400
    if not 2 <= len(product_name) <= 160:
        return jsonify(error="Enter a product name between 2 and 160 characters."), 400
    if price is None:
        return jsonify(error="Enter a valid product price with up to two decimal places."), 400
    if isinstance(quantity_value, bool):
        quantity = 0
    else:
        try:
            quantity = int(quantity_value)
        except (ValueError, TypeError, OverflowError):
            quantity = 0
    if str(quantity_value).strip() != str(quantity) or not 1 <= quantity <= 99:
        return jsonify(error="Quantity must be a whole number between 1 and 99."), 400

    subtotal = (price * quantity).quantize(MONEY)
    delivery_charge = (
        Decimal("0.00") if subtotal >= FREE_DELIVERY_THRESHOLD else DELIVERY_CHARGE
    )
    total = subtotal + delivery_charge
    order = Order(
        customer_name=name,
        email=email,
        phone=phone,
        delivery_address=address,
        subtotal=subtotal,
        delivery_charge=delivery_charge,
        total_amount=total,
        status="Order Placed",
        created_at=utc_now(),
    )
    order.items.append(
        OrderItem(
            product_name=product_name,
            unit_price=price,
            quantity=quantity,
            line_total=subtotal,
        )
    )
    order.delivery = Delivery(
        tracking_number=f"EM{secrets.token_hex(5).upper()}",
        estimated_delivery=date.today() + timedelta(days=5),
        status="Order Placed",
        updated_at=utc_now(),
    )

    try:
        db.session.add(order)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Could not save checkout order")
        return jsonify(error="We couldn't save your order. Please try again."), 500

    return jsonify(
        message="Your order has been placed.",
        order={
            "id": order.id,
            "customer_name": order.customer_name,
            "product_name": product_name,
            "subtotal": str(order.subtotal),
            "delivery_charge": str(order.delivery_charge),
            "total_amount": str(order.total_amount),
            "status": order.status,
        },
    ), 201
