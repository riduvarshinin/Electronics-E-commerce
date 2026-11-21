# ElectroMart — Electronics E-commerce Website

A single integrated Flask + MySQL academic project containing all seven requested modules.

## Modules
1. User registration, login, logout and password hashing
2. Profile editing and multiple delivery addresses
3. Product catalogue, category filter, search, sorting and admin product CRUD (add/edit/hide)
4. Shopping cart with quantity and stock checks
5. Checkout, demo payment selection, order placement and delivery-status tracking
6. Return/replacement requests and admin review
7. Admin dashboard with sales, users, products, orders and pending-return summary

## Requirements
- Python 3.10 or newer
- MySQL Server 8.0 running locally
- A MySQL database named `electromart_db`

## Run on Windows (PowerShell)

1. Open this folder in VS Code.
2. Create the database in MySQL Workbench or run:
   ```sql
   CREATE DATABASE IF NOT EXISTS electromart_db;
   ```
3. Create a virtual environment and install packages:
   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   py -m pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and enter your MySQL password in `DB_PASSWORD`.
   ```powershell
   Copy-Item .env.example .env
   ```
5. Start the app:
   ```powershell
   py app.py
   ```
6. Open `http://127.0.0.1:5000` in your browser.

The application creates its own `em_*` tables inside `electromart_db` at first launch. This prefix is intentional: it prevents the app from dropping or overwriting the existing `users`, `products`, `categories`, `cart`, `orders`, `payments`, `reviews`, `addresses`, or other project tables. If your existing `products` table has `product_name`, `brand`, `category`, `price`, and `stock_quantity` columns, the app imports those products into its integrated catalogue on first launch. Otherwise it loads sample products.

## Admin login
- Email: `admin@electromart.com`
- Password: `Admin@12345`

Change these in `.env` before first launch if desired. The admin account is created only when it does not already exist. If the admin account already exists, changing `.env` will not reset its password.

## Test the modules
- Register a customer account and sign in.
- Add a delivery address under **Profile**.
- Browse/search products and add items to cart.
- Checkout and choose Cash on Delivery or Demo Online Payment.
- Track order status under **Orders**.
- Submit a return/replacement request.
- Sign in as admin to manage products, delivery statuses and return requests.

## Important payment note
Checkout is a demonstration flow. It does not charge a card, process UPI, or store payment credentials. A real payment gateway requires merchant credentials and a verified server-side integration.

## Notes
- Do not deploy with Flask debug mode enabled.
- Replace `SECRET_KEY` with a long random value.
- Configure HTTPS and production-grade hosting before public deployment.
- This is a locally runnable project; it is not hosted on a public domain by this package.
