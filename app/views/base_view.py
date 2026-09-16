"""Базовый класс для API View."""
from flask import jsonify
from flask.views import MethodView


class BaseAPIView(MethodView):
    """Базовый класс для API endpoints."""

    decorators = []

    def _success_response(self, data, status=200):
        """Успешный ответ."""
        return jsonify(data), status

    def _error_response(self, message, status=400):
        """Ответ об ошибке."""
        return jsonify({"error": "Error", "message": message}), status

    def _not_found_response(self, resource="Ресурс"):
        """Ответ 404."""
        return jsonify({"error": "Not Found", "message": f"{resource} не найден"}), 404
