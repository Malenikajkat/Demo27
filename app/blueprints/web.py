"""
Blueprint для веб-страниц: авторизация, дашборды.
"""
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
            return redirect(url_for("web.admin_users"))
        return redirect(url_for("web.dashboard"))

    return render_template("login.html", puzzle_solved=False)


@web_bp.route("/dashboard")
@login_required
def dashboard():
    """Главная страница с статистикой."""
    return render_template(
        "dashboard.html", user=current_user,
        current_page="dashboard", page_title="Главная"
    )


@web_bp.route("/clients")
@login_required
def clients():
    """Страница управления клиентами."""
    return render_template(
        "clients.html", user=current_user,
        current_page="clients", page_title="Клиенты"
    )


@web_bp.route("/products")
@login_required
def products():
    """Страница управления продукцией."""
    return render_template(
        "products.html", user=current_user,
        current_page="products", page_title="Продукция"
    )


@web_bp.route("/materials")
@login_required
def materials():
    """Страница управления материалами."""
    return render_template(
        "materials.html", user=current_user,
        current_page="materials", page_title="Материалы"
    )


@web_bp.route("/operations")
@login_required
def operations():
    """Страница управления операциями."""
    return render_template(
        "operations.html", user=current_user,
        current_page="operations", page_title="Операции"
    )


@web_bp.route("/specifications")
@login_required
def specifications():
    """Страница управления спецификациями."""
    return render_template(
        "specifications.html", user=current_user,
        current_page="specifications", page_title="Спецификации"
    )


@web_bp.route("/sales-orders")
@login_required
def sales_orders():
    """Страница управления заказами покупателей."""
    return render_template(
        "sales-orders.html", user=current_user,
        current_page="sales-orders", page_title="Заказы покупателей"
    )


@web_bp.route("/admin/users")
@login_required
def admin_users():
    """Страница управления пользователями (админ)."""
    if current_user.role != "Администратор":
        flash("Доступ запрещён", "error")
        return redirect(url_for("web.dashboard"))

    return render_template(
        "admin-dashboard.html", user=current_user,
        current_page="admin-users", page_title="Пользователи"
    )


@web_bp.route("/notes")
@login_required
def notes():
    """Страница управления заметками."""
    return render_template(
        "notes.html", user=current_user,
        current_page="notes", page_title="Заметки"
    )


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


@web_bp.route("/api/notes/", methods=["POST"])
@login_required
def create_note():
    """Создание новой заметки."""
    try:
        data = request.get_json()
        if not data or "title" not in data or "content" not in data:
            return {"error": "Bad Request", "message": "Укажите title и content"}, 400

        from app.models import Note
        note = Note(
            title=data["title"],
            content=data["content"],
            id_user=current_user.user_id
        )
        db.session.add(note)
        db.session.commit()

        from app.utils import build_note_response
        return {
            "message": "Заметка создана",
            "note": build_note_response(note, current_user.login)
        }, 201
    except Exception:
        db.session.rollback()
        return {"error": "Internal Server Error", "message": "Ошибка БД"}, 500
