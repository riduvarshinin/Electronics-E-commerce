
from flask import Blueprint, render_template
from models import Product

products = Blueprint("products", __name__)

@products.route("/products")
def list_products():
    all_products = Product.query.all()
    return render_template(
        "products.html",
        products=all_products
    )
