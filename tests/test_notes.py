"""
Тесты для API заметок.
Задание 5: API.md — проверка формата ответа и HTTP-статусов.
"""
import pytest
from app.extensions import db
from app.models import User, Note
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Создаёт тестовое приложение с in-memory SQLite."""
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        # Создание тестового пользователя
        user = User(
            login="testuser",
            password_hash=generate_password_hash("test123"),
            role="Пользователь",
        )
        db.session.add(user)
        db.session.commit()

        # Создание тестовых заметок
        note = Note(
            title="Test Note",
            content="Test content",
            id_user=user.user_id,
        )
        db.session.add(note)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Тестовый клиент Flask."""
    return app.test_client()


def test_get_notes_returns_200(client):
    """Тест: GET /api/notes возвращает 200 OK."""
    response = client.get("/api/notes/")
    assert response.status_code == 200
    data = response.get_json()
    assert "notes" in data
    assert "total" in data


def test_get_notes_format(client):
    """Тест: формат ответа соответствует спецификации API.md."""
    response = client.get("/api/notes/")
    data = response.get_json()
    assert len(data["notes"]) >= 1

    note = data["notes"][0]

    # Проверка всех обязательных полей
    assert "id" in note
    assert "title_user" in note
    assert "content" in note
    assert "formatted_date" in note

    # id должен быть нуль-заполненной строкой
    assert note["id"].isdigit() and len(note["id"]) == 5

    # title_user должен содержать " - "
    assert " - " in note["title_user"]

    # formatted_date должен быть в формате ДД.ММ.ГГГГ
    parts = note["formatted_date"].split(".")
    assert len(parts) == 3
    assert all(len(p) == 2 for p in parts[:2])
    assert len(parts[2]) == 4


def test_get_notes_empty(client):
    """Тест: пустая таблица заметок возвращает 200 с пустым массивом."""
    from app.models import Note
    db.session.query(Note).delete()
    db.session.commit()

    response = client.get("/api/notes/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["notes"] == []
    assert data["total"] == 0


def test_get_notes_invalid_params(client):
    """Тест: неверные параметры возвращают 400."""
    response = client.get("/api/notes/?skip=-1")
    assert response.status_code == 400

    response = client.get("/api/notes/?limit=0")
    assert response.status_code == 400


def test_get_notes_json_valid(client):
    """Тест: ответ всегда в формате JSON."""
    response = client.get("/api/notes/")
    assert response.content_type == "application/json"
    data = response.get_json()
    assert isinstance(data, dict)


def test_get_notes_single(client):
    """Тест: получение одной заметки по ID."""
    note = db.session.execute(db.select(Note)).scalar()
    response = client.get(f"/api/notes/{note.note_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == f"{note.note_id:05d}"
    assert " - " in data["title_user"]


def test_get_notes_not_found(client):
    """Тест: несуществующая заметка возвращает 404."""
    response = client.get("/api/notes/99999")
    assert response.status_code == 404
