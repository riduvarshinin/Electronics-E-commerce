
from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)

# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect("store.db")
    conn.row_factory = sqlite3.Row
    return conn

# CREATE DATABASE TABLE
def create_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    if count == 0:
        conn.executemany("""
            INSERT INTO products (name, category, price, stock)
            VALUES (?, ?, ?, ?)
        """, [
            ("Laptop", "Electronics", 45000, 10),
            ("Headphones", "Accessories", 1500, 25),
            ("Smartphone", "Electronics", 25000, 15)
        ])

    conn.commit()
    conn.close()


# DASHBOARD DESIGN
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>E-Commerce Admin Dashboard</title>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background: #f3f4f8;
    color: #333;
}

.sidebar {
    width: 230px;
    height: 100vh;
    background: #20243a;
    color: white;
    position: fixed;
    padding: 25px 15px;
}

.sidebar h2 {
    margin-bottom: 35px;
    text-align: center;
}

.sidebar a {
    display: block;
    color: white;
    text-decoration: none;
    padding: 15px;
    margin: 8px 0;
    border-radius: 7px;
}

.sidebar a:hover {
    background: #484e75;
}

.main {
    margin-left: 230px;
    padding: 30px;
}

.header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 2px 8px #ddd;
}

.card h3 {
    color: #777;
    margin-bottom: 15px;
}

.card p {
    font-size: 27px;
    font-weight: bold;
    color: #5145a8;
}

.section {
    background: white;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 25px;
}

input {
    padding: 11px;
    margin: 7px 5px 7px 0;
    border: 1px solid #ccc;
    border-radius: 5px;
}

button {
    padding: 11px 18px;
    background: #5145a8;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

button:hover {
    background: #342b80;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th, td {
    padding: 14px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    background: #f3f2fa;
}

.delete {
    background: #e74c3c;
}

.low {
    color: #e74c3c;
    font-weight: bold;
}

@media(max-width: 750px) {
    .sidebar {
        width: 150px;
    }
    .main {
        margin-left: 150px;
        padding: 15px;
    }
    .cards {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>

<div class="sidebar">
    <h2>SHOP ADMIN</h2>
    <a href="/">🏠 Dashboard</a>
    <a href="#products">📦 Products</a>
    <a href="#orders">🛒 Orders</a>
    <a href="#customers">👥 Customers</a>
</div>

<div class="main">

    <div class="header">
        <h1>Admin Dashboard</h1>
        <h3>Welcome, Admin 👋</h3>
    </div>

    <div class="cards">

        <div class="card">
            <h3>Total Products</h3>
            <p>{{ total_products }}</p>
        </div>

        <div class="card">
            <h3>Low Stock Products</h3>
            <p>{{ low_stock }}</p>
        </div>

        <div class="card">
            <h3>Total Categories</h3>
            <p>{{ categories }}</p>
        </div>

    </div>

    <div class="section" id="products">

        <h2>➕ Add New Product</h2>

        <form action="/add" method="POST">
            <input type="text" name="name"
                   placeholder="Product Name" required>

            <input type="text" name="category"
                   placeholder="Category" required>

            <input type="number" name="price"
                   placeholder="Price" min="0.01"
                   step="0.01" required>

            <input type="number" name="stock"
                   placeholder="Stock Quantity"
                   min="0" required>

            <button type="submit">Add Product</button>
        </form>

    </div>

    <div class="section">

        <h2>📦 Product Management</h2>

        <form action="/" method="GET">
            <input type="text" name="search"
                   placeholder="Search products..."
                   value="{{ search }}">

            <button type="submit">Search</button>
        </form>

        <table>
            <tr>
                <th>ID</th>
                <th>Product</th>
                <th>Category</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Action</th>
            </tr>

            {% for p in products %}
            <tr>
                <td>{{ p.id }}</td>
                <td>{{ p.name }}</td>
                <td>{{ p.category }}</td>
                <td>₹{{ "%.2f"|format(p.price) }}</td>
                <td>
                    {% if p.stock < 5 %}
                    <span class="low">{{ p.stock }} (Low)</span>
                    {% else %}
                    {{ p.stock }}
                    {% endif %}
                </td>
                <td>
                    <form action="/delete/{{ p.id }}"
                          method="POST"
                          onsubmit="return confirm('Delete this product?')">
                        <button class="delete"
                                type="submit">Delete</button>
                    </form>
                </td>
            </tr>
            {% endfor %}

        </table>

    </div>

    <div class="section" id="orders">
        <h2>🛒 Order Management</h2>
        <p>Order management module will be connected
        when the team integrates the order system.</p>
    </div>

    <div class="section" id="customers">
        <h2>👥 Customer Management</h2>
        <p>Customer management module will be connected
        when the team integrates the customer system.</p>
    </div>

</div>
</body>
</html>
"""


# HOME PAGE
@app.route("/")
def dashboard():
    conn = get_db()

    search = request.args.get("search", "")

    products = conn.execute(
        "SELECT * FROM products WHERE name LIKE ? OR category LIKE ?",
        ('%' + search + '%', '%' + search + '%')
    ).fetchall()

    total_products = conn.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    low_stock = conn.execute(
        "SELECT COUNT(*) FROM products WHERE stock < 5"
    ).fetchone()[0]

    categories = conn.execute(
        "SELECT COUNT(DISTINCT category) FROM products"
    ).fetchone()[0]

    conn.close()

    return render_template_string(
        HTML,
        products=products,
        total_products=total_products,
        low_stock=low_stock,
        categories=categories,
        search=search
    )


# ADD PRODUCT
@app.route("/add", methods=["POST"])
def add_product():
    name = request.form["name"].strip()
    category = request.form["category"].strip()
    price = float(request.form["price"])
    stock = int(request.form["stock"])

    if not name or not category or price <= 0 or stock < 0:
        return "Invalid product details", 400

    conn = get_db()

    conn.execute("""
        INSERT INTO products (name, category, price, stock)
        VALUES (?, ?, ?, ?)
    """, (name, category, price, stock))

    conn.commit()
    conn.close()

    return redirect("/")


# DELETE PRODUCT
@app.route("/delete/<int:id>", methods=["POST"])
def delete_product(id):
    conn = get_db()

    conn.execute(
        "DELETE FROM products WHERE id = ?", (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# START APPLICATION
if __name__ == "__main__":
    create_table()
    app.run(debug=True)
