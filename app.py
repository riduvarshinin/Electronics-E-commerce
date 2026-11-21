
from flask import Flask
from extensions import db, login_manager
from models import User
from routes.cart import cart
from routes.products import products

app = Flask(__name__)

app.config["SECRET_KEY"] = "electronics-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///electronics.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager.init_app(app)
login_manager.login_view = "login"

app.register_blueprint(cart)
app.register_blueprint(products)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    return "Welcome to Electronics E-Commerce!"


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
