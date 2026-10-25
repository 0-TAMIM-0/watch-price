"""
pytest configuration file for WatchPrice backend testing.

This file defines fixtures that are used across multiple test files.
Fixtures:
    app: Creates a Flask test application instance (session-scoped).
    client: Provides a test HTTP client for making API requests.
    db_session: Provides a database session for manual database operations in tests.
"""

import pytest
import os
import tempfile

# ========== ENVIRONMENT CONFIGURATION ==========
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["UPLOAD_FOLDER"] = tempfile.mkdtemp()

from app import create_app, db


# ========== SESSION-LEVEL FIXTURE ==========


@pytest.fixture(scope="session")
def app():
    """
    Create a Flask test application instance.

    This fixture:
    - Runs ONCE per test session (not per test)
    - Creates the Flask app with test configuration
    - Initializes SQLite in-memory database
    - Creates all tables before tests run
    - Cleans up after all tests complete
    """
    # Create Flask app instance
    app = create_app()

    # Override configuration for testing
    app.config["TESTING"] = True

    # Initialize database
    with app.app_context():
        db.create_all()

        # Yield control to tests
        yield app

        # After all tests complete: cleanup
        db.session.remove()
        db.drop_all()


# ========== TEST CLIENT FIXTURE ==========


@pytest.fixture
def client(app):
    """
    Create a test HTTP client for making API requests.

    This fixture:
    - Runs for EVERY test that requests it
    - Provides a way to make GET, POST, DELETE requests
    - Routes requests through the Flask test client (no real HTTP)
    """
    return app.test_client()


# ========== DATABASE SESSION FIXTURE ==========


@pytest.fixture
def db_session(app):
    """
    Provide a clean database session for manual database operations in tests.

    This fixture:
    - Runs for EVERY test that requests it (doesn't have scope="session")
    - Provides direct access to the database session
    - Ensures test isolation (each test starts with clean DB)
    """
    with app.app_context():  # Ensure we're in Flask app context
        yield db.session  # Provide the session to the test

        # rollback any uncommitted changes
        db.session.rollback()

        # Delete all records from all tables
        for table in reversed(db.metadata.tables.values()):
            db.session.execute(table.delete())

        db.session.commit()
