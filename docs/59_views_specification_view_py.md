# Документация: app/views/specification_view.py

## Назначение

Class-Based API для спецификаций: GET/POST для материалов и операций. Прямой доступ к БД без сервисного слоя.

## Классы

### `SpecificationMaterialListAPI(BaseAPIView)`
| Метод | Маршрут | Описание |
|-------|---------|----------|
| `get()` | GET /api/specifications/materials/ | Список |
| `post()` | POST /api/specifications/materials/ | Создание |

### `SpecificationOperationListAPI(BaseAPIView)`
| Метод | Маршрут | Описание |
|-------|---------|----------|
| `get()` | GET /api/specifications/operations/ | Список |
| `post()` | POST /api/specifications/operations/ | Создание |

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseAPIView` | Наследует |
| `db` | Прямой доступ к БД |
| `SpecificationMaterial`, `SpecificationOperation` | Модели |

## Важные замечания

1. **Без сервисного слоя**: Прямой `db.session.execute()`.
2. **Только GET/POST**: Нет обновления и удаления.
