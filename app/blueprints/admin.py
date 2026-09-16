"""Blueprint для админ-панели."""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.auth import hash_password
from app.models import User
from app.extensions import db

admin_bp = Blueprint("admin", __name__)


def _require_admin():
    """Проверка прав администратора."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized", "message": "Необходима авторизация"}), 401
    if current_user.role != "Администратор":
        return jsonify({"error": "Forbidden", "message": "Доступ запрещён"}), 403
    return None


@admin_bp.route("/users/", methods=["GET"])
@login_required
def list_users():
    """Список пользователей."""
    admin_check = _require_admin()
    if admin_check:
        return admin_check

    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify({
        "users": [
            {
                "user_id": u.user_id,
                "login": u.login,
                "role": u.role,
                "is_blocked": u.is_blocked,
                "failed_attempts": u.failed_attempts,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
    }), 200


@admin_bp.route("/users/", methods=["POST"])
@login_required
def create_user():
    """Создание пользователя."""
    admin_check = _require_admin()
    if admin_check:
        return admin_check

    data = request.get_json()
    if not data or "login" not in data or "password" not in data:
        return jsonify({"error": "Bad Request", "message": "Укажите login и password"}), 400

    login_value = data["login"].strip()
    password_value = data["password"]

    if not login_value or not password_value:
        return jsonify({"error": "Bad Request", "message": "Поля обязательны"}), 400

    existing = db.session.execute(
        db.select(User).where(User.login == login_value)
    ).scalar_one_or_none()

    if existing:
        return jsonify({"error": "Bad Request", "message": f"Пользователь '{login_value}' существует"}), 400

    role = data.get("role", "Пользователь")
    if role not in ("Администратор", "Пользователь"):
        return jsonify({"error": "Bad Request", "message": "Неверная роль"}), 400

    new_user = User(
        login=login_value,
        password_hash=hash_password(password_value),
        role=role,
        is_blocked=False,
        failed_attempts=0,
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": f"Пользователь '{login_value}' создан",
        "user_id": new_user.user_id,
    }), 201


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    """Обновление пользователя."""
    admin_check = _require_admin()
    if admin_check:
        return admin_check

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Not Found", "message": "Пользователь не найден"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request", "message": "Нет данных"}), 400

    if "role" in data:
        new_role = data["role"]
        if new_role not in ("Администратор", "Пользователь"):
            return jsonify({"error": "Bad Request", "message": "Неверная роль"}), 400
        user.role = new_role

    if "is_blocked" in data:
        user.is_blocked = data["is_blocked"]
        if not data["is_blocked"]:
            user.failed_attempts = 0

    db.session.commit()
    return jsonify({"message": "Данные обновлены"}), 200


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    """Удаление пользователя."""
    admin_check = _require_admin()
    if admin_check:
        return admin_check

    if user_id == current_user.user_id:
        return jsonify({"error": "Bad Request", "message": "Нельзя удалить себя"}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Not Found", "message": "Пользователь не найден"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Пользователь '{user.login}' удалён"}), 200
