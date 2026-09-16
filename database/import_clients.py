"""
Импорт данных из Заказчики.json в базу данных PostgreSQL.
Задание 2: Импорт данных заказчиков.
"""
import json
import sys
import uuid
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values


def load_clients_from_json(json_path: str) -> list[dict]:
    """Загрузить данные заказчиков из JSON файла."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def convert_id_to_uuid(id_str: str) -> str:
    """Преобразует ID в UUID формат."""
    # Если уже UUID формат - возвращаем как есть
    try:
        uuid.UUID(id_str)
        return id_str
    except ValueError:
        # Преобразуем "000000001" в "00000000-0000-0000-0000-000000000001"
        num = int(id_str)
        return str(uuid.UUID(int=num, version=4))


def import_clients(db_config: dict, json_path: str) -> None:
    """Импортировать заказчиков в базу данных."""
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    clients = load_clients_from_json(json_path)
    inserted = 0
    skipped = 0

    for client in clients:
        # Проверка на дубликат по INN или name
        cur.execute(
            "SELECT client_id FROM clients WHERE inn = %s OR name = %s",
            (client.get('inn'), client.get('name'))
        )
        if cur.fetchone():
            skipped += 1
            print(f"  Пропущен (дубликат): {client['name']}")
            continue

        # Вставка клиента
        client_uuid = convert_id_to_uuid(client['id'])
        execute_values(
            cur,
            """INSERT INTO clients (client_id, name, inn, address, phone, client_type)
               VALUES %s""",
            [(
                client_uuid,
                client['name'],
                client.get('inn', ''),
                client.get('addres', ''),
                client.get('phone', ''),
                client.get('type', 'Покупатель')
            )]
        )
        inserted += 1
        print(f"  Вставлен: {client['name']}")

    conn.commit()
    cur.close()
    conn.close()

    print(f"\nИмпорт завершён: вставлено {inserted}, пропущено {skipped}")


if __name__ == '__main__':
    # Конфигурация БД (должна совпадать с .env)
    db_config = {
        'dbname': 'production',
        'user': 'postgres',
        'password': '12345',
        'host': 'localhost',
        'port': 5432
    }

    # Путь к JSON файлу
    json_path = Path(__file__).parent.parent / 'Заказчики.json'
    if not json_path.exists():
        # Альтернативный путь
        json_path = Path(__file__).parent.parent / 'database' / 'Заказчики.json'

    if not json_path.exists():
        print(f"Ошибка: файл не найден: {json_path}")
        sys.exit(1)

    print(f"Импорт из: {json_path}")
    import_clients(db_config, str(json_path))
