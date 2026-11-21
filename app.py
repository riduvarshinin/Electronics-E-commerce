
import os
import uuid
from decimal import Decimal, InvalidOperation

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "electromart_dev_key"

load_dotenv()

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

app.config["UPLOAD_FOLDER"] = os.path.join(
    app.static_folder, "uploads"
)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

ALLOWED_CATEGORIES = {
    "Mobiles",
    "Laptops",
    "Tablets",
    "Headphones",
    "Accessories",
    "Smart Watches",
    "Cameras",
    "Televisions"
}


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=3306,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# --------------------------------------------------
# IMAGE VALIDATION
# --------------------------------------------------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# --------------------------------------------------
# CUSTOMER HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template(
        "home.html",
        products=[],
        user_name=None,
        user_initial="G"
    )


# --------------------------------------------------
# ADMIN - ADD PRODUCT
# --------------------------------------------------

@app.route("/admin/add-product", methods=["GET", "POST"])
def add_product():

    if request.method == "GET":
        return render_template("add_product.html")

    image_path = None
    saved_image_path = None
    connection = None
    cursor = None

    try:
        # 1. RECEIVE FORM DATA

        product_name = request.form.get(
            "product_name", ""
        ).strip()

        brand = request.form.get(
            "brand", ""
        ).strip()

        model_number = request.form.get(
            "model_number", ""
        ).strip()

        category = request.form.get(
            "category", ""
        ).strip()

        description = request.form.get(
            "description", ""
        ).strip()

        original_price_text = request.form.get(
            "original_price", ""
        ).strip()

        discount_price_text = request.form.get(
            "discount_price", ""
        ).strip()

        stock_text = request.form.get(
            "stock", ""
        ).strip()

        status = request.form.get(
            "status", ""
        ).strip().capitalize()

        colour = request.form.get("colour", "").strip()
        ram = request.form.get("ram", "").strip()
        storage = request.form.get("storage", "").strip()
        processor = request.form.get("processor", "").strip()
        display_size = request.form.get("display_size", "").strip()
        battery = request.form.get("battery", "").strip()
        warranty = request.form.get("warranty", "").strip()

        # 2. REQUIRED FIELD VALIDATION

        if not all([
            product_name,
            brand,
            category,
            description,
            original_price_text,
            stock_text
        ]):
            return render_template(
                "add_product.html",
                error="Please fill in all required fields."
            ), 400

        if len(product_name) > 200:
            return render_template(
                "add_product.html",
                error="Product name must not exceed 200 characters."
            ), 400

        if len(brand) > 100:
            return render_template(
                "add_product.html",
                error="Brand must not exceed 100 characters."
            ), 400

        if category not in ALLOWED_CATEGORIES:
            return render_template(
                "add_product.html",
                error="Please select a valid product category."
            ), 400

        if status not in ["Active", "Inactive"]:
            return render_template(
                "add_product.html",
                error="Please select a valid product status."
            ), 400

        # 3. PRICE VALIDATION

        try:
            original_price = Decimal(original_price_text)

            if discount_price_text:
                discount_price = Decimal(discount_price_text)
            else:
                discount_price = original_price

            if (
                not original_price.is_finite()
                or not discount_price.is_finite()
                or original_price <= 0
                or discount_price <= 0
            ):
                raise ValueError

            if discount_price > original_price:
                return render_template(
                    "add_product.html",
                    error="Discount price cannot exceed original price."
                ), 400

            if (
                original_price.as_tuple().exponent < -2
                or discount_price.as_tuple().exponent < -2
                or original_price > Decimal("99999999.99")
                or discount_price > Decimal("99999999.99")
            ):
                raise ValueError

        except (InvalidOperation, ValueError):
            return render_template(
                "add_product.html",
                error="Please enter valid prices with up to two decimal places."
            ), 400

        # 4. STOCK VALIDATION

        try:
            stock = int(stock_text)

            if stock < 0:
                raise ValueError

        except ValueError:
            return render_template(
                "add_product.html",
                error="Stock must be a whole number greater than or equal to zero."
            ), 400

        # 5. IMAGE VALIDATION

        image = request.files.get("product_image")

        if image and image.filename:

            if not allowed_file(image.filename):
                return render_template(
                    "add_product.html",
                    error="Only JPG, JPEG and PNG images are allowed."
                ), 400

            os.makedirs(
                app.config["UPLOAD_FOLDER"],
                exist_ok=True
            )

            extension = image.filename.rsplit(".", 1)[1].lower()

            unique_filename = secure_filename(
                f"{uuid.uuid4().hex}.{extension}"
            )

            saved_image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                unique_filename
            )

            image.save(saved_image_path)

            image_path = f"uploads/{unique_filename}"

        # 6. CONNECT TO DATABASE

        connection = get_db_connection()
        cursor = connection.cursor()

        # 7. FIND CATEGORY ID

        cursor.execute(
            """
            SELECT category_id
            FROM categories
            WHERE category_name = %s
            """,
            (category,)
        )

        category_result = cursor.fetchone()

        if not category_result:
            raise ValueError(
                "Selected category was not found in the database."
            )

        category_id = category_result[0]

        # 8. INSERT PRODUCT INTO MYSQL

        sql = """
            INSERT INTO products (
                category_id,
                product_name,
                brand,
                description,
                price,
                stock_quantity,
                model_number,
                category,
                original_price,
                discount_price,
                product_status,
                colour,
                ram,
                storage,
                processor,
                display_size,
                battery,
                warranty,
                product_image_path
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        values = (
            category_id,
            product_name,
            brand,
            description,
            discount_price,
            stock,
            model_number or None,
            category,
            original_price,
            discount_price,
            status,
            colour or None,
            ram or None,
            storage or None,
            processor or None,
            display_size or None,
            battery or None,
            warranty or None,
            image_path
        )

        cursor.execute(sql, values)

        # GET GENERATED PRODUCT ID

        new_product_id = cursor.lastrowid

        # SAVE TRANSACTION

        connection.commit()

        return render_template(
            "add_product.html",
            success=(
                f"Product created successfully! "
                f"Product ID: {new_product_id}"
            )
        )

    except (mysql.connector.Error, ValueError) as error:

        if connection and connection.is_connected():
            connection.rollback()

        # Remove uploaded image if database insertion failed
        if saved_image_path and os.path.exists(saved_image_path):
            os.remove(saved_image_path)

        app.logger.exception("Product creation failed")

        return render_template(
            "add_product.html",
            error=f"Product could not be created: {error}"
        ), 400

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# --------------------------------------------------
# CUSTOMER - PRODUCT DETAILS
# --------------------------------------------------

@app.route("/product/<int:product_id>")
def product_details(product_id):

    return render_template(
        "product_details.html",
        product=None,
        product_id=product_id
    )


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
