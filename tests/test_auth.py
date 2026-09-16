"""
Тесты для API авторизации.
Задание 4: TZ.md — проверка авторизации и блокировки.
"""
import pytest
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Создаёт тестовое приложение с in-memory SQLite."""
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        # Создание тестовых пользователей
        admin = User(
            login="admin",
            password_hash=generate_password_hash("admin123"),
            role="Администратор",
        )
        user = User(
            login="user1",
            password_hash=generate_password_hash("user123"),
            role="Пользователь",
        )
        db.session.add_all([admin, user])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Тестовый клиент Flask."""
    return app.test_client()


def test_login_success(client):
    """Тест: успешная авторизация."""
    # Убедимся, что пользователь не заблокирован
    user = db.session.execute(
        db.select(User).where(User.login == "admin")
    ).scalar()
    user.is_blocked = False
    user.failed_attempts = 0
    db.session.commit()

    response = client.post(
        "/api/auth/login",
        json={"login": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Вы успешно авторизовались"
    assert data["login"] == "admin"
    assert data["role"] == "Администратор"


def test_login_wrong_password(client):
    """Тест: неверный пароль."""
    response = client.post(
        "/api/auth/login",
        json={"login": "admin", "password": "wrong"},
    )
    assert response.status_code == 401
    data = response.get_json()
    assert "неверный логин или пароль" in data["message"].lower()


def test_login_nonexistent_user(client):
    """Тест: несуществующий пользователь."""
    response = client.post(
        "/api/auth/login",
        json={"login": "nonexistent", "password": "password"},
    )
    assert response.status_code == 401


def test_account_blocking(client):
    """Тест: блокировка после 3 неверных попыток."""
    # 3 неверные попытки
    for _ in range(3):
        client.post(
            "/api/auth/login",
            json={"login": "admin", "password": "wrong"},
        )

    # 4-я попытка — пользователь заблокирован
    response = client.post(
        "/api/auth/login",
        json={"login": "admin", "password": "admin123"},
    )
    assert response.status_code == 403
    data = response.get_json()
    assert "заблокированы" in data["message"].lower()


def test_login_missing_fields(client):
    """Тест: отсутствие обязательных полей."""
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 400


def test_get_current_user_unauthenticated(client):
    """Тест: получение данных текущего пользователя без авторизации."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_current_user_authenticated(client):
    """Тест: получение данных текущего пользователя после авторизации."""
    # Убедимся, что пользователь не заблокирован
    user = db.session.execute(
        db.select(User).where(User.login == "admin")
    ).scalar()
    user.is_blocked = False
    user.failed_attempts = 0
    db.session.commit()

    # Авторизация через сессию
    client.post(
        "/api/auth/login",
        json={"login": "admin", "password": "admin123"},
    )

    # Получаем данные
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.get_json()
    assert data["login"] == "admin"
    assert data["role"] == "Администратор"
