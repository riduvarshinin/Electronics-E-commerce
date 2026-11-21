from datetime import datetime, timezone

from extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    delivery_address = db.Column(db.String(500), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_charge = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(40), nullable=False, default="Order Placed")
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    items = db.relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    payment = db.relationship(
        "Payment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    delivery = db.relationship(
        "Delivery", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_name = db.Column(db.String(160), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship("Order", back_populates="items")


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id"), nullable=False, unique=True
    )
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String(40), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    paid_at = db.Column(db.DateTime)

    order = db.relationship("Order", back_populates="payment")


class Delivery(db.Model):
    __tablename__ = "deliveries"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id"), nullable=False, unique=True
    )
    tracking_number = db.Column(db.String(32), nullable=False, unique=True)
    estimated_delivery = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(40), nullable=False, default="Order Placed")
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    order = db.relationship("Order", back_populates="delivery")
