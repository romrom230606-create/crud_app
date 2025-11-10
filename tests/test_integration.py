import json
import pytest
from app import app, db
from models import Person

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  
    SQLALCHEMY_TRACK_MODIFICATIONS = False

@pytest.fixture
def client():
    app.config.from_object(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all() 
        yield client
        with app.app_context():
            db.drop_all()  

def test_post_invalid_email(client):
    payload = {"first_name": "John", "last_name": "Doe", "email": "bad", "birth_date": "2000-01-01", "personal_code": "ABCD1234", "salary": 50000}
    r = client.post("/persons", data=json.dumps(payload), content_type="application/json")
    assert r.status_code == 400

def test_post_duplicate_code(client):
    payload = {"first_name": "John", "last_name": "Doe", "email": "john@example.com", "birth_date": "2000-01-01", "personal_code": "DUP1234", "salary": 50000}
    r1 = client.post("/persons", data=json.dumps(payload), content_type="application/json")
    assert r1.status_code == 201
    r2 = client.post("/persons", data=json.dumps(payload), content_type="application/json")
    assert r2.status_code == 409

def test_get_delete_not_found(client):
    r = client.get("/persons/9999")
    assert r.status_code == 404
    r2 = client.delete("/persons/9999")
    assert r2.status_code == 404