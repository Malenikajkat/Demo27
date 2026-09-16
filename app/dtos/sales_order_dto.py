"""DTO для заказа."""
from dataclasses import dataclass, asdict
from typing import Optional, List


@dataclass
class SalesOrderItemDTO:
    """DTO для позиции заказа."""
    sales_order_item_id: str
    product_id: str
    quantity: float
    unit_price: float
    discount: float

    @classmethod
    def from_model(cls, item) -> "SalesOrderItemDTO":
        """Создать DTO из модели."""
        return cls(
            sales_order_item_id=str(item.sales_order_item_id),
            product_id=str(item.product_id),
            quantity=float(item.quantity),
            unit_price=float(item.unit_price),
            discount=float(item.discount),
        )

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)


@dataclass
class SalesOrderDTO:
    """DTO для заказа."""
    sales_order_id: str
    order_number: str
    order_date: Optional[str] = None
    client_id: str = ""
    executor_id: str = ""
    total_amount: float = 0.0
    created_at: Optional[str] = None
    items: Optional[List[SalesOrderItemDTO]] = None

    @classmethod
    def from_model(cls, order) -> "SalesOrderDTO":
        """Создать DTO из модели."""
        items = [SalesOrderItemDTO.from_model(item) for item in order.items] if order.items else None
        return cls(
            sales_order_id=str(order.sales_order_id), order_number=order.order_number,
            order_date=order.order_date.isoformat() if order.order_date else None,
            client_id=str(order.client_id), executor_id=str(order.executor_id),
            total_amount=float(order.total_amount) if order.total_amount else 0,
            created_at=order.created_at.isoformat() if order.created_at else None,
            items=items,
        )

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)
