"""
Скрипт для заполнения базы данных тестовыми данными.
"""
import os
import sys

from app import create_app
from app.extensions import db
from app.models import User, Note
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def seed_database():
    """Заполняет БД тестовыми пользователями и заметками."""
    app = create_app()

    with app.app_context():
        # Очистка существующих тестовых данных
        db.session.query(Note).delete()
        db.session.query(User).filter(
            User.login.in_(['admin', 'user1', 'user2'])
        ).delete(synchronize_session='fetch')
        db.session.commit()

        # Создание пользователей
        admin = User(
            login='admin',
            password_hash=generate_password_hash('admin123'),
            role='Администратор',
        )
        db.session.add(admin)

        user1 = User(
            login='user1',
            password_hash=generate_password_hash('user123'),
            role='Пользователь',
        )
        db.session.add(user1)

        user2 = User(
            login='user2',
            password_hash=generate_password_hash('user234'),
            role='Пользователь',
        )
        db.session.add(user2)

        db.session.commit()

        # Получение ID пользователей
        db.session.execute(
            db.select(User).where(User.login == 'admin')
        ).scalar()
        user1_id = db.session.execute(
            db.select(User).where(User.login == 'user1')
        ).scalar().user_id
        user2_id = db.session.execute(
            db.select(User).where(User.login == 'user2')
        ).scalar().user_id

        # Создание тестовых заметок (минимум 5 по API.md)
        notes = [
            Note(
                title='Конференция ИТ',
                content='Расписание конференции: 15 марта 2027, зал А',
                id_user=user2_id,
            ),
            Note(
                title='Отчёт за Q1',
                content='Подготовить отчёт по продажам за первый квартал',
                id_user=user1_id,
            ),
            Note(
                title='Закупка материалов',
                content='Заказать столешницы и мебельные детали',
                id_user=user2_id,
            ),
            Note(
                title='Спецификация стола',
                content='Обновить спецификацию для Стол кухонный Самобранка',
                id_user=user1_id,
            ),
            Note(
                title='Встреча с заказчиком',
                content='Обсудить новый заказ на 10 столов',
                id_user=user2_id,
            ),
        ]
        db.session.add_all(notes)
        db.session.commit()

        print("База данных заполнена тестовыми данными!")
        print("  Пользователи: admin (admin123), user1 (user123), user2 (user234)")
        print(f"  Заметок создано: {len(notes)}")


if __name__ == '__main__':
    seed_database()
