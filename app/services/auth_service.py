"""Сервис аутентификации."""
from flask import jsonify
from flask_login import login_user
from app.repositories.user_repository import UserRepository
from app.auth import verify_password
from app.extensions import db


class AuthService:
    """Сервис аутентификации."""

    def __init__(self):
        self.repository = UserRepository()

    def login(self, data: dict):
        login_value = data.get("login", "").strip()
        password_value = data.get("password", "")

        if not login_value or not password_value:
            return jsonify({"error": "Bad Request", "message": "Поля login и password обязательны"}), 400

        user = self.repository.find_by_login(login_value)

        # 1. Блокировка — до проверки пароля
        if user and user.is_blocked:
            return jsonify({"error": "Forbidden", "message": "Вы заблокированы"}), 403

        # 2. Пароль
        if not user or not verify_password(password_value, user.password_hash):
            if user:
                self.repository.increment_failed_attempts(user.user_id)
            return jsonify({"error": "Unauthorized", "message": "Неверный логин или пароль"}), 401

        login_user(user)
        user.failed_attempts = 0
        db.session.commit()
        return jsonify({
            "message": "Авторизация успешна",
            "user_id": user.user_id, "login": user.login, "role": user.role,
        }), 200
