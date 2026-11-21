import os
from functools import wraps
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-secret-key-before-deployment')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'electromart_db'),
    'port': int(os.getenv('DB_PORT', '3306')),
}

PRODUCTS = [
    ('iPhone 16', 'Apple', 'Mobiles', 79900, 12, '📱', 'Powerful smartphone with an advanced camera system.'),
    ('Samsung Galaxy S24', 'Samsung', 'Mobiles', 74999, 15, '📱', 'Premium Android smartphone with vivid display.'),
    ('Dell Inspiron 14', 'Dell', 'Laptops', 62999, 8, '💻', 'Everyday laptop for study, work and entertainment.'),
    ('HP Pavilion 15', 'HP', 'Laptops', 58999, 10, '💻', 'Versatile laptop with a spacious display.'),
    ('Samsung Galaxy Tab S9', 'Samsung', 'Tablets', 45999, 7, '▣', 'Portable tablet for productivity and streaming.'),
    ('Boat Rockerz 450', 'boAt', 'Headphones', 1499, 30, '🎧', 'Wireless headphones with comfortable ear cushions.'),
    ('Apple Watch SE', 'Apple', 'Smart Watches', 24900, 9, '⌚', 'Smart watch for everyday activity and notifications.'),
    ('Canon EOS 1500D', 'Canon', 'Cameras', 34999, 5, '📷', 'DSLR camera for photography beginners.'),
    ('Samsung 43 inch Smart TV', 'Samsung', 'Televisions', 32999, 6, '📺', 'Smart television for home entertainment.'),
    ('Logitech Wireless Mouse', 'Logitech', 'Accessories', 899, 40, '🖱️', 'Reliable wireless mouse for work and study.'),
    ('Anker USB-C Hub', 'Anker', 'Accessories', 2299, 20, '🔌', 'Compact multi-port USB-C connectivity hub.'),
]


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def query(sql, params=(), one=False, commit=False):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        result = cur.fetchone() if one else cur.fetchall()
        if commit:
            conn.commit()
        return result
    finally:
        cur.close(); conn.close()


def execute(sql, params=()):
    conn = get_db(); cur = conn.cursor()
    try:
        cur.execute(sql, params); conn.commit(); return cur.lastrowid
    finally:
        cur.close(); conn.close()


