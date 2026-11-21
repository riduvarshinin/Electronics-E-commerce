import logging

from flask import Flask, jsonify, render_template, request
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException

from checkout import checkout_bp
from config import Config
from delivery import delivery_bp
from extensions import csrf, db
from models import Delivery, Order, Payment
from orders import orders_bp
from payment import payment_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(checkout_bp, url_prefix="/checkout")
    app.register_blueprint(payment_bp, url_prefix="/payment")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(delivery_bp, url_prefix="/delivery")

    with app.app_context():
        db.create_all()

    @app.get("/")
    def index():
        orders = Order.query.order_by(Order.created_at.desc(), Order.id.desc()).all()
        deliveries = Delivery.query.join(Order).order_by(Order.created_at.desc()).all()
        return render_template("index.html", orders=orders, deliveries=deliveries)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        return jsonify(error="Your session token expired. Refresh the page and try again."), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        if request.path.startswith(("/checkout", "/payment", "/orders", "/delivery")):
            return jsonify(error=error.description), error.code
        return error

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unexpected application error", exc_info=error)
        if request.path.startswith(("/checkout", "/payment", "/orders", "/delivery")):
            return jsonify(error="Something went wrong. Please try again."), 500
        return "Something went wrong. Please try again.", 500

    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="127.0.0.1", port=5000, debug=False)
