from flask import Flask, request, jsonify, render_template
from models import db, Product
import os

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products]), 200

@app.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    p = Product.query.get(id)
    if not p:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(p.to_dict()), 200

@app.route("/products", methods=["POST"])
def create_product():
    data = request.get_json()
    if not data or "name" not in data or "sku" not in data or "price" not in data:
        return jsonify({"error": "Invalid data"}), 400
    product = Product(
        name=data["name"],
        sku=data["sku"],
        price=data["price"],
        stock=data.get("stock", 0)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201

@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    data = request.get_json()
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    product.name = data.get("name", product.name)
    product.sku = data.get("sku", product.sku)
    product.price = data.get("price", product.price)
    product.stock = data.get("stock", product.stock)
    db.session.commit()
    return jsonify(product.to_dict()), 200

@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

