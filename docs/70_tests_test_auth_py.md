# Документация: tests/test_auth.py

## Назначение

7 тестов для API авторизации (Задание 4: TZ.md).

## Тесты

| Тест | Описание | Ожидаемый статус |
|------|----------|-----------------|
| `test_login_success` | Успешный вход | 200 |
| `test_login_wrong_password` | Неверный пароль | 401 |
| `test_login_nonexistent_user` | Несуществующий пользователь | 401 |
| `test_account_blocking` | Блокировка после 3 попыток | 403 |
| `test_login_missing_fields` | Нет полей | 400 |
| `test_get_current_user_unauthenticated` | Без авторизации | 401 |
| `test_get_current_user_authenticated` | После авторизации | 200 |

## Фикстуры

| Фикстура | Описание |
|----------|----------|
| `app` | Тестовое приложение с SQLite |
| `client` | Flask test client |
