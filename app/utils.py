"""
Утилиты для приложения.
Задание 5: API.md — трансформация данных заметок.
"""


def format_note_id(note_id: int) -> str:
    """Форматирует ID заметки согласно API.md: '00001'."""
    return str(note_id).zfill(5)


def format_date(date_obj) -> str:
    """Форматирует дату в ДД.ММ.ГГГГ."""
    return date_obj.strftime("%d.%m.%Y")


def build_note_response(note, login: str) -> dict:
    """Создаёт словарь ответа для заметки с трансформацией данных."""
    return {
        "id": format_note_id(note.note_id),
        "title_user": f"{note.title} - {login}",
        "content": note.content,
        "formatted_date": format_date(note.created_at),
    }
