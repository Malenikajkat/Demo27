"""
Фабрика Flask-приложения.
"""
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from app.extensions import db, login_manager, migrate
from app.config import get_config

# Загрузка .env из корня проекта
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def create_app(config_name=None):
    """Создаёт и настраивает Flask-приложение."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    base_dir = Path(__file__).parent.parent
    app = Flask(
        __name__,
        template_folder=str(base_dir / "web"),
        static_folder=str(base_dir / "web"),
        static_url_path="/static",
    )

    # Загрузка конфигурации
    config_class = get_config()
    app.config.from_object(config_class)

    # Финальная проверка наличия DATABASE_URL
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError(
            "SQLALCHEMY_DATABASE_URI is not set. "
            "Set DATABASE_URL or DATABASE_* environment variables."
        )

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "web.login_page"
    login_manager.login_message = "Пожалуйста, войдите в систему"

    # Callback для Flask-Login: загрузка пользователя по ID
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return db.session.get(User, int(user_id))

    # Регистрация Blueprint
    from app.blueprints.web import web_bp
    from app.blueprints.auth import auth_bp

    # OOP Views (Class-Based Views)
    from app.views.client_view import clients_bp
    from app.views.product_view import products_bp
    from app.views.material_view import materials_bp
    from app.views.operation_view import operations_bp
    from app.views.specification_view import specifications_bp
    from app.views.sales_order_view import sales_orders_bp
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
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")

    # Обработчики ошибок
    @app.errorhandler(400)
    def bad_request(e):
        return {"error": "Bad Request", "message": str(e.description)}, 400

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not Found", "message": "Ресурс не найден"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return {
            "error": "Internal Server Error",
            "message": "Ошибка подключения к базе данных",
        }, 500

    # Проверка подключения к базе данных
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

    # Создание таблиц БД (для разработки)
    with app.app_context():
        check_db_connection()
        db.create_all()

    return app
