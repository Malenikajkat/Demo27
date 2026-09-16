# Документация: scripts/check_password.py

## Назначение

Debug-скрипт для проверки хеша пароля пользователя admin.

## Логика

1. Загружает пользователя с ID=1
2. Проверяет пароли: admin, admin123, password
3. Выводит результат: OK/FAIL

## Использование

```bash
python scripts/check_password.py
```
