"""
Точка входа в Flask-приложение.

Параметры запуска берутся из переменных окружения:
  FLASK_RUN_HOST (по умолчанию 127.0.0.1), FLASK_RUN_PORT (5000), FLASK_DEBUG (0/1).
"""
import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_RUN_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
