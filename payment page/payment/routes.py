from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models import Order, Payment, utc_now


payment_bp = Blueprint("payment", __name__)
PAYMENT_METHODS = {"Cash on Delivery", "UPI (Demo)", "Card (Demo)"}


@payment_bp.post("/")
def confirm_payment():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify(error="A JSON payment form is required."), 400

    try:
        order_id = int(data.get("order_id"))
    except (ValueError, TypeError, OverflowError):
        return jsonify(error="Select a valid order."), 400
    method = data.get("method")
    if method not in PAYMENT_METHODS:
        return jsonify(error="Choose Cash on Delivery, UPI demo, or Card demo."), 400

    order = db.session.get(Order, order_id)
    if order is None:
        return jsonify(error="That order could not be found."), 404

    now = utc_now()
    payment = order.payment
    if payment is None:
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            method=method,
            status="Pending",
            created_at=now,
        )
        db.session.add(payment)
    payment.amount = order.total_amount
    payment.method = method
    payment.status = "Pending" if method == "Cash on Delivery" else "Paid"
    payment.paid_at = now if payment.status == "Paid" else None

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Could not save payment confirmation")
        return jsonify(error="Payment confirmation could not be saved. Please try again."), 500

    message = (
        "Cash on Delivery confirmed. Payment is due when your order arrives."
        if method == "Cash on Delivery"
        else f"{method} payment simulated successfully."
    )
    return jsonify(
        message=message,
        payment={
            "order_id": order.id,
            "amount": str(payment.amount),
            "method": payment.method,
            "status": payment.status,
        },
    )
