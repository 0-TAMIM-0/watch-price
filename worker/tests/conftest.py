import sys
import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

# Set test config BEFORE importing worker/config (config reads env at import time)
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["CHECK_INTERVAL_MINUTES"] = "1"

# Add parent directory to Python path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))


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
def engine():
    """Fixture that creates a test database engine with schema initialized"""
    eng = create_engine(os.environ["DATABASE_URL"])

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
