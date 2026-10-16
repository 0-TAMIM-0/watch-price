import logging
from dataclasses import dataclass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from apscheduler.schedulers.blocking import BlockingScheduler

from config import DATABASE_URL, CHECK_INTERVAL_MINUTES
from price_simulator import simulate_price_change

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WORKER] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class Product:
    id: int
    name: str
    current_price: float
    target_price: float


def create_db_engine(database_url: str = DATABASE_URL) -> Engine:
    return create_engine(database_url)


def fetch_products(engine: Engine) -> list[Product]:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, name, current_price, target_price FROM products")
        ).mappings().all()
    return [Product(**row) for row in rows]


def update_price(engine: Engine, product_id: int, new_price: float) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE products SET current_price = :price WHERE id = :id"),
            {"price": new_price, "id": product_id},
        )
        conn.execute(
            text(
                """
                INSERT INTO price_history (product_id, price, checked_at)
                VALUES (:product_id, :price, CURRENT_TIMESTAMP)
                """
            ),
            {"product_id": product_id, "price": new_price},
        )


def check_prices(engine: Engine) -> None:
    logger.info("Starting price check cycle...")

    try:
        products = fetch_products(engine)
    except Exception:
        logger.exception("Failed to fetch products")
        return

    logger.info(f"Found {len(products)} product(s) to check")

    for product in products:
        try:
            new_price = simulate_price_change(product.current_price)
            update_price(engine, product.id, new_price)

            logger.info(
                f"Product '{product.name}' (id={product.id}): "
                f"{product.current_price} -> {new_price}"
            )

            if new_price <= product.target_price:
                logger.warning(
                    f"🎯 ALERT: '{product.name}' hit target price! "
                    f"Current: {new_price}, Target: {product.target_price}"
                )
        except Exception:
            logger.exception(f"Error processing product id={product.id}")

    logger.info("Price check cycle completed.")


def main() -> None:
    logger.info(
        f"WatchPrice worker started. Checking every {CHECK_INTERVAL_MINUTES} minute(s)."
    )
    engine = create_db_engine()

    scheduler = BlockingScheduler()
    scheduler.add_job(check_prices, "interval", minutes=CHECK_INTERVAL_MINUTES, args=[engine])

    check_prices(engine)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Worker stopped.")


if __name__ == "__main__":  # pragma: no cover
    main()
