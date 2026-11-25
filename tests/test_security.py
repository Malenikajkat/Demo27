"""
Тесты безопасности: контроль доступа, регистрация, конфигурация, экранирование в шаблонах.
Покрывают замечания S-01, S-02, S-03, S-04, S-09, L-01, L-02 из docs/review/review_report.md.
"""
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

PROTECTED_API = [
    "/api/clients/",
    "/api/products/",
    "/api/materials/",
    "/api/operations/",
    "/api/specifications/materials/",
    "/api/specifications/operations/",
    "/api/sales-orders/",
    "/api/production-orders/",
    "/api/admin/users/",
]


@pytest.fixture
def app():
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        db.session.add_all([
            User(login="admin", password_hash=generate_password_hash("admin12345"),
                 role="Администратор"),
            User(login="user1", password_hash=generate_password_hash("user12345"),
                 role="Пользователь"),
        ])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _login(client, login, password):
    return client.post("/api/auth/login", json={"login": login, "password": password})


@pytest.mark.parametrize("url", PROTECTED_API)
def test_api_requires_authentication(client, url):
    """S-01: без входа API отвечает JSON 401, а не данными."""
    response = client.get(url)
    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"


def test_api_available_after_login(client):
    assert _login(client, "user1", "user12345").status_code == 200
    assert client.get("/api/clients/").status_code == 200


def test_register_cannot_grant_admin_role_anonymously(client):
    """S-02: аноним не может создать администратора."""
    response = client.post("/api/auth/register", json={
        "login": "evil", "password": "password123", "role": "Администратор",
    })
    assert response.status_code == 403


def test_register_cannot_grant_admin_role_as_user(client):
    _login(client, "user1", "user12345")
    response = client.post("/api/auth/register", json={
        "login": "evil", "password": "password123", "role": "Администратор",
    })
    assert response.status_code == 403


def test_register_default_role_is_user(client, app):
    response = client.post("/api/auth/register", json={"login": "newbie", "password": "password123"})
    assert response.status_code == 201
    assert response.get_json()["role"] == "Пользователь"


def test_admin_can_register_admin(client):
    _login(client, "admin", "admin12345")
    response = client.post("/api/auth/register", json={
        "login": "boss", "password": "password123", "role": "Администратор",
    })
    assert response.status_code == 201
    assert response.get_json()["role"] == "Администратор"


@pytest.mark.parametrize("payload", [
    {"login": 123, "password": "password123"},      # логин не строка (L-01)
    {"login": "   ", "password": "password123"},    # пустой логин (L-01)
    {"login": "abc", "password": ""},               # пустой пароль (S-09)
    {"login": "abc", "password": "short"},          # слишком короткий пароль (S-09)
    {"login": "abc"},                               # нет пароля
])
def test_register_validation_returns_400(client, payload):
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Bad Request"


def test_non_json_body_returns_json_400(client):
    """L-02: вместо HTML-страницы 415 — JSON-ошибка 400."""
    response = client.post("/api/auth/login", data="x", content_type="text/plain")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Bad Request"


def test_production_config_requires_secret_key(monkeypatch):
    """S-04: production не стартует без SECRET_KEY."""
    from app.config import get_config
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("DATABASE_PASSWORD", "x")
    with pytest.raises(RuntimeError):
        get_config("production")


@pytest.mark.parametrize("template, unsafe", [
    ("clients.html", "${client.name}"),
    ("materials.html", "${material.name}"),
    ("products.html", "${product.name}"),
    ("operations.html", "${operation.name}"),
    ("admin-dashboard.html", "${user.login}"),
])
def test_templates_escape_user_data(template, unsafe):
    """S-03: пользовательские поля не вставляются в innerHTML без escapeHtml()."""
    assert unsafe not in (WEB_DIR / template).read_text(encoding="utf-8")
