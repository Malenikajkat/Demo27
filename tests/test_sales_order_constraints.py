"""
Тесты ограничений модели SalesOrderItem.
Проверяется допустимый диапазон скидки: от 0 до 100 процентов.
"""

from app.models import SalesOrderItem


def get_discount_constraint():
    """Возвращает ограничение диапазона скидки."""
    return next(
        (
            constraint
            for constraint in SalesOrderItem.__table__.constraints
            if constraint.name == "chk_sales_discount_range"
        ),
        None,
    )


def test_discount_column_exists():
    """Поле скидки существует и обязательно для заполнения."""
    discount_column = SalesOrderItem.__table__.columns.get("discount")

    assert discount_column is not None
    assert discount_column.nullable is False


def test_discount_default_is_zero():
    """Значение скидки по умолчанию равно нулю."""
    discount_column = SalesOrderItem.__table__.columns.get("discount")

    assert discount_column.server_default is not None
    assert "0.00" in str(discount_column.server_default.arg)


def test_discount_minimum_is_zero():
    """Ограничение запрещает отрицательную скидку."""
    constraint = get_discount_constraint()

    assert constraint is not None
    assert "discount >= 0" in str(constraint.sqltext)


def test_discount_maximum_is_100():
    """Ограничение запрещает скидку больше 100 процентов."""
    constraint = get_discount_constraint()

    assert constraint is not None
    assert "discount <= 100" in str(constraint.sqltext)