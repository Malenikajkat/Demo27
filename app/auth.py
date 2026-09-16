"""
Модуль аутентификации: хеширование и проверка паролей.
"""
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет пароль по хешу."""
    return check_password_hash(password_hash, password)
