import logging
import math
import os
import uuid

from flask import Blueprint, abort, current_app, jsonify, request, send_from_directory
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import PriceHistory, Product


logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

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
    except SQLAlchemyError:
        logger.exception("Readiness check failed")  # full details go to the logs only
        return jsonify(
            {"status": "not ready"}
        ), 503  # no internal details in the response


# ========== Image Functions ==========


def save_image(file):
    """Validate and save an uploaded image, return its URL"""
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("unsupported file type")

    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)

    # random name: never trust the client filename
    filename = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(folder, filename))

    return f"/api/uploads/{filename}"


def delete_image(image_url):
    """Delete an uploaded image file from disk (never raise)"""
    if not image_url:
        return

    filename = os.path.basename(image_url)
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    except OSError:
        logger.exception("Failed to delete image %s", path)


@api.route("/uploads/<filename>", methods=["GET"])
def get_upload(filename):
    """Serve an uploaded image"""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


def validate_product_form(data):
    """Return (values, error). error is None when valid."""
    name = (data.get("name") or "").strip()
    if not name:
        return None, "Name is required"
    if len(name) > 255:
        return None, "Name must be at most 255 characters"

    category = (data.get("category") or "").strip() or None
    if category and len(category) > 100:
        return None, "Category must be at most 100 characters"

    try:
        current_price = float(data["current_price"])
        target_price = float(data["target_price"])
    except (KeyError, ValueError):
        return None, "Prices must be numbers"

    if not (math.isfinite(current_price) and math.isfinite(target_price)):
        return None, "Prices must be finite numbers"
    if current_price <= 0 or target_price <= 0:
        return None, "Prices must be greater than 0"
    if target_price >= current_price:
        return None, "Target price must be less than current price"

    return {
        "name": name,
        "category": category,
        "current_price": current_price,
        "target_price": target_price,
    }, None


# ========== Products CRUD ==========


@api.route("/products", methods=["POST"])
def add_product():
    """Add a new product to track (multipart form)"""
    values, error = validate_product_form(request.form)
    if error:
        return jsonify({"error": error}), 400

    image_url = None
    file = request.files.get("image")
    if file and file.filename:
        try:
            image_url = save_image(file)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    product = Product(
        name=values["name"],
        category=values["category"],
        image_url=image_url,
        target_price=values["target_price"],
        current_price=values["current_price"],
    )

    product.price_history.append(PriceHistory(price=values["current_price"]))
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
        PriceHistory.query.filter_by(product_id=product_id)
        .order_by(PriceHistory.checked_at.asc())
        .all()
    )

    result = product.to_dict()
    result["price_history"] = [h.to_dict() for h in history]

    return jsonify(result), 200


@api.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Delete a product, its price history and its image"""
    product = db.session.get(Product, product_id)

    if product is None:
        abort(404, description="Product not found")

    image_url = product.image_url

    db.session.delete(product)
    db.session.commit()

    # delete the file only AFTER the DB commit succeeded
    delete_image(image_url)

    return jsonify({"message": "Product deleted"}), 200
