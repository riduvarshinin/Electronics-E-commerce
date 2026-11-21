from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models import Delivery, Order, utc_now


delivery_bp = Blueprint("delivery", __name__)
DELIVERY_STATUSES = [
    "Order Placed",
    "Processing",
    "Shipped",
    "Out for Delivery",
    "Delivered",
]


def _delivery_data(delivery):
    order = delivery.order
    return {
        "order_id": order.id,
        "customer_name": order.customer_name,
        "delivery_address": order.delivery_address,
        "tracking_number": delivery.tracking_number,
        "order_date": order.created_at.isoformat(),
        "estimated_delivery": delivery.estimated_delivery.isoformat(),
        "status": delivery.status,
    }


@delivery_bp.get("/")
def list_deliveries():
    deliveries = (
        Delivery.query.join(Order)
        .order_by(Order.created_at.desc(), Order.id.desc())
        .all()
    )
    return jsonify(deliveries=[_delivery_data(delivery) for delivery in deliveries])


@delivery_bp.post("/<int:order_id>")
def update_delivery_status(order_id):
    data = request.get_json()
    if not isinstance(data, dict) or data.get("status") not in DELIVERY_STATUSES:
        return jsonify(error="Choose a valid delivery status."), 400

    delivery = Delivery.query.filter_by(order_id=order_id).first_or_404()
    new_status = data["status"]
    if DELIVERY_STATUSES.index(new_status) < DELIVERY_STATUSES.index(delivery.status):
        return jsonify(error="Delivery status cannot move backwards."), 400

    delivery.status = new_status
    delivery.updated_at = utc_now()
    delivery.order.status = new_status
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Could not update delivery status")
        return jsonify(error="Delivery status could not be updated. Please try again."), 500

    return jsonify(message="Delivery status updated.", delivery=_delivery_data(delivery))
