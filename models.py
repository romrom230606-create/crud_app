from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), nullable=False, unique=True)  # legacy field name kept
    code = db.Column(db.String(100), nullable=True)  # optional alias
    email = db.Column(db.String(255), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    price = db.Column(db.Numeric(10,2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "code": self.code,
            "email": self.email,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "price": float(self.price),
            "stock": self.stock,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