def init_db():
    conn = get_db(); cur = conn.cursor()
    statements = [
        "CREATE TABLE IF NOT EXISTS em_users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(120) NOT NULL, email VARCHAR(190) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL, phone VARCHAR(30), role VARCHAR(20) NOT NULL DEFAULT 'customer', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS em_addresses (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, full_name VARCHAR(120) NOT NULL, phone VARCHAR(30) NOT NULL, line1 VARCHAR(255) NOT NULL, line2 VARCHAR(255), city VARCHAR(100) NOT NULL, state VARCHAR(100) NOT NULL, postal_code VARCHAR(20) NOT NULL, is_default TINYINT DEFAULT 0, FOREIGN KEY(user_id) REFERENCES em_users(id) ON DELETE CASCADE)",
        "CREATE TABLE IF NOT EXISTS em_products (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(180) NOT NULL, brand VARCHAR(100), category VARCHAR(100), price DECIMAL(12,2) NOT NULL, stock INT NOT NULL DEFAULT 0, emoji VARCHAR(12) DEFAULT '📦', description TEXT, image_file VARCHAR(255), active TINYINT DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS em_cart_items (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, product_id INT NOT NULL, quantity INT NOT NULL DEFAULT 1, UNIQUE KEY uq_cart_user_product(user_id,product_id), FOREIGN KEY(user_id) REFERENCES em_users(id) ON DELETE CASCADE, FOREIGN KEY(product_id) REFERENCES em_products(id) ON DELETE CASCADE)",
        "CREATE TABLE IF NOT EXISTS em_orders (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, address_id INT, total DECIMAL(12,2) NOT NULL, payment_method VARCHAR(40) NOT NULL, payment_status VARCHAR(40) NOT NULL DEFAULT 'Pending', order_status VARCHAR(40) NOT NULL DEFAULT 'Placed', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES em_users(id), FOREIGN KEY(address_id) REFERENCES em_addresses(id) ON DELETE SET NULL)",
        "CREATE TABLE IF NOT EXISTS em_order_items (id INT AUTO_INCREMENT PRIMARY KEY, order_id INT NOT NULL, product_id INT, product_name VARCHAR(180) NOT NULL, price DECIMAL(12,2) NOT NULL, quantity INT NOT NULL, FOREIGN KEY(order_id) REFERENCES em_orders(id) ON DELETE CASCADE)",
        "CREATE TABLE IF NOT EXISTS em_returns (id INT AUTO_INCREMENT PRIMARY KEY, order_id INT NOT NULL, user_id INT NOT NULL, reason VARCHAR(255) NOT NULL, request_type VARCHAR(30) NOT NULL, status VARCHAR(40) DEFAULT 'Submitted', admin_note TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(order_id) REFERENCES em_orders(id), FOREIGN KEY(user_id) REFERENCES em_users(id))",
    ]
    try:
        for s in statements: cur.execute(s)
        # Add the per-product image field safely for databases created by earlier versions.
        cur.execute('SHOW COLUMNS FROM em_products LIKE %s', ('image_file',))
        if not cur.fetchone():
            cur.execute('ALTER TABLE em_products ADD COLUMN image_file VARCHAR(255) NULL AFTER description')
        cur.execute('SELECT COUNT(*) FROM em_products'); count = cur.fetchone()[0]
        if count == 0:
            # Import the user's existing product catalogue when its common columns are present.
            imported = False
            cur.execute("SHOW TABLES LIKE 'products'")
            if cur.fetchone():
                cur.execute('SHOW COLUMNS FROM products')
                cols = {row[0] for row in cur.fetchall()}
                needed = {'product_name','brand','category','price','stock_quantity'}
                if needed.issubset(cols):
                    cur.execute('SELECT product_name,brand,category,price,stock_quantity FROM products')
                    existing = cur.fetchall()
                    if existing:
                        cur.executemany('INSERT INTO em_products (name,brand,category,price,stock,emoji,description) VALUES (%s,%s,%s,%s,%s,%s,%s)', [(r[0],r[1],r[2],r[3],r[4],'📦','Imported from your existing products table.') for r in existing])
                        imported = True
            if not imported:
                cur.executemany('INSERT INTO em_products (name,brand,category,price,stock,emoji,description) VALUES (%s,%s,%s,%s,%s,%s,%s)', PRODUCTS)
        # Assign a distinct local product photo to each matching catalogue item.
        product_images = {
            'iPhone 16':'iphone-16.jpg', 'Samsung Galaxy S24':'samsung-galaxy-s24.jpg',
            'Samsung 43 inch Smart TV':'samsung-smart-tv.jpg', 'Samsung Galaxy Tab S9':'galaxy-tab-s9.jpg',
            'Apple Watch SE':'apple-watch-se.jpg', 'Dell Inspiron 14':'dell-inspiron-14.jpg',
            'HP Pavilion 15':'hp-pavilion-15.jpg', 'Boat Rockerz 450':'boat-rockerz-450.jpg',
            'Canon EOS 1500D':'canon-eos-1500d.jpg', 'Logitech Wireless Mouse':'logitech-wireless-mouse.jpg'
        }
        for product_name, image_name in product_images.items():
            cur.execute('UPDATE em_products SET image_file=%s WHERE name=%s', (image_name, product_name))
        cur.execute('SELECT id FROM em_users WHERE email=%s', (os.getenv('ADMIN_EMAIL','admin@electromart.com'),))
        if not cur.fetchone():
            cur.execute('INSERT INTO em_users(name,email,password_hash,role) VALUES(%s,%s,%s,%s)', ('Store Admin', os.getenv('ADMIN_EMAIL','admin@electromart.com'), generate_password_hash(os.getenv('ADMIN_PASSWORD','Admin@12345')), 'admin'))
        conn.commit()
    finally:
        cur.close(); conn.close()


@app.context_processor
def inject_globals():
    cart_count = 0
    if session.get('user_id'):
        try:
            r = query('SELECT COALESCE(SUM(quantity),0) AS n FROM em_cart_items WHERE user_id=%s', (session['user_id'],), one=True)
            cart_count = r['n'] if r else 0
        except Exception: pass
    return {'cart_count': cart_count, 'current_user': session.get('user_name'), 'is_admin': session.get('role') == 'admin'}


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please sign in to continue.', 'warning'); return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin': abort(403)
        return fn(*args, **kwargs)
    return wrapper


