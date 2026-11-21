
import os
import uuid
from decimal import Decimal, InvalidOperation

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = "electromart_dev_key"

# IMAGE UPLOAD SETTINGS
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = os.path.join(
    app.static_folder, "uploads"
)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# CUSTOMER HOME PAGE
@app.route("/")
def home():
    return render_template(
        "home.html",
        products=[],
        user_name=None,
        user_initial="G"
    )


# ADMIN - ADD PRODUCT
@app.route("/admin/add-product", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        # GET FORM DATA
        product_name = request.form.get("product_name", "").strip()
        brand = request.form.get("brand", "").strip()
        model_number = request.form.get("model_number", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "").strip().lower()

        original_price = request.form.get("original_price", "").strip()
        discount_price = request.form.get("discount_price", "").strip()
        stock = request.form.get("stock", "").strip()

        # REQUIRED FIELD VALIDATION
        required_fields = {
            "Product Name": product_name,
            "Brand": brand,
            "Model Number": model_number,
            "Category": category,
            "Description": description,
            "Original Price": original_price,
            "Discount Price": discount_price,
            "Stock": stock,
            "Status": status
        }

        for field, value in required_fields.items():
            if not value:
                return f"{field} is required.", 400

        # PRICE VALIDATION
        try:
            original_price = Decimal(original_price)
            discount_price = Decimal(discount_price)

            if original_price <= 0 or discount_price <= 0:
                return "Prices must be greater than zero.", 400

            if discount_price > original_price:
                return "Discount price cannot exceed original price.", 400

        except InvalidOperation:
            return "Please enter valid prices.", 400

        # STOCK VALIDATION
        try:
            stock = int(stock)

            if stock < 0:
                return "Stock cannot be negative.", 400

        except ValueError:
            return "Please enter a valid stock quantity.", 400

        # STATUS VALIDATION
        if status not in ["active", "inactive"]:
            return "Please select a valid product status.", 400

        # IMAGE VALIDATION
        image = request.files.get("product_image")
        image_filename = None

        if image and image.filename:

            if not allowed_file(image.filename):
                return "Only JPG, JPEG and PNG images are allowed.", 400

            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

            extension = image.filename.rsplit(".", 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{extension}"

            safe_filename = secure_filename(unique_filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    safe_filename
                )
            )

            image_filename = f"uploads/{safe_filename}"

        # DATABASE INTEGRATION WILL BE ADDED HERE
        # Product details are validated, but NOT saved to MySQL yet.

        return (
            "Product form validation successful! "
            "Image uploaded: "
            + (image_filename or "No image selected.")
            + " Product has NOT been saved to the database yet."
        )

    return render_template("add_product.html")


# CUSTOMER - PRODUCT DETAILS
@app.route("/product/<int:product_id>")
def product_details(product_id):

    return render_template(
        "product_details.html",
        product=None,
        product_id=product_id
    )


if __name__ == "__main__":
    app.run(debug=True)



