import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://watchprice:watchprice@localhost:5432/watchprice",
)

# Price check interval in minutes (configurable via .env)
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "10"))
