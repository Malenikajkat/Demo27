"""Blueprint для API авторизации.

Студенты: этот Blueprint предоставляет JSON API для авторизации.
Отличие от web_bp (app/blueprints/web.py):
- web_bp: возвращает HTML-страницы, использует redirect, render_template.
- auth_bp: возвращает JSON, используется для AJAX/API запросов (например, с мобильного приложения).

Оба маршрута используют одну и ту же логику проверки паролей (app/auth.py).
"""
from flask import Blueprint, request, jsonify
from flask_login import login_user

from app.auth import hash_password, verify_password
from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Авторизация пользователя через JSON API."""
    data = request.get_json()
    if not data or "login" not in data or "password" not in data:
        return jsonify({
            "error": "Bad Request",
            "message": "Поля login и password обязательны",
        }), 400

    login_value = data["login"].strip()
    password_value = data["password"]

    user = db.session.execute(
        db.select(User).where(User.login == login_value)
    ).scalar_one_or_none()

    if not user or not verify_password(password_value, user.password_hash):
        if user:
            user.failed_attempts += 1
            if user.failed_attempts >= 3:
                user.is_blocked = True
            db.session.commit()

        return jsonify({
            "error": "Unauthorized",
            "message": "Неверный логин или пароль",
        }), 401

    if user.is_blocked:
        return jsonify({
            "error": "Forbidden",
            "message": "Вы заблокированы",
        }), 403

    login_user(user)
    user.failed_attempts = 0
    db.session.commit()

    return jsonify({
        "message": "Вы успешно авторизовались",
        "user_id": user.user_id,
        "login": user.login,
        "role": user.role,
    }), 200


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Данные текущего пользователя.

    Студенты: этот маршрут демонстрирует паттерн "profile endpoint".
    После авторизации клиент может запросить /api/auth/me, чтобы получить
    данные текущего пользователя (без пароля!). Это стандартная практика
    для SPA (Single Page Application) и мобильных приложений.
    """
    from flask_login import current_user

    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized", "message": "Пользователь не авторизован"}), 401

    return jsonify({
        "user_id": current_user.user_id,
        "login": current_user.login,
        "role": current_user.role,
        "is_blocked": current_user.is_blocked,
    }), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    """Регистрация нового пользователя с обычными правами."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Bad Request",
            "message": "Необходимо передать JSON с login и password",
        }), 400

    login_value = data.get("login")
    password_value = data.get("password")

    if not isinstance(login_value, str) or not login_value.strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Логин не может быть пустым",
        }), 400

    if not isinstance(password_value, str) or not password_value.strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Пароль не может быть пустым",
        }), 400

    login_value = login_value.strip()

    existing = db.session.execute(
        db.select(User).where(User.login == login_value)
    ).scalar_one_or_none()

    if existing:
        return jsonify({
            "error": "Bad Request",
            "message": f"Пользователь '{login_value}' уже существует",
        }), 400

    new_user = User(
        login=login_value,
        password_hash=hash_password(password_value),
        role="Пользователь",
        is_blocked=False,
        failed_attempts=0,
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": f"Пользователь '{login_value}' зарегистрирован",
        "user_id": new_user.user_id,
        "login": new_user.login,
        "role": new_user.role,
    }), 201
