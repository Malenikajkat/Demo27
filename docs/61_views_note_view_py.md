# Документация: app/views/note_view.py

## Назначение

API для заметок: GET списка и одной заметки с трансформацией данных. Дублирует `app/blueprints/notes.py`.

## Функции

### `get_notes()`
| Маршрут | Описание |
|---------|----------|
| GET /api/notes/ | Список с пагинацией |

### `get_note(note_id)`
| Маршрут | Описание |
|---------|----------|
| GET /api/notes/<note_id> | Одна заметка |

## Трансформация

Использует `build_note_response()` из `app/utils.py`.

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `app/blueprints/notes.py` | Дублирует |
| `app/utils.py` | Использует `build_note_response()` |
| `Note`, `User` | Модели |

## Важные замечания

1. **Дубликат**: Полностью повторяет `app/blueprints/notes.py`.
2. **Трансформация**: Поля `id`, `title_user`, `formatted_date`.
