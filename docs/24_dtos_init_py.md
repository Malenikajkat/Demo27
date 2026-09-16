# Документация: app/dtos/__init__.py

## Назначение

Файл `app/dtos/__init__.py` — это **пустой пакетный файл** Python. Его единственная задача — сделать каталог `dtos/` полноценным Python-пакетом.

## Структура

```python
"""DTOs package."""
```

Содержит только docstring. Не содержит импортов, классов или функций.

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/dtos/client_dto.py` | Содержится | ClientDTO |
| `app/dtos/product_dto.py` | Содержится | ProductDTO |
| `app/dtos/material_dto.py` | Содержится | MaterialDTO |
| `app/dtos/operation_dto.py` | Содержится | OperationDTO |
| `app/dtos/sales_order_dto.py` | Содержится | SalesOrderDTO, SalesOrderItemDTO |
| `app/dtos/specification_dto.py` | Содержится | SpecificationMaterialDTO, SpecificationOperationDTO |
| `app/dtos/note_dto.py` | Содержится | NoteDTO |
| `app/dtos/user_dto.py` | Содержится | UserDTO |
