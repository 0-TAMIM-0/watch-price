from flask import Blueprint, jsonify, request, abort
from app import db
from app.models import Product, PriceHistory


api = Blueprint("api", __name__, url_prefix="/api")

# Separate blueprint for health checks (without /api prefix)
health_app = Blueprint("health", __name__)


# ========== Health & Readiness Checks (for Kubernetes probes) ==========

@health_app.route("/health")
def health():
    """Liveness probe: is the application running?"""
    return jsonify({"status": "ok"}), 200


@health_app.route("/ready")
def ready():
    """Readiness probe: is the application ready to accept requests? (DB connected)"""
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "ready"}), 200
    except Exception as e:
        return jsonify({"status": "not ready", "error": str(e)}), 503


# ========== Products CRUD ==========

@api.route("/products", methods=["POST"])
def add_product():
    """Add a new product to track"""
    data = request.get_json()

    if not data or "name" not in data or "current_price" not in data or "target_price" not in data:
        return jsonify({"error": "name, current_price, and target_price are required"}), 400

    product = Product(
        name=data["name"],
        category=data.get("category"),
        image_url=data.get("image_url"),
        target_price=data["target_price"],
        current_price=data["current_price"]
    )

    product.price_history.append(
        PriceHistory(price=data["current_price"])
    )
    db.session.add(product)
    db.session.commit()

    return jsonify(product.to_dict()), 201


@api.route("/products", methods=["GET"])
def get_products():
    """Get all tracked products"""
    products = Product.query.order_by(Product.created_at.desc()).all()
    return jsonify([p.to_dict() for p in products]), 200


@api.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Get product details with price history"""
    product = db.session.get(Product, product_id)

    if product is None:
        abort(404, description="Product not found")

    history = (
        PriceHistory.query
        .filter_by(product_id=product_id)
        .order_by(PriceHistory.checked_at.asc())
        .all()
    )

    result = product.to_dict()
    result["price_history"] = [h.to_dict() for h in history]

    return jsonify(result), 200


@api.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Delete a product and its price history"""
    product = db.session.get(Product, product_id)

    if product is None:
        abort(404, description="Product not found")

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200
