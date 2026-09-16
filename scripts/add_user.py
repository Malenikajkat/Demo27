"""
Скрипт для добавления пользователя в базу данных.

Использование:
    python scripts/add_user.py admin пароль Администратор
    python scripts/add_user.py admin пароль Пользователь

Аргументы:
    1. login    - логин пользователя
    2. password - пароль
    3. role     - роль (опционально, по умолчанию "Пользователь")

Примеры:
    python scripts/add_user.py admin admin Администратор
    python scripts/add_user.py user1 secret123
"""
import sys

from app import create_app
from app.auth import hash_password
from app.models import User
from app.extensions import db


def add_user(login: str, password: str, role: str = "Пользователь"):
    """Создаёт пользователя в базе данных."""
    app = create_app()

    with app.app_context():
        # Проверяем, существует ли пользователь
        existing = db.session.execute(
            db.select(User).where(User.login == login)
        ).scalar_one_or_none()

        if existing:
            print(f"⚠  Пользователь '{login}' уже существует (ID: {existing.user_id})")
            print(f"   Роль: {existing.role}")
            print(f"   Заблокирован: {existing.is_blocked}")

            # Обновляем пароль и роль
            existing.password_hash = hash_password(password)
            existing.role = role
            existing.is_blocked = False
            existing.failed_attempts = 0
            db.session.commit()
            print("Пароль и роль обновлены")
            return

        # Создаём нового пользователя
        user = User(
            login=login,
            password_hash=hash_password(password),
            role=role,
            is_blocked=False,
            failed_attempts=0,
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅  Пользователь '{login}' успешно создан!")
        print(f"   ID: {user.user_id}")
        print(f"   Роль: {user.role}")
        print(f"   Пароль: {password}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    login = sys.argv[1]
    password = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else "Пользователь"

    add_user(login, password, role)
