# Документация: database/import_clients.py

## Назначение

Скрипт для импорта заказчиков из JSON-файла в PostgreSQL.

## Функции

| Функция | Описание |
|---------|----------|
| `load_clients_from_json(path)` | Загрузка из JSON |
| `convert_id_to_uuid(id_str)` | Преобразование ID в UUID |
| `import_clients(db_config, json_path)` | Основной импорт |

## Логика импорта

1. Загружает `Заказчики.json`
2. Проверяет дубликаты по INN/name
3. Конвертирует ID в UUID
4. Вставляет через `execute_values()`

## Использование

```bash
python database/import_clients.py
```

## Зависимости

- `psycopg2` — подключение к PostgreSQL
- `json` — парсинг JSON