@app.route('/')
def home():
    products = query('SELECT * FROM em_products WHERE active=1 ORDER BY created_at DESC LIMIT 8')
    categories = query('SELECT DISTINCT category FROM em_products WHERE active=1 ORDER BY category')
    return render_template('home.html', products=products, categories=categories)

@app.route('/products')
def products():
    term = request.args.get('q','').strip(); category = request.args.get('category','').strip(); sort = request.args.get('sort','')
    sql = 'SELECT * FROM em_products WHERE active=1'; args=[]
    if term: sql += ' AND (name LIKE %s OR brand LIKE %s OR description LIKE %s)'; args += [f'%{term}%']*3
    if category: sql += ' AND category=%s'; args.append(category)
    sql += {'price_low':' ORDER BY price ASC','price_high':' ORDER BY price DESC','name':' ORDER BY name ASC'}.get(sort,' ORDER BY created_at DESC')
    items = query(sql,args); cats = query('SELECT DISTINCT category FROM em_products WHERE active=1 ORDER BY category')
    return render_template('products.html', products=items, categories=cats, q=term, selected_category=category, sort=sort)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    item = query('SELECT * FROM em_products WHERE id=%s AND active=1',(product_id,),one=True)
    if not item: abort(404)
    return render_template('product_detail.html', product=item)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        if not name or not email or len(password)<8:
            flash('Enter your name and email. Password must contain at least 8 characters.','danger')
        elif query('SELECT id FROM em_users WHERE email=%s',(email,),one=True): flash('An account with this email already exists.','danger')
        else:
            execute('INSERT INTO em_users(name,email,password_hash) VALUES(%s,%s,%s)',(name,email,generate_password_hash(password)))
            flash('Account created. Please sign in.','success'); return redirect(url_for('login'))
    return render_template('auth.html', mode='register')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        user=query('SELECT * FROM em_users WHERE email=%s',(email,),one=True)
        if user and check_password_hash(user['password_hash'],password):
            session.clear(); session.update(user_id=user['id'],user_name=user['name'],role=user['role'])
            flash('Welcome back!','success'); return redirect(url_for('admin_dashboard' if user['role']=='admin' else 'home'))
        flash('Invalid email or password.','danger')
    return render_template('auth.html', mode='login')

@app.post('/logout')
def logout(): session.clear(); flash('You have been signed out.','success'); return redirect(url_for('home'))

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    user=query('SELECT * FROM em_users WHERE id=%s',(session['user_id'],),one=True)
    if request.method=='POST':
        name=request.form.get('name','').strip(); phone=request.form.get('phone','').strip()
        if name:
            execute('UPDATE em_users SET name=%s,phone=%s WHERE id=%s',(name,phone,session['user_id'])); session['user_name']=name
            flash('Profile updated.','success'); return redirect(url_for('profile'))
    addresses=query('SELECT * FROM em_addresses WHERE user_id=%s ORDER BY is_default DESC,id DESC',(session['user_id'],))
    return render_template('profile.html',user=user,addresses=addresses)

@app.post('/addresses/add')
@login_required
def add_address():
    f=request.form; required=['full_name','phone','line1','city','state','postal_code']
    if any(not f.get(x,'').strip() for x in required): flash('Please complete all required address fields.','danger')
    else: execute('INSERT INTO em_addresses(user_id,full_name,phone,line1,line2,city,state,postal_code) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',(session['user_id'],f['full_name'],f['phone'],f['line1'],f.get('line2'),f['city'],f['state'],f['postal_code'])); flash('Address saved.','success')
    return redirect(url_for('profile'))

@app.post('/cart/add/<int:product_id>')
@login_required
def cart_add(product_id):
    p=query('SELECT * FROM em_products WHERE id=%s AND active=1',(product_id,),one=True)
    if not p: abort(404)
    if p['stock']<1: flash('This product is out of stock.','danger')
    else:
        execute('INSERT INTO em_cart_items(user_id,product_id,quantity) VALUES(%s,%s,1) ON DUPLICATE KEY UPDATE quantity=LEAST(quantity+1,%s)',(session['user_id'],product_id,p['stock']))
        flash('Added to your cart.','success')
    return redirect(request.referrer or url_for('products'))

@app.route('/cart')
@login_required
def cart():
    items=query('SELECT c.id AS cart_id,c.quantity,p.* FROM em_cart_items c JOIN em_products p ON p.id=c.product_id WHERE c.user_id=%s',(session['user_id'],))
    total=sum((Decimal(str(i['price']))*i['quantity'] for i in items),Decimal('0'))
    return render_template('cart.html',items=items,total=total)

