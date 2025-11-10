import os
import re
from datetime import datetime, date
from flask import Flask, request, jsonify, render_template
from models import db, Person

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

def validate_person_payload(data, require_all=True):
    field_errors = []
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    email = (data.get("email") or "").strip()
    salary = data.get("salary")
    birth = data.get("birth_date")
    personal_code = (data.get("personal_code") or "").strip()

    if require_all or "first_name" in data:
        if len(first_name) < 2 or len(first_name) > 100:
            field_errors.append({"field":"first_name","code":"INVALID_LENGTH","message":"First name must be 2-100 characters"})
    if require_all or "last_name" in data:
        if len(last_name) < 2 or len(last_name) > 100:
            field_errors.append({"field":"last_name","code":"INVALID_LENGTH","message":"Last name must be 2-100 characters"})
    if require_all or "email" in data:
        if email:
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                field_errors.append({"field":"email","code":"INVALID_FORMAT","message":"Invalid email format"})
        else:
            field_errors.append({"field":"email","code":"REQUIRED","message":"Email is required"})
    if require_all or "salary" in data:
        if salary is not None:
            try:
                s = float(salary)
                if s < 0:
                    field_errors.append({"field":"salary","code":"INVALID_VALUE","message":"Salary must be positive"})
            except Exception:
                field_errors.append({"field":"salary","code":"INVALID_FORMAT","message":"Salary must be a number"})
    if require_all or "birth_date" in data:
        if birth:
            try:
                bd = datetime.fromisoformat(birth).date()
                if bd > date.today():
                    field_errors.append({"field":"birth_date","code":"INVALID_DATE","message":"Birth date cannot be in future"})
            except Exception:
                field_errors.append({"field":"birth_date","code":"INVALID_FORMAT","message":"Birth date must be ISO date (YYYY-MM-DD)"})
        else:
            field_errors.append({"field":"birth_date","code":"REQUIRED","message":"Birth date is required"})
    if require_all or "personal_code" in data:
        if not re.match(r"^[A-Za-z0-9-]{4,20}$", personal_code):
            field_errors.append({"field":"personal_code","code":"INVALID_FORMAT","message":"Personal code: 4-20 chars letters/numbers/dash"})
    return field_errors

@app.route("/")
def index():
    return render_template("index.html", today=date.today().isoformat())

@app.route("/persons", methods=["GET"])
def list_persons():
    persons = Person.query.order_by(Person.id.desc()).all()
    return jsonify([p.to_dict() for p in persons]), 200

@app.route("/persons/<int:pid>", methods=["GET"])
def get_person(pid):
    p = Person.query.get(pid)
    if not p:
        return error_response(404, "Not Found", [{"field":"id","code":"NOT_FOUND","message":"Person not found"}])
    return jsonify(p.to_dict()), 200

@app.route("/persons", methods=["POST"])
def create_person():
    data = request.get_json() or {}
    errors = validate_person_payload(data, require_all=True)
    if errors:
        return error_response(400, "Bad Request", errors)

    personal_code = data.get("personal_code")
    email = data.get("email")
    
    if Person.query.filter(Person.personal_code == personal_code).first():
        return error_response(409, "Conflict", [{"field":"personal_code","code":"DUPLICATE","message":"Personal code already exists"}])
    
    if Person.query.filter(Person.email == email).first():
        return error_response(409, "Conflict", [{"field":"email","code":"DUPLICATE","message":"Email already exists"}])

    p = Person(
        first_name=data.get("first_name").strip(),
        last_name=data.get("last_name").strip(),
        email=data.get("email"),
        birth_date=datetime.fromisoformat(data.get("birth_date")).date() if data.get("birth_date") else None,
        personal_code=personal_code,
        salary=data.get("salary"),
        department=data.get("department")
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201

@app.route("/persons/<int:pid>", methods=["PUT"])
def update_person(pid):
    p = Person.query.get(pid)
    if not p:
        return error_response(404, "Not Found", [{"field":"id","code":"NOT_FOUND","message":"Person not found"}])

    data = request.get_json() or {}
    errors = validate_person_payload(data, require_all=False)
    if errors:
        return error_response(400, "Bad Request", errors)

    if "first_name" in data:
        p.first_name = data.get("first_name").strip()
    if "last_name" in data:
        p.last_name = data.get("last_name").strip()
    if "email" in data:
        new_email = data.get("email")
        if Person.query.filter((Person.email == new_email) & (Person.id != pid)).first():
            return error_response(409, "Conflict", [{"field":"email","code":"DUPLICATE","message":"Email already exists"}])
        p.email = new_email
    if "birth_date" in data:
        p.birth_date = datetime.fromisoformat(data.get("birth_date")).date() if data.get("birth_date") else None
    if "salary" in data:
        p.salary = data.get("salary")
    if "department" in data:
        p.department = data.get("department")
    if "personal_code" in data:
        new_code = data.get("personal_code")
        if Person.query.filter((Person.personal_code == new_code) & (Person.id != pid)).first():
            return error_response(409, "Conflict", [{"field":"personal_code","code":"DUPLICATE","message":"Personal code already exists"}])
        p.personal_code = new_code

    db.session.commit()
    return jsonify(p.to_dict()), 200

@app.route("/persons/<int:pid>", methods=["DELETE"])
def delete_person(pid):
    p = Person.query.get(pid)
    if not p:
        return error_response(404, "Not Found", [{"field":"id","code":"NOT_FOUND","message":"Person not found"}])
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message":"Deleted"}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)