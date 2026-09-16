"""
Конфигурация приложения.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv(Path(__file__).parent.parent / ".env")

# Корневая директория проекта
BASE_DIR = Path(__file__).parent.parent


def _build_database_url():
    """Сборка DATABASE_URL из переменных окружения."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    host = os.getenv("DATABASE_HOST", "localhost")
    port = os.getenv("DATABASE_PORT", "5432")
    name = os.getenv("DATABASE_NAME", "production_db")
    user = os.getenv("DATABASE_USER", "postgres")
    password = os.getenv("DATABASE_PASSWORD", "12345")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


class BaseConfig:
    """Базовая конфигурация."""
    SECRET_KEY = os.getenv("SECRET_KEY", "production-is-system-secret-key-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 3600

    SQLALCHEMY_DATABASE_URI = _build_database_url()

    SQLALCHEMY_POOL_SIZE = int(os.getenv("SQLALCHEMY_POOL_SIZE", "10"))
    SQLALCHEMY_MAX_OVERFLOW = int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "20"))
    SQLALCHEMY_POOL_TIMEOUT = int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "30"))
    SQLALCHEMY_POOL_RECYCLE = int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "3600"))
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"


class DevelopmentConfig(BaseConfig):
    """Конфигурация для среды разработки."""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """Конфигурация для продакшн-среды."""
    DEBUG = False


class TestingConfig(BaseConfig):
    """Конфигурация для тестовой среды."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:12345@localhost/test_production_db",
    )


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    """Получение конфигурации по имени окружения."""
    env = os.getenv("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)
