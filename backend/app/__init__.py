from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app)  # Allow Cross-Origin requests

    with app.app_context():
        # from .models import Product, PriceHistory  # Import models for SQLAlchemy
        db.create_all()  # Create tables if they don't exist

        from .routes import api, health_app  # Import blueprints

        app.register_blueprint(api)
        app.register_blueprint(health_app)

    return app
