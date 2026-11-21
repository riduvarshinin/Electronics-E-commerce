from flask import Blueprint, jsonify

from models import Order


orders_bp = Blueprint("orders", __name__)


def _order_data(order, include_details=False):
    data = {
        "id": order.id,
        "customer_name": order.customer_name,
        "product_name": ", ".join(item.product_name for item in order.items),
        "created_at": order.created_at.isoformat(),
        "subtotal": str(order.subtotal),
        "delivery_charge": str(order.delivery_charge),
        "total_amount": str(order.total_amount),
        "payment_method": order.payment.method if order.payment else "Not selected",
        "payment_status": order.payment.status if order.payment else "Awaiting payment",
        "order_status": order.status,
    }
    if include_details:
        data.update(
            email=order.email,
            phone=order.phone,
            delivery_address=order.delivery_address,
            items=[
                {
                    "product_name": item.product_name,
                    "unit_price": str(item.unit_price),
                    "quantity": item.quantity,
                    "line_total": str(item.line_total),
                }
                for item in order.items
            ],
        )
    return data


@orders_bp.get("/")
def list_orders():
    orders = Order.query.order_by(Order.created_at.desc(), Order.id.desc()).all()
    return jsonify(orders=[_order_data(order) for order in orders])


@orders_bp.get("/<int:order_id>")
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order=_order_data(order, include_details=True))
