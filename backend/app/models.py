from datetime import datetime, UTC
from app import db


def utcnow() -> datetime:
    """Called on every INSERT (passed as callable, NOT evaluated at import)."""
    return datetime.now(UTC)


def to_iso_utc(dt: datetime | None) -> str | None:
    """Serialize to ISO 8601 with explicit +00:00 offset.

    SQLite (used in tests) returns naive datetimes, PostgreSQL timestamptz
    returns aware ones. We normalize both to UTC-aware.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat()


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    target_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    # One-to-Many relationship: one product has many price history records
    price_history = db.relationship(
        "PriceHistory", backref="product", lazy=True, cascade="all, delete-orphan"
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
            "created_at": to_iso_utc(self.created_at),
        }


class PriceHistory(db.Model):
    __tablename__ = "price_history"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    checked_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "price": self.price,
            "checked_at": to_iso_utc(self.checked_at),
        }
