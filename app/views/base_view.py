"""
Базовый класс для API View.

Студенты: этот файл демонстрирует Паттерн "Class-Based Views" (CBV) в Flask.

Что такое Class-Based Views?
- В Flask есть два подхода к определению маршрутов:
  1. Function-Based Views (FBV): def get_clients(): ...
  2. Class-Based Views (CBV): class ClientView(MethodView): ...

- MethodView автоматически мапит HTTP-методы на методы класса:
  GET    -> get()
  POST   -> post()
  PUT    -> put()
  DELETE -> delete()

Преимущества CBV:
1. Организация: весь CRUD для одного ресурса — в одном классе.
2. Наследование: конкретные Views наследуют общие методы (_success_response, _error_response).
3. Декораторы: можно задать decorators = [...] для всех методов класса сразу.
4. Переиспользование: базовый класс содержит общую логику ответов.

Почему _success_response, а не success_response?
- Подчёркивание (_) означает "внутренний" метод (private convention).
- Он не вызывается напрямую из маршрутов, только из других методов класса.

jsonify(data), status — Flask позволяет возвращать кортеж (response, status_code).
Это эквивалентно: return jsonify(data); return ..., status
"""
from flask import jsonify
from flask.views import MethodView
from flask_login import login_required


class BaseAPIView(MethodView):
    """Базовый класс для API endpoints.

    Студенты: все конкретные View (ClientView, ProductView) наследуются от этого класса.
    Они переопределяют get(), post(), put(), delete() для своей логики,
    но могут использовать self._success_response(), self._error_response() и т.д.
    """

    # Все API-ресурсы доступны только авторизованным пользователям.
    # Неавторизованный запрос получает JSON 401 (см. unauthorized_handler в app/__init__.py).
    decorators = [login_required]

    def _success_response(self, data, status=200):
        return jsonify(data), status

    def _error_response(self, message, status=400):
        return jsonify({"error": "Error", "message": message}), status

    def _not_found_response(self, resource="Ресурс"):
        return jsonify({"error": "Not Found", "message": f"{resource} не найден"}), 404
