# Документация: tests/test_notes.py

## Назначение

7 тестов для API заметок (Задание 5: API.md).

## Тесты

| Тест | Описание | Ожидаемый статус |
|------|----------|-----------------|
| `test_get_notes_returns_200` | Список заметок | 200 |
| `test_get_notes_format` | Формат ответа API.md | 200 |
| `test_get_notes_empty` | Пустая таблица | 200, [] |
| `test_get_notes_invalid_params` | skip=-1, limit=0 | 400 |
| `test_get_notes_json_valid` | JSON content-type | 200 |
| `test_get_notes_single` | Одна заметка по ID | 200 |
| `test_get_notes_not_found` | Несуществующая заметка | 404 |

## Проверки формата

- `id` — 5-значная строка
- `title_user` — содержит " - "
- `formatted_date` — ДД.ММ.ГГГГ
