import json
import os
import pytest
from app import app, db
from models import Product


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def client():
    # Зберігаємо оригінальні значення
    original_uri = app.config['SQLALCHEMY_DATABASE_URI']
    original_testing = app.config.get('TESTING', False)
    
    # Зберігаємо та видаляємо змінні середовища
    original_env_vars = {}
    env_vars_to_remove = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASS', 'DB_NAME', 'DATABASE_URL']
    
    for var in env_vars_to_remove:
        if var in os.environ:
            original_env_vars[var] = os.environ[var]
            del os.environ[var]  # Видаляємо змінні середовища
    
    # Встановлюємо тестовий конфіг ПЕРЕД створенням контексту
    app.config['SQLALCHEMY_DATABASE_URI'] = TestConfig.SQLALCHEMY_DATABASE_URI
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Примусово переконфігуруємо базу даних
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    with app.test_client() as client:
        yield client
    
    with app.app_context():
        db.drop_all()
    
    # Повертаємо оригінальні значення
    app.config['SQLALCHEMY_DATABASE_URI'] = original_uri
    app.config['TESTING'] = original_testing
    
    # Повертаємо змінні середовища
    for var, value in original_env_vars.items():
        os.environ[var] = value


def test_post_invalid_email(client):
    payload = {"name": "Valid Name", "email": "bad", "price": 10, "birthDate": "2000-01-01", "code": "ABCD"}
    r = client.post("/products", data=json.dumps(payload), content_type="application/json")
    assert r.status_code == 400


def test_post_duplicate_code(client):
    payload = {"name": "Prod1", "email": "a@a.com", "price": 10, "birthDate": "2000-01-01", "code": "DUP1"}
    r1 = client.post("/products", data=json.dumps(payload), content_type="application/json")
    assert r1.status_code == 201
    r2 = client.post("/products", data=json.dumps(payload), content_type="application/json")
    assert r2.status_code == 409


def test_get_delete_not_found(client):
    r = client.get("/products/9999")
    assert r.status_code == 404
    r2 = client.delete("/products/9999")
    assert r2.status_code == 404