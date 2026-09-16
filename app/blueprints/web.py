"""
Blueprint для веб-страниц: авторизация, дашборды.
"""
import os
from pathlib import Path

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file,
)
from flask_login import login_user, logout_user, login_required, current_user

from app.auth import verify_password
from app.models import User
from app.extensions import db

web_bp = Blueprint("web", __name__)

# Путь к папке с изображениями пазл-капчи
BASE_DIR = Path(__file__).parent.parent.parent
IMAGE_FOLDER = BASE_DIR / "image"


@web_bp.route("/", methods=["GET", "POST"])
def login_page():
    """Страница авторизации. GET — форма, POST — проверка."""
    if request.method == "POST":
        login_value = request.form.get("login", "").strip()
        password_value = request.form.get("password", "")

        # Временно отключена проверка капчи
        captcha_ok = True

        if not captcha_ok:
            flash("Пазл собран неверно. Попробуйте ещё раз.", "error")
            return render_template(
                "login.html",
                puzzle_solved=False,
                error_message="Пазл собран неверно",
                login=login_value,
            )

        if not login_value or not password_value:
            flash("Неверный логин или пароль", "error")
            return render_template(
                "login.html",
                puzzle_solved=True,
                error_message="Неверный логин или пароль",
                login=login_value,
            )

        user = db.session.execute(
            db.select(User).where(User.login == login_value)
        ).scalar_one_or_none()

        if not user or not verify_password(password_value, user.password_hash):
            if user:
                user.failed_attempts += 1
                if user.failed_attempts >= 3:
                    user.is_blocked = True
                db.session.commit()

            flash("Неверный логин или пароль", "error")
            return render_template(
                "login.html",
                puzzle_solved=True,
                error_message="Неверный логин или пароль",
                login=login_value,
            )

        if user.is_blocked:
            flash("Вы заблокированы. Обратитесь к администратору", "error")
            return render_template(
                "login.html",
                puzzle_solved=True,
                error_message="Вы заблокированы",
                login=login_value,
            )

        login_user(user)
        user.failed_attempts = 0
        db.session.commit()

        flash("Вы успешно авторизовались", "success")

        if user.role == "Администратор":
            return redirect(url_for("web.admin_dashboard"))
        return redirect(url_for("web.user_dashboard"))

    return render_template("login.html", puzzle_solved=False)


@web_bp.route("/admin-dashboard")
@login_required
def admin_dashboard():
    """Дашборд администратора."""
    if current_user.role != "Администратор":
        flash("Доступ запрещён", "error")
        return redirect(url_for("web.user_dashboard"))

    flash("Добро пожаловать в панель администратора!", "info")
    return render_template("admin-dashboard.html", user=current_user)


@web_bp.route("/user-dashboard")
@login_required
def user_dashboard():
    """Дашборд обычного пользователя."""
    flash("Добро пожаловать!", "info")
    return render_template("user-dashboard.html", user=current_user)


@web_bp.route("/image/<filename>")
def serve_image(filename):
    """Раздача изображений пазл-капчи."""
    filepath = IMAGE_FOLDER / filename
    if filepath.exists() and filepath.is_file():
        return send_file(str(filepath))
    return {"error": "Not found"}, 404


@web_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Выход из системы."""
    logout_user()
    session.clear()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("web.login_page"))
