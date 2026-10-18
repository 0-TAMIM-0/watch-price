from unittest.mock import MagicMock, ANY
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, text

from worker import CHECK_INTERVAL_MINUTES, DATABASE_URL, create_db_engine, fetch_products, update_price, check_prices, Product, main


class TestCreateDBEngine:
    """Test suite for create_db_engine function"""

    def test_create_db_engine_returns_engine_with_default_url(self):
        """Verify that create_db_engine returns a valid Engine object using default DATABASE_URL"""
        created_engine = create_db_engine()

        assert isinstance(created_engine, Engine), "Expected Engine instance"
        created_engine.dispose()

    def test_create_db_engine_accepts_env_url(self):
        """Verify that create_db_engine accepts database URL from environment variables"""
        created_engine = create_db_engine(DATABASE_URL)

        assert isinstance(created_engine, Engine), "Expected Engine instance from env URL"

    def test_create_db_engine_accepts_custom_url(self):
        """Verify that create_db_engine accepts and uses a custom database URL"""
        created_engine = create_db_engine("sqlite:///test.db")

        assert isinstance(created_engine, Engine), "Expected Engine instance from custom URL"
        created_engine.dispose()


class TestFetchProducts:
    """Test suite for fetch_products function"""

    def test_fetch_products_returns_empty_list_when_no_data(self, engine):
        """Verify that fetch_products returns an empty list when products table is empty"""
        products = fetch_products(engine)

        assert products == [], "Expected empty list when no products in database"

    def test_fetch_products_returns_all_products(self, seeded_engine):
        """Verify that fetch_products retrieves all Product records from database"""
        products = fetch_products(seeded_engine)

        # Verify correct number of products were returned
        assert len(products) == 2, "Expected exactly 2 products from seeded database"

        # Verify all returned items are Product instances
        assert all(isinstance(p, Product) for p in products), "All items should be Product objects"

        # Verify product names match expected values
        product_names = {p.name for p in products}
        assert product_names == {"Widget", "Gadget"}, "Product names should match seeded data"


class TestUpdatePrice:
    """Test suite for update_price function"""

    def test_update_price_updates_current_price(self, seeded_engine):
        """Verify that update_price modifies the current_price in products table"""
        update_price(seeded_engine, product_id=1, new_price=90.0)

        # Fetch the updated product
        products = fetch_products(seeded_engine)
        updated = next((p for p in products if p.id == 1), None)

        assert updated is not None, "Product with id=1 not found"
        assert updated.current_price == 90.0

    def test_update_price_records_history(self, seeded_engine):
        """Verify that update_price inserts a new row in price_history table"""
        update_price(seeded_engine, product_id=1, new_price=90.0)

        # Query price_history table
        with seeded_engine.connect() as conn:
            rows = conn.execute(
                text("SELECT * FROM price_history WHERE product_id = 1")
            ).mappings().all()

        assert len(rows) == 1, "Expected exactly 1 history record"
        assert rows[0]["price"] == 90.0
        assert rows[0]["checked_at"] is not None


class TestCheckPrices:
    """Test suite for check_prices function"""

    def test_check_prices_updates_all_products(self, seeded_engine, monkeypatch):
        """Verify that check_prices updates current_price for all products"""
        # Mock simulate_price_change to return predictable values
        monkeypatch.setattr("worker.simulate_price_change", lambda price: price - 10)

        check_prices(seeded_engine)

        # Verify prices were updated
        products = fetch_products(seeded_engine)
        prices = {p.id: p.current_price for p in products}

        assert prices[1] == 90.0, "Product 1 price should be 90.0"
        assert prices[2] == 40.0, "Product 2 price should be 40.0"

    def test_check_prices_handles_fetch_failure_gracefully(self, caplog):
        """Verify that fetch errors are logged without crashing"""
        # Create engine without tables to simulate database error
        bad_engine = create_engine("sqlite:///:memory:")

        with caplog.at_level("ERROR"):
            check_prices(bad_engine)

        # Verify error was logged
        assert any("Failed to fetch products" in record.message for record in caplog.records)

    def test_check_prices_continues_after_single_product_error(self, seeded_engine, monkeypatch, caplog):
        """Verify that one product error doesn't stop processing other products"""
        # Mock simulate_price_change to fail for product id=1
        def flaky_simulate(price):
            if price == 100.0:
                raise ValueError("Price simulation failed")
            return price - 5

        monkeypatch.setattr("worker.simulate_price_change", flaky_simulate)

        with caplog.at_level("ERROR"):
            check_prices(seeded_engine)

        # Product 1 should fail
        assert any("Error processing product id=1" in record.message for record in caplog.records)

        # Product 2 should still be updated (45.0 = 50.0 - 5)
        gadget = next(p for p in fetch_products(seeded_engine) if p.id == 2)
        assert gadget.current_price == 45.0

    def test_check_prices_logs_alert_when_target_hit(self, seeded_engine, monkeypatch, caplog):
        """Verify that an alert is logged when price reaches target_price"""
        # Mock simulate_price_change to return a very low price
        monkeypatch.setattr("worker.simulate_price_change", lambda price: 10.0)

        with caplog.at_level("WARNING"):
            check_prices(seeded_engine)

        # Verify alert was logged
        assert any("ALERT" in record.message for record in caplog.records)

    def test_check_prices_no_repeat_alert_when_already_below_target(self, engine, caplog, monkeypatch):
        """No alert if the price was already below target before this cycle"""
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO products (id, name, current_price, target_price) "
                    "VALUES (1, 'Cheap', 50.0, 60.0)"
                )
            )
        monkeypatch.setattr("worker.simulate_price_change", lambda price: price - 5)

        with caplog.at_level("WARNING"):
            check_prices(engine)

        assert not any("ALERT" in record.message for record in caplog.records)

    def test_check_prices_no_alert_when_target_not_hit(self, seeded_engine, monkeypatch, caplog):
        """Verify that no alert is logged when price stays above target_price"""
        # Mock simulate_price_change to return a very high price
        monkeypatch.setattr("worker.simulate_price_change", lambda price: price + 100)

        with caplog.at_level("WARNING"):
            check_prices(seeded_engine)

        # Verify no alert was logged
        assert not any("ALERT" in record.message for record in caplog.records)


