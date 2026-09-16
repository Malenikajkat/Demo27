"""
Конфигурация pytest.
Устанавливает SQLite для тестов до импорта приложения.
"""
import os
import sys

# Устанавливаем SQLite до импорта app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
