"""Configuration objects for MERVE Café.

Reads from environment variables (loaded from .env via python-dotenv).
Falls back to safe local SQLite defaults so the project runs out of the box,
while fully supporting PostgreSQL in production.
"""
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _normalize_db_url(url: str) -> str:
    # Heroku / some providers hand out postgres:// which SQLAlchemy no longer accepts.
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production-merve-2026")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY + "-jwt")
    JWT_EXPIRES = timedelta(days=int(os.environ.get("JWT_EXPIRES_DAYS", "7")))

    # Database --------------------------------------------------------------
    _db_url = _normalize_db_url(os.environ.get("DATABASE_URL", ""))
    SQLALCHEMY_DATABASE_URI = _db_url or "sqlite:///" + os.path.join(BASE_DIR, "instance", "merve.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Uploads ---------------------------------------------------------------
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB
    ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "gif"}

    # Sessions / security ---------------------------------------------------
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Brand / loyalty rules -------------------------------------------------
    LOYALTY_COFFEE_GOAL = 5          # buy 5 coffees -> 1 free
    LOYALTY_POINTS_PER_CURRENCY = 1  # 1 point per somoni spent


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
