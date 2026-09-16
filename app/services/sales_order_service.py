"""Сервис для работы с заказами."""
from typing import Optional, List
from app.services.base_service import BaseService
from app.repositories.sales_order_repository import SalesOrderRepository
from app.dtos.sales_order_dto import SalesOrderDTO


class SalesOrderService(BaseService):
    """Сервис для работы с заказами."""

    def __init__(self):
        super().__init__(SalesOrderRepository())

    def get_all_dto(self, skip: int = 0, limit: int = 100) -> List[SalesOrderDTO]:
        """Получить список заказов в формате DTO."""
        orders = self.get_all(skip, limit)
        return [SalesOrderDTO.from_model(o) for o in orders]

    def get_by_id_dto(self, order_id) -> Optional[SalesOrderDTO]:
        """Получить заказ по ID в формате DTO."""
        order = self.get_by_id(order_id)
        return SalesOrderDTO.from_model(order) if order else None

    def calculate_cost(self, order_id: str) -> dict:
        """Расчёт стоимости заказа."""
        order = self.get_by_id(order_id)
        if not order:
            return {"error": "Заказ не найден"}

        total = 0.0
        items_detail = []
        for item in order.items:
            from app.models import ProductPrice
            from app.extensions import db
            from sqlalchemy import select

            price_stmt = select(ProductPrice).where(
                ProductPrice.product_id == item.product_id
            ).order_by(ProductPrice.effective_date.desc()).limit(1)
            price_record = db.session.execute(price_stmt).scalar_one_or_none()

            unit_price = float(item.unit_price) if item.unit_price else (
                float(price_record.price) if price_record else 0.0
            )
            discount = float(item.discount) if item.discount else 0.0
            quantity = float(item.quantity)

            item_total = quantity * unit_price * (1 - discount / 100)
            total += item_total

            items_detail.append({
                "product_id": str(item.product_id),
                "quantity": quantity,
                "unit_price": unit_price,
                "discount": discount,
                "item_total": item_total,
            })

        return {
            "sales_order_id": str(order.sales_order_id),
            "order_number": order.order_number,
            "items": items_detail,
            "total_amount": total,
        }
