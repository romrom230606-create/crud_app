import os
import re
from datetime import datetime, date
from flask import Flask, request, jsonify, render_template
from models import db, Product

app = Flask(__name__)


if os.getenv('TESTING') == 'True' or os.getenv('PYTEST_CURRENT_TEST'):
   
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    print("Using SQLite for testing")
else:
    
   
    from dotenv import load_dotenv
    if os.path.exists('.env'):
        load_dotenv('.env')
    
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_NAME = os.getenv("DB_NAME", "mydb")
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"Using PostgreSQL: {DB_HOST}:{DB_PORT}/{DB_NAME}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def error_response(status, error, field_errors):
    return jsonify({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": status,
        "error": error,
        "fieldErrors": field_errors
    }), status

def validate_product_payload(data, require_all=True):
    field_errors = []
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    price = data.get("price")
    birth = data.get("birthDate") or data.get("birth_date")
    code = (data.get("code") or data.get("sku") or "").strip()

    if require_all or "name" in data:
        if len(name) < 3 or len(name) > 50:
            field_errors.append({"field":"name","code":"INVALID_LENGTH","message":"name: 3-50 characters"})
    if require_all or "email" in data:
        if email:
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                field_errors.append({"field":"email","code":"INVALID_FORMAT","message":"Invalid email"})
        else:
            field_errors.append({"field":"email","code":"REQUIRED","message":"Email is required"})
    if require_all or "price" in data:
        try:
            p = float(price)
            if p <= 0:
                field_errors.append({"field":"price","code":"INVALID_VALUE","message":"Price must be > 0"})
        except Exception:
            field_errors.append({"field":"price","code":"INVALID_FORMAT","message":"Price must be a number"})
    if require_all or "birthDate" in data or "birth_date" in data:
        if birth:
            try:
                bd = datetime.fromisoformat(birth).date()
                if bd > date.today():
                    field_errors.append({"field":"birthDate","code":"INVALID_DATE","message":"birthDate cannot be in future"})
            except Exception:
                field_errors.append({"field":"birthDate","code":"INVALID_FORMAT","message":"birthDate must be ISO date (YYYY-MM-DD)"})
        else:
            field_errors.append({"field":"birthDate","code":"REQUIRED","message":"birthDate is required"})
    if require_all or "code" in data or "sku" in data:
        if not re.match(r"^[A-Za-z0-9-]{4,20}$", code):
            field_errors.append({"field":"code","code":"INVALID_FORMAT","message":"code: 4-20 chars letters/numbers/dash"})
    return field_errors

@app.route("/")
def index():
    return render_template("index.html", today=date.today().isoformat())

@app.route("/products", methods=["GET"])
def list_products():
    products = Product.query.order_by(Product.id.desc()).all()
    return jsonify([p.to_dict() for p in products]), 200

@app.route("/products/<int:pid>", methods=["GET"])
def get_product(pid):
    p = Product.query.get(pid)
    if not p:
        return error_response(404, "Not Found", [{"field":"id","code":"NOT_FOUND","message":"Product not found"}])
    return jsonify(p.to_dict()), 200

@app.route("/products", methods=["POST"])
def create_product():
    data = request.get_json() or {}
    errors = validate_product_payload(data, require_all=True)
    if errors:
        return error_response(400, "Bad Request", errors)

    code = data.get("code") or data.get("sku")
    if Product.query.filter((Product.sku == code) | (Product.code == code)).first():
        return error_response(409, "Conflict", [{"field":"code","code":"DUPLICATE","message":"Product code already exists"}])

    p = Product(
        name=data.get("name").strip(),
        sku=code,
        code=code,
        email=data.get("email"),
        birth_date=(datetime.fromisoformat(data.get("birthDate")).date() if data.get("birthDate") else None),
        price=data.get("price"),
        stock=data.get("stock", 0)
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201

@app.route("/products/<int:pid>", methods=["PUT"])
def update_product(pid):
    p = Product.query.get(pid)
    if not p:
        return error_response(404, "Not Found", [{"field":"id","code":"NOT_FOUND","message":"Product not found"}])

    data = request.get_json() or {}
    errors = validate_product_payload(data, require_all=False)
    if errors:
        return error_response(400, "Bad Request", errors)

    if "name" in data:
        p.name = data.get("name").strip()
    if "email" in data:
        p.email = data.get("email")
    if "birthDate" in data or "birth_date" in data:
        p.birth_date = (datetime.fromisoformat(data.get("birthDate") or data.get("birth_date")).date() 
                        if (data.get("birthDate") or data.get("birth_date")) else None)
    if "price" in data:
        p.price = data.get("price")
    if "stock" in data:
        p.stock = data.get("stock")
    if "code" in data or "sku" in data:
        new_code = data.get("code") or data.get("sku")
        if Product.query.filter(((Product.sku == new_code) | (Product.code == new_code)) & (Product.id != pid)).first():
            return error_response(409, "Conflict", [{"field":"code","code":"DUPLICATE","message":"Product code already exists"}])
        p.sku = new_code
        p.code = new_code

    db.session.commit()
    return jsonify(p.to_dict()), 200

@app.route("/products/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    p = Product.query.get(pid)
    if not p:
        return error_response(404, "Not Found", [{"field":"id","code":"NOT_FOUND","message":"Product not found"}])
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message":"Deleted"}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)