class TestMain:
    """Test suite for main function"""

    def test_main_creates_db_engine(self, monkeypatch, caplog):
        """Verify that main() creates a database engine on startup"""
        # Mock scheduler to prevent blocking
        mock_scheduler = MagicMock()
        monkeypatch.setattr("worker.BlockingScheduler", lambda: mock_scheduler)

        # Mock check_prices to prevent execution
        monkeypatch.setattr("worker.check_prices", MagicMock())

        with caplog.at_level("INFO"):
            main()

        assert "WatchPrice worker started" in caplog.text

    def test_main_schedules_check_prices_job(self, monkeypatch):
        """Verify that main() schedules check_prices to run at specified interval"""
        # Mock scheduler to capture job configuration
        mock_scheduler = MagicMock()
        monkeypatch.setattr("worker.BlockingScheduler", lambda: mock_scheduler)
        monkeypatch.setattr("worker.check_prices", MagicMock())

        main()

        # Verify add_job was called with correct parameters
        mock_scheduler.add_job.assert_called_once_with(
            ANY, "interval", minutes=CHECK_INTERVAL_MINUTES, args=[ANY]
        )

    def test_main_runs_initial_check(self, monkeypatch):
        """Verify that main() executes check_prices immediately before scheduler starts"""
        # Mock scheduler and check_prices
        mock_scheduler = MagicMock()
        mock_check = MagicMock()
        monkeypatch.setattr("worker.BlockingScheduler", lambda: mock_scheduler)
        monkeypatch.setattr("worker.check_prices", mock_check)

        main()

        # Verify check_prices was called at least once (initial check)
        assert mock_check.call_count >= 1

    def test_main_starts_scheduler(self, monkeypatch):
        """Verify that main() starts the BlockingScheduler"""
        # Mock scheduler
        mock_scheduler = MagicMock()
        monkeypatch.setattr("worker.BlockingScheduler", lambda: mock_scheduler)
        monkeypatch.setattr("worker.check_prices", MagicMock())

        main()

        # Verify scheduler.start() was called
        mock_scheduler.start.assert_called_once()

    def test_main_handles_keyboard_interrupt(self, monkeypatch, caplog):
        """Verify that main() handles KeyboardInterrupt gracefully and logs shutdown"""
        # Mock scheduler to raise KeyboardInterrupt
        mock_scheduler = MagicMock()
        mock_scheduler.start.side_effect = KeyboardInterrupt()
        monkeypatch.setattr("worker.BlockingScheduler", lambda: mock_scheduler)
        monkeypatch.setattr("worker.check_prices", MagicMock())

        with caplog.at_level("INFO"):
            main()

        assert "Worker stopped" in caplog.text

    def test_main_handles_system_exit(self, monkeypatch, caplog):
        """Verify that main() handles SystemExit gracefully and logs shutdown"""
        # Mock scheduler to raise SystemExit
        mock_scheduler = MagicMock()
        mock_scheduler.start.side_effect = SystemExit()
        monkeypatch.setattr("worker.BlockingScheduler", lambda: mock_scheduler)
        monkeypatch.setattr("worker.check_prices", MagicMock())

        with caplog.at_level("INFO"):
            main()

        assert "Worker stopped" in caplog.text
