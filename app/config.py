"""
Конфигурация приложения.

Студенты: этот файл демонстрирует паттерн "Configuration Hierarchy" через наследование классов.

Почему конфигурация разбита на классы, а не хранится в одном словаре?

1. Наследование: DevelopmentConfig наследует все настройки из BaseConfig
   и переопределяет только нужные (DEBUG = True). Это избегает дублирования.

2. Переключение окружений: функция get_config() читает FLASK_ENV из переменных
   окружения и возвращает нужный класс конфигурации.
   - development: DEBUG=True, SQLALCHEMY_ECHO=True (полезно при разработке)
   - production: DEBUG=False, оптимизированные настройки пула БД
   - testing: отдельная тестовая БД, TESTING=True

3. Безопасность: секретные ключи (SECRET_KEY) читаются из переменных окружения,
   а не захардкожены. Дефолтное значение "production-is-system-secret-key-change-me"
   — это подсказка для разработчиков изменить его!

4. SQLALCHEMY_TRACK_MODIFICATIONS = False — важная оптимизация!
   По умолчанию SQLAlchemy отслеживает все изменения объектов в памяти,
   чтобы отправлять события. Это замедляет приложение. False отключает отслеживание,
   так как Flask-SQLAlchemy не использует эти события.

Как добавить новую конфигурацию?
  1. Создайте новый класс, наследующий BaseConfig
  2. Добавьте его в config_by_name
  3. Установите FLASK_ENV=ваше_окружение
"""
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла.
# Это позволяет хранить секреты (пароли, ключи) вне кода.
load_dotenv(Path(__file__).parent.parent / ".env")

# Корневая директория проекта (верхнеуровневая папка с папками app/, web/ и т.д.)
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


# Ключ для разработки. В production запуск без SECRET_KEY запрещён (см. get_config).
DEV_SECRET_KEY = secrets.token_hex(32)  # случайный ключ на процесс: в dev сессии сбрасываются при перезапуске


class BaseConfig:
    """Базовая конфигурация."""
    SECRET_KEY = os.getenv("SECRET_KEY", DEV_SECRET_KEY)
    # Защита сессионной cookie: недоступна из JS, не отправляется при кросс-сайт POST.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
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


def get_config(name=None):
    """Возвращает класс конфигурации по имени окружения.

    Если имя не передано, используется переменная FLASK_ENV (по умолчанию development).
    Для production обязательны SECRET_KEY и параметры подключения к БД.
    """
    env = name or os.getenv("FLASK_ENV", "development")
    config_class = config_by_name.get(env, DevelopmentConfig)
    if config_class is ProductionConfig:
        missing = []
        if not os.getenv("SECRET_KEY"):
            missing.append("SECRET_KEY")
        if not (os.getenv("DATABASE_URL") or os.getenv("DATABASE_PASSWORD")):
            missing.append("DATABASE_URL или DATABASE_PASSWORD")
        if missing:
            raise RuntimeError(
                "Для production не заданы переменные окружения: " + ", ".join(missing)
            )
    return config_class
