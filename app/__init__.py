"""
Фабрика Flask-приложения.

Почему используется паттерн "Application Factory" (create_app)?

Студенты: этот файл демонстрирует паттерн "Factory Function" — функцию, которая создаёт
и настраивает Flask-приложение. Почему не просто `app = Flask(__name__)` на верхнем уровне?

1. Тестируемость: каждый тест может получить НОВОЕ приложение с чистой конфигурацией.
2. Несколько окружений: одна фабрика может создавать разные конфигурации
   (development, testing, production) на основе переменных окружения.
3. Расширения (db, login_manager) не привязаны к приложению при инициализации.
   Это позволяет создавать несколько Flask-приложений в одном процессе.

Структура create_app():
  1. Создание объекта Flask
  2. Загрузка конфигурации из app/config.py
  3. Инициализация расширений (db, migrate, login_manager)
  4. Регистрация Blueprint (модулей маршрутов)
  5. Настройка обработчиков ошибок
  6. Проверка подключения к БД и создание таблиц
"""
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, redirect, request, url_for

from app.extensions import db, login_manager, migrate
from app.config import get_config

# Загрузка переменных окружения из .env файла (если существует).
# Это позволяет хранить секреты (пароли, ключи) вне кода.
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def create_app(config_name=None):
    """Создаёт и настраивает Flask-приложение.

    Студенты: обратите внимание — эта функция принимает config_name, но в текущей
    реализации он не используется напрямую. Вместо этого get() считывает FLASK_ENV
    из переменных окружения. Это распространённая практика для переключения
    между development/production/testing конфигурациями.
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    base_dir = Path(__file__).parent.parent
    app = Flask(
        __name__,
        template_folder=str(base_dir / "web"),
        static_folder=str(base_dir / "web"),
        static_url_path="/static",
    )

    # Загрузка конфигурации: читает класс из config_by_name в app/config.py.
    # Например, если FLASK_ENV=development, будет использован DevelopmentConfig.
    config_class = get_config()
    app.config.from_object(config_class)

    # Финальная проверка: без DATABASE_URL приложение не сможет работать с БД.
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError(
            "SQLALCHEMY_DATABASE_URI is not set. "
            "Set DATABASE_URL or DATABASE_* environment variables."
        )

    # Инициализация расширений Flask.
    # Важно: мы передаём app через init_app(), а не через конструктор.
    # Это позволяет создать расширения ДО создания приложения (паттерн Factory).
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "web.login_page"
    login_manager.login_message = "Пожалуйста, войдите в систему"

    @login_manager.unauthorized_handler
    def unauthorized():
        """Для /api/* — JSON 401, для страниц — редирект на форму входа."""
        if request.path.startswith("/api/"):
            return {
                "error": "Unauthorized",
                "message": "Необходима авторизация",
            }, 401
        flash(login_manager.login_message, "error")
        return redirect(url_for(login_manager.login_view))

    # Flask-Login использует этот callback для восстановления сессии.
    # При каждом запросе Flask-Login вызывает load_user(user_id), чтобы
    # подгрузить объект пользователя из БД и сохранить в сессию.
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return db.session.get(User, int(user_id))

    # Регистрация Blueprint — это способ разделения маршрутов по модулям.
    # Каждый Blueprint отвечает за свою область (web-страницы, API авторизации, клиенты и т.д.).
    # url_prefix="/api/..." означает, что все маршруты этого Blueprint будут
    # начинаться с этого префикса (например, /api/clients/).
    from app.blueprints.web import web_bp
    from app.blueprints.auth import auth_bp

    # OOP Views (Class-Based Views)
    from app.views.client_view import clients_bp
    from app.views.product_view import products_bp
    from app.views.material_view import materials_bp
    from app.views.operation_view import operations_bp
    from app.views.specification_view import specifications_bp
    from app.views.sales_order_view import sales_orders_bp
    from app.views.production_order_view import production_orders_bp
    from app.views.admin_view import admin_bp
    from app.views.note_view import notes_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(clients_bp, url_prefix="/api/clients")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(materials_bp, url_prefix="/api/materials")
    app.register_blueprint(operations_bp, url_prefix="/api/operations")
    app.register_blueprint(specifications_bp, url_prefix="/api/specifications")
    app.register_blueprint(sales_orders_bp, url_prefix="/api/sales-orders")
    app.register_blueprint(production_orders_bp, url_prefix="/api/production-orders")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")

    # Обработчики ошибок: эти функции вызываются Flask автоматически,
    # когда возникает ошибка с указанным кодом (400, 404, 500).
    # Мы возвращаем JSON вместо HTML, чтобы API был консистентным.
    @app.errorhandler(400)
    def bad_request(e):
        return {"error": "Bad Request", "message": str(e.description)}, 400

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not Found", "message": "Ресурс не найден"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        # При ошибке откатываем транзакцию, чтобы не оставить БД в несогласованном состоянии.
        db.session.rollback()
        return {
            "error": "Internal Server Error",
            "message": "Ошибка подключения к базе данных",
        }, 500

    # Проверка подключения к базе данных при запуске.
    # Если БД недоступна — логируем ошибку, но не прерываем работу приложения.
    def check_db_connection():
        """Проверка подключения к PostgreSQL."""
        try:
            with app.app_context():
                db.engine.connect()
                logging.info("Успешное подключение к PostgreSQL")
                return True
        except Exception as e:
            logging.error(f"Ошибка подключения к базе данных: {e}")
            return False

    # Создание таблиц БД (для разработки).
    # Студенты: в продакшене обычно используют миграции (Alembic/Flask-Migrate),
    # а не db.create_all(). Этот код удобен для быстрого старта, но не заменяет миграции.
    with app.app_context():
        check_db_connection()
        db.create_all()

    return app
