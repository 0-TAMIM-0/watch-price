from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from .config import Config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from .models import Product, PriceHistory  # noqa: F401  (Import models for SQLAlchemy)
        db.create_all()  # Create tables if they don't exist

        from .routes import api, health_app  # Import blueprints

        app.register_blueprint(api)
        app.register_blueprint(health_app)

    @app.errorhandler(413)
    def file_too_large(_error):
        return jsonify({"error": "File too large (max 2MB)"}), 413

    return app
