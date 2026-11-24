"""Конфигурация приложения для development, production и testing."""
import os
import secrets
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")



def _build_database_url():
    """Создаёт URL подключения к PostgreSQL."""
    url = os.getenv("DATABASE_URL")

    if url:
        return url.replace(
            "postgresql+psycopg://",
            "postgresql+psycopg2://",
            1,
        )

    password = os.getenv("DATABASE_PASSWORD")
    if not password:
        return None

    host = os.getenv("DATABASE_HOST", "localhost")
    port = os.getenv("DATABASE_PORT", "5432")
    name = os.getenv("DATABASE_NAME", "production_db")
    user = quote_plus(os.getenv("DATABASE_USER", "postgres"))
    encoded_password = quote_plus(password)

    return (
        f"postgresql+psycopg2://"
        f"{user}:{encoded_password}@{host}:{port}/{name}"
    )



class BaseConfig:
    """Общие параметры; production-секреты задаются через окружение."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 3600
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    AUTO_CREATE_DB = False

    SQLALCHEMY_DATABASE_URI = _build_database_url()
    SQLALCHEMY_POOL_SIZE = int(os.getenv("SQLALCHEMY_POOL_SIZE", "10"))
    SQLALCHEMY_MAX_OVERFLOW = int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "20"))
    SQLALCHEMY_POOL_TIMEOUT = int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "30"))
    SQLALCHEMY_POOL_RECYCLE = int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "3600"))
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"


class DevelopmentConfig(BaseConfig):
    """Локальная конфигурация с временным ключом при отсутствии .env."""

    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = True
    AUTO_CREATE_DB = True


class ProductionConfig(BaseConfig):
    """Production-конфигурация без автоматического создания таблиц."""

    DEBUG = False
    AUTO_CREATE_DB = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(BaseConfig):
    """Изолированная конфигурация для тестов."""

    TESTING = True
    SECRET_KEY = os.getenv("SECRET_KEY", "test-only-secret-key")
    AUTO_CREATE_DB = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        os.getenv("DATABASE_URL", "sqlite:///:memory:"),
    )


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(env=None):
    """Возвращает конфигурационный класс по имени окружения."""
    environment = env or os.getenv("FLASK_ENV", "development")
    return config_by_name.get(environment, DevelopmentConfig)
