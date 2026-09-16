# Документация: tests/conftest.py

## Назначение

Конфигурация pytest: устанавливает SQLite in-memory до импорта приложения.

## Логика

```python
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
```

Это позволяет тестам работать без PostgreSQL.
