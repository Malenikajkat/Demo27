"""Проверка пароля пользователя admin."""
from app import create_app
from app.auth import verify_password
from app.models import User
from app.extensions import db

app = create_app()
with app.app_context():
    user = db.session.get(User, 1)
    print(f'Пользователь: {user.login}')
    print(f'Хеш: {user.password_hash[:50]}...')

    for pwd in ['admin', 'admin123', 'password']:
        result = verify_password(pwd, user.password_hash)
        status = 'OK' if result else 'FAIL'
        print(f'Пароль "{pwd}" -> {status}')
