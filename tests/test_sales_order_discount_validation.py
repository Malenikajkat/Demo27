
from unittest.mock import MagicMock

import pytest

from app.views.sales_order_view import validate_discount


@pytest.mark.parametrize("value", [0, 25, 50, 100, "50"])
def test_validate_discount_accepts_valid_values(value):
    db = MagicMock()

    discount, error = validate_discount({"discount": value}, db)

    assert discount == float(value)
    assert error is None
    db.session.rollback.assert_not_called()


@pytest.mark.parametrize("value", [-1, 101, "abc", None])
def test_validate_discount_rejects_invalid_values(value):
    db = MagicMock()

    discount, error = validate_discount({"discount": value}, db)

    assert discount is None
    assert error is not None
    db.session.rollback.assert_called_once()


def test_validate_discount_defaults_to_zero():
    db = MagicMock()

    discount, error = validate_discount({}, db)

    assert discount == 0
    assert error is None
    db.session.rollback.assert_not_called()
