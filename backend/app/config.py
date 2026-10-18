import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SECRET_KEY = os.environ["SECRET_KEY"]

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/app/uploads")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB
