from datetime import datetime, UTC
from app import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    target_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    # One-to-Many relationship: one product has many price history records
    price_history = db.relationship(
        "PriceHistory",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "image_url": self.image_url,
            "target_price": self.target_price,
            "current_price": self.current_price,
            "target_reached": self.current_price <= self.target_price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class PriceHistory(db.Model):
    __tablename__ = "price_history"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )
    price = db.Column(db.Float, nullable=False)
    checked_at = db.Column(db.DateTime, default=datetime.now(UTC))

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "price": self.price,
            "checked_at": self.checked_at.isoformat() if self.checked_at else None,
        }
