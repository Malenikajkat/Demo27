# Документация: web/notes.html

## Назначение

Страница заметок: карточки + форма создания.

## API

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/notes/` | GET | Список с трансформацией |
| `/api/notes/` | POST | Создание (через web.py) |

## Компоненты

- Grid карточек (id, title_user, content, date)
- Форма создания (title, content)
- Pagination (skip/limit)

## Трансформация

Поля: `id` (00001), `title_user` (title - login), `formatted_date` (ДД.ММ.ГГГГ)
