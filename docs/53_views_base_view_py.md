# Документация: app/views/base_view.py

## Назначение

Базовый класс для API View — наследник Flask `MethodView`. Определяет вспомогательные методы для создания JSON-ответов.

## Класс `BaseAPIView(MethodView)`

### Методы

| Метод | Параметры | Описание |
|-------|-----------|----------|
| `_success_response(data, status=200)` | data, status | JSON-ответ с успехом |
| `_error_response(message, status=400)` | message, status | JSON-ответ с ошибкой |
| `_not_found_response(resource="Ресурс")` | resource | JSON-ответ 404 |

### Пример использования

```python
class ClientListAPI(BaseAPIView):
    def get(self):
        clients = self.service.get_all_dto()
        return self._success_response({"clients": [c.to_dict() for c in clients]})
```

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `flask.views.MethodView` | Наследует |
| Все views | Наследуют |
