"""Проверки валидации позиций заказа покупателя."""
import pytest

from app.views.sales_order_view import _parse_order_date, _parse_order_item


VALID_PRODUCT_ID = "12345678-1234-5678-1234-567812345678"


def test_parse_order_item_accepts_valid_values():
    product_id, quantity, unit_price, discount = _parse_order_item({
        "product_id": VALID_PRODUCT_ID,
        "quantity": 2,
        "unit_price": 100,
        "discount": 15,
    })

    assert str(product_id) == VALID_PRODUCT_ID
    assert quantity == 2
    assert unit_price == 100
    assert discount == 15


@pytest.mark.parametrize("discount", [-1, 100.01, float("nan"), float("inf")])
def test_parse_order_item_rejects_invalid_discount(discount):
    with pytest.raises(ValueError):
        _parse_order_item({"product_id": VALID_PRODUCT_ID, "discount": discount})


def test_parse_order_item_rejects_non_positive_quantity():
    with pytest.raises(ValueError):
        _parse_order_item({"product_id": VALID_PRODUCT_ID, "quantity": 0})


@pytest.mark.parametrize("value", ["24.11.2026", "not-a-date", 20261124, None])
def test_parse_order_date_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        _parse_order_date(value)


def test_parse_order_date_accepts_iso_date():
    assert _parse_order_date("2026-11-24").isoformat() == "2026-11-24"
