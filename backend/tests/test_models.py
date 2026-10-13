import time
from datetime import datetime

from app.models import Product, PriceHistory, to_iso_utc


class TestProductModel:
    """Test suite for Product model"""

    def test_product_creation(self, db_session):
        """Test creating a product"""
        product = Product(
            name="iPhone 15 Pro",
            category="Electronics",
            image_url="https://example.com/iphone.jpg",
            target_price=800,
            current_price=999
        )

        db_session.add(product)
        db_session.commit()

        assert product.id is not None
        assert product.name == "iPhone 15 Pro"
        assert product.target_price == 800
        assert product.current_price == 999
        assert product.created_at is not None

    def test_product_to_dict(self, db_session):
        """Test converting product to dictionary"""
        product = Product(
            name="Test Product",
            category="Test",
            target_price=100,
            current_price=150
        )

        db_session.add(product)
        db_session.commit()

        product_dict = product.to_dict()

        assert isinstance(product_dict, dict)
        assert product_dict["name"] == "Test Product"
        assert product_dict["target_price"] == 100
        assert product_dict["current_price"] == 150
        assert product_dict["target_reached"] == False  # 150 > 100

    def test_product_target_reached(self, db_session):
        """Test target_reached calculation"""
        # Case 1: Price above target
        product1 = Product(
            name="Expensive Item",
            target_price=100,
            current_price=150
        )
        db_session.add(product1)
        db_session.commit()

        assert product1.to_dict()["target_reached"] == False

        # Case 2: Price equal to target
        product2 = Product(
            name="Equal Price",
            target_price=100,
            current_price=100
        )
        db_session.add(product2)
        db_session.commit()

        assert product2.to_dict()["target_reached"] == True

        # Case 3: Price below target
        product3 = Product(
            name="Cheap Item",
            target_price=100,
            current_price=50
        )
        db_session.add(product3)
        db_session.commit()

        assert product3.to_dict()["target_reached"] == True

    def test_product_cascade_delete(self, db_session):
        """Test that deleting product also deletes price history"""
        product = Product(
            name="Delete Test",
            target_price=100,
            current_price=200
        )
        db_session.add(product)
        db_session.flush()

        # Add price history
        history = PriceHistory(product_id=product.id, price=200)
        db_session.add(history)
        db_session.commit()

        product_id = product.id
        history_id = history.id

        # Delete product
        db_session.delete(product)
        db_session.commit()

        # Verify both are deleted
        assert db_session.get(Product, product_id) is None
        assert db_session.get(PriceHistory, history_id) is None

    # ---------- Regression tests: timestamps ----------

    def test_timestamps_are_evaluated_per_row(self, db_session):
        """Regression: default must be evaluated on each INSERT, not at import."""
        product1 = Product(name="A", target_price=1, current_price=2)
        db_session.add(product1)
        db_session.commit()

        time.sleep(0.01)

        product2 = Product(name="B", target_price=1, current_price=2)
        db_session.add(product2)
        db_session.commit()

        assert product2.created_at > product1.created_at

    def test_to_dict_timestamps_are_utc_aware(self, db_session):
        """created_at must be serialized with an explicit UTC offset."""
        product = Product(name="TZ", target_price=1, current_price=2)
        db_session.add(product)
        db_session.commit()

        iso = product.to_dict()["created_at"]

        assert iso.endswith("+00:00")
        assert datetime.fromisoformat(iso).tzinfo is not None


class TestPriceHistoryModel:
    """Test suite for PriceHistory model"""

    def test_price_history_creation(self, db_session):
        """Test creating a price history record"""
        product = Product(
            name="Test Product",
            target_price=100,
            current_price=200
        )
        db_session.add(product)
        db_session.flush()

        history = PriceHistory(product_id=product.id, price=199.99)
        db_session.add(history)
        db_session.commit()

        assert history.id is not None
        assert history.product_id == product.id
        assert history.price == 199.99
        assert history.checked_at is not None

    def test_price_history_to_dict(self, db_session):
        """Test converting price history to dictionary"""
        product = Product(
            name="Test",
            target_price=100,
            current_price=200
        )
        db_session.add(product)
        db_session.flush()

        history = PriceHistory(product_id=product.id, price=185.50)
        db_session.add(history)
        db_session.commit()

        history_dict = history.to_dict()

        assert isinstance(history_dict, dict)
        assert history_dict["product_id"] == product.id
        assert history_dict["price"] == 185.50
        assert "checked_at" in history_dict

    def test_price_history_relationship(self, db_session):
        """Test relationship between Product and PriceHistory"""
        product = Product(
            name="Test Relationship",
            target_price=100,
            current_price=200
        )
        db_session.add(product)
        db_session.flush()

        # Add multiple price history records
        for price in [200, 190, 180, 170]:
            history = PriceHistory(product_id=product.id, price=price)
            db_session.add(history)

        db_session.commit()

        # Verify relationship
        assert len(product.price_history) == 4
        assert product.price_history[0].price == 200
        assert product.price_history[-1].price == 170


class TestToIsoUtc:
    """Test suite for the to_iso_utc helper"""

    def test_none_returns_none(self):
        assert to_iso_utc(None) is None

    def test_naive_datetime_is_treated_as_utc(self):
        naive = datetime(2026, 10, 12, 12, 0, 0)

        assert to_iso_utc(naive) == "2026-10-12T12:00:00+00:00"

    def test_aware_datetime_is_converted_to_utc(self):
        from datetime import timezone, timedelta

        berlin = timezone(timedelta(hours=2))
        aware = datetime(2026, 10, 12, 14, 0, 0, tzinfo=berlin)

        assert to_iso_utc(aware) == "2026-10-12T12:00:00+00:00"
