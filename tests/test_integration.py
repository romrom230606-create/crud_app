import json
import pytest
from app import app, db
from models import Product

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_post_invalid_email(client):
    payload = {"name":"Valid Name","email":"bad","price":10,"birthDate":"2000-01-01","code":"ABCD"}
    r = client.post("/products", data=json.dumps(payload), content_type="application/json")
    assert r.status_code == 400

def test_post_duplicate_code(client):
    payload = {"name":"Prod1","email":"a@a.com","price":10,"birthDate":"2000-01-01","code":"DUP1"}
    r1 = client.post("/products", data=json.dumps(payload), content_type="application/json")
    assert r1.status_code == 201
    r2 = client.post("/products", data=json.dumps(payload), content_type="application/json")
    assert r2.status_code == 409

def test_get_delete_not_found(client):
    r = client.get("/products/9999")
    assert r.status_code == 404
    r2 = client.delete("/products/9999")
    assert r2.status_code == 404