@app.post('/cart/update/<int:cart_id>')
@login_required
def cart_update(cart_id):
    qty=max(1,min(int(request.form.get('quantity',1)),99))
    execute('UPDATE em_cart_items c JOIN em_products p ON p.id=c.product_id SET c.quantity=LEAST(%s,p.stock) WHERE c.id=%s AND c.user_id=%s',(qty,cart_id,session['user_id']))
    return redirect(url_for('cart'))

@app.post('/cart/remove/<int:cart_id>')
@login_required
def cart_remove(cart_id):
    execute('DELETE FROM em_cart_items WHERE id=%s AND user_id=%s',(cart_id,session['user_id'])); flash('Item removed.','success'); return redirect(url_for('cart'))

@app.route('/checkout',methods=['GET','POST'])
@login_required
def checkout():
    items=query('SELECT c.quantity,p.* FROM em_cart_items c JOIN em_products p ON p.id=c.product_id WHERE c.user_id=%s',(session['user_id'],))
    if not items: flash('Your cart is empty.','warning'); return redirect(url_for('products'))
    addresses=query('SELECT * FROM em_addresses WHERE user_id=%s',(session['user_id'],))
    total=sum((Decimal(str(i['price']))*i['quantity'] for i in items),Decimal('0'))
    if request.method=='POST':
        address_id=request.form.get('address_id'); method=request.form.get('payment_method','Cash on Delivery')
        address=next((a for a in addresses if str(a['id'])==str(address_id)),None)
        if not address: flash('Please add and select a delivery address.','danger')
        elif any(i['stock']<i['quantity'] for i in items): flash('One or more products no longer have enough stock.','danger')
        else:
            conn=get_db(); cur=conn.cursor()
            try:
                cur.execute('INSERT INTO em_orders(user_id,address_id,total,payment_method,payment_status,order_status) VALUES(%s,%s,%s,%s,%s,%s)',(session['user_id'],address['id'],total,method,'Pending' if method=='Cash on Delivery' else 'Demo paid','Placed'))
                oid=cur.lastrowid
                for i in items:
                    cur.execute('INSERT INTO em_order_items(order_id,product_id,product_name,price,quantity) VALUES(%s,%s,%s,%s,%s)',(oid,i['id'],i['name'],i['price'],i['quantity']))
                    cur.execute('UPDATE em_products SET stock=stock-%s WHERE id=%s',(i['quantity'],i['id']))
                cur.execute('DELETE FROM em_cart_items WHERE user_id=%s',(session['user_id'],)); conn.commit()
            except: conn.rollback(); raise
            finally: cur.close(); conn.close()
            flash('Order placed successfully! This is a demonstration checkout.','success'); return redirect(url_for('order_detail',order_id=oid))
    return render_template('checkout.html',items=items,total=total,addresses=addresses)

@app.route('/orders')
@login_required
def orders():
    data=query('SELECT * FROM em_orders WHERE user_id=%s ORDER BY created_at DESC',(session['user_id'],))
    return render_template('orders.html',orders=data)

@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order=query('SELECT o.*,a.full_name,a.phone,a.line1,a.line2,a.city,a.state,a.postal_code FROM em_orders o LEFT JOIN em_addresses a ON a.id=o.address_id WHERE o.id=%s AND o.user_id=%s',(order_id,session['user_id']),one=True)
    if not order: abort(404)
    items=query('SELECT * FROM em_order_items WHERE order_id=%s',(order_id,))
    return render_template('order_detail.html',order=order,items=items)

