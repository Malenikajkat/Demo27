# Документация: web/base-dashboard.html

## Назначение

Базовый шаблон-макет для всех дашбордов: sidebar, top-bar, content area.

## Структура

| Элемент | Описание |
|---------|----------|
| Sidebar | Навигация с ролями |
| Top-bar | Пользователь, выход |
| Content | `{% block content %}` |
| Notification | Toast-уведомления |
| Modal | Модальные окна |

## JavaScript-утилиты

| Функция | Описание |
|---------|----------|
| `showNotification(msg, type)` | Показать уведомление |
| `openModal(id)` | Открыть модалку |
| `closeModal(id)` | Закрыть модалку |
| `fetchData(url)` | GET запрос |
| `postData(url, data)` | POST запрос |
| `putData(url, data)` | PUT запрос |
| `deleteData(url)` | DELETE запрос |

## Role-based navigation

| Роль | Видимые пункты |
|------|---------------|
| Администратор | Все + админ-панель |
| Пользователь | Основные разделы |
