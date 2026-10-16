import sys
import os
from pathlib import Path
from dotenv import load_dotenv

import pytest
from sqlalchemy import create_engine, text

# Load .env.test automatically before importing any modules
env_file = Path(__file__).parent.parent / ".env.test"
load_dotenv(env_file, override=True)

# Add parent directory to Python path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# ========== DATABASE FIXTURES ==========


@pytest.fixture
def database_url():
    """Fixture that returns database URL from environment variables with SQLite fallback"""
    return os.getenv("DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture
def check_interval():
    """Fixture that returns check interval in minutes from environment variables"""
    return int(os.getenv("CHECK_INTERVAL_MINUTES", "1"))


# ========== DATABASE SCHEMA ==========

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        current_price REAL NOT NULL,
        target_price REAL NOT NULL
    )
    """,
    """
    CREATE TABLE price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        price REAL NOT NULL,
        checked_at TIMESTAMP NOT NULL
    )
    """,
]


# ========== ENGINE FIXTURES ==========


@pytest.fixture
def engine(database_url):
    """Fixture that creates a test database engine with schema initialized"""
    eng = create_engine(database_url)

    # Create all tables
    with eng.begin() as conn:
        for stmt in SCHEMA_STATEMENTS:
            conn.execute(text(stmt))

    # Cleanup after test
    yield eng
    eng.dispose()


@pytest.fixture
def seeded_engine(engine):
    """Fixture that creates engine with sample test data (2 products)"""
    with engine.begin() as conn:
        # Insert test product 1: Widget (current: 100, target: 80)
        conn.execute(
            text(
                "INSERT INTO products (id, name, current_price, target_price) "
                "VALUES (:id, :name, :cp, :tp)"
            ),
            {"id": 1, "name": "Widget", "cp": 100.0, "tp": 80.0},
        )

        # Insert test product 2: Gadget (current: 50, target: 60)
        conn.execute(
            text(
                "INSERT INTO products (id, name, current_price, target_price) "
                "VALUES (:id, :name, :cp, :tp)"
            ),
            {"id": 2, "name": "Gadget", "cp": 50.0, "tp": 60.0},
        )

    return engine