@app.route('/returns',methods=['GET','POST'])
@login_required
def returns():
    if request.method=='POST':
        oid=request.form.get('order_id'); reason=request.form.get('reason','').strip(); kind=request.form.get('request_type','Return')
        owned=query('SELECT id FROM em_orders WHERE id=%s AND user_id=%s',(oid,session['user_id']),one=True)
        if owned and reason: execute('INSERT INTO em_returns(order_id,user_id,reason,request_type) VALUES(%s,%s,%s,%s)',(oid,session['user_id'],reason,kind)); flash('Your request has been submitted.','success')
        else: flash('Choose one of your orders and enter a reason.','danger')
        return redirect(url_for('returns'))
    data=query('SELECT r.*,o.total FROM em_returns r JOIN em_orders o ON o.id=r.order_id WHERE r.user_id=%s ORDER BY r.created_at DESC',(session['user_id'],))
    user_orders=query("SELECT id,created_at FROM em_orders WHERE user_id=%s AND order_status NOT IN ('Cancelled') ORDER BY created_at DESC",(session['user_id'],))
    return render_template('returns.html',returns=data,orders=user_orders)

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats={
        'sales':query("SELECT COALESCE(SUM(total),0) AS n FROM em_orders WHERE order_status!='Cancelled'",one=True)['n'],
        'orders':query('SELECT COUNT(*) AS n FROM em_orders',one=True)['n'],
        'users':query("SELECT COUNT(*) AS n FROM em_users WHERE role='customer'",one=True)['n'],
        'products':query('SELECT COUNT(*) AS n FROM em_products',one=True)['n'],
        'returns':query("SELECT COUNT(*) AS n FROM em_returns WHERE status='Submitted'",one=True)['n']}
    recent=query('SELECT o.*,u.name AS customer FROM em_orders o JOIN em_users u ON u.id=o.user_id ORDER BY o.created_at DESC LIMIT 8')
    return render_template('admin.html',stats=stats,orders=recent)

@app.route('/admin/products',methods=['GET','POST'])
@login_required
@admin_required
def admin_products():
    if request.method=='POST':
        f=request.form; pid=f.get('id')
        vals=(f['name'],f.get('brand'),f.get('category'),f['price'],f['stock'],f.get('emoji') or '📦',f.get('description'))
        if pid: execute('UPDATE em_products SET name=%s,brand=%s,category=%s,price=%s,stock=%s,emoji=%s,description=%s WHERE id=%s',vals+(pid,))
        else: execute('INSERT INTO em_products(name,brand,category,price,stock,emoji,description) VALUES(%s,%s,%s,%s,%s,%s,%s)',vals)
        flash('Product saved.','success'); return redirect(url_for('admin_products'))
    data=query('SELECT * FROM em_products ORDER BY id DESC')
    edit_id=request.args.get('edit', type=int)
    editing=query('SELECT * FROM em_products WHERE id=%s',(edit_id,),one=True) if edit_id else None
    return render_template('admin_products.html',products=data,editing=editing)

@app.post('/admin/products/delete/<int:pid>')
@login_required
@admin_required
def admin_product_delete(pid):
    execute('UPDATE em_products SET active=0 WHERE id=%s',(pid,)); flash('Product hidden from the store.','success'); return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    data=query('SELECT o.*,u.name AS customer FROM em_orders o JOIN em_users u ON u.id=o.user_id ORDER BY o.created_at DESC')
    return render_template('admin_orders.html',orders=data)

@app.post('/admin/orders/<int:oid>/status')
@login_required
@admin_required
def admin_order_status(oid):
    status=request.form.get('status')
    if status in ['Placed','Processing','Shipped','Out for delivery','Delivered','Cancelled']:
        execute('UPDATE em_orders SET order_status=%s WHERE id=%s',(status,oid)); flash('Order status updated.','success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/returns')
@login_required
@admin_required
def admin_returns():
    data=query('SELECT r.*,u.name AS customer FROM em_returns r JOIN em_users u ON u.id=r.user_id ORDER BY r.created_at DESC')
    return render_template('admin_returns.html',returns=data)

@app.post('/admin/returns/<int:rid>/status')
@login_required
@admin_required
def admin_return_status(rid):
    status=request.form.get('status'); note=request.form.get('admin_note','')
    if status in ['Approved','Rejected','Completed','Submitted']:
        execute('UPDATE em_returns SET status=%s,admin_note=%s WHERE id=%s',(status,note,rid)); flash('Return request updated.','success')
    return redirect(url_for('admin_returns'))

@app.errorhandler(403)
def forbidden(e): return render_template('error.html',code=403,message='You do not have permission to view this page.'),403
@app.errorhandler(404)
def not_found(e): return render_template('error.html',code=404,message='The page or item you requested was not found.'),404

if __name__ == '__main__':
    try:
        init_db(); print('Database ready. Starting ElectroMart...')
    except Error as e:
        print('\nDATABASE CONNECTION FAILED:',e)
        print('Check MySQL is running, database exists, and .env credentials are correct.\n')
        raise
    app.run(debug=os.getenv('FLASK_DEBUG','True').lower()=='true', host='127.0.0.1', port=int(os.getenv('PORT','5000')))
