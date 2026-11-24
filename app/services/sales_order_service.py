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
        """Расчёт стоимости заказа с учётом себестоимости.

        Возвращает:
        - items_detail: детали по каждой позиции (продажа)
        - cost_detail: себестоимость (материалы + операции)
        - total_amount: общая сумма продажи
        - total_cost: общая себестоимость
        """
        from app.models import MaterialPrice, OperationPrice
        from app.extensions import db
        from sqlalchemy import select

        order = self.get_by_id(order_id)
        if not order:
            return {"error": "Заказ не найден"}

        total_amount = 0.0
        total_cost = 0.0
        items_detail = []
        cost_detail = {
            "material_costs": {"total": 0.0, "items": []},
            "operation_costs": {"total": 0.0, "items": []}
        }

        for item in order.items:
            quantity = float(item.quantity)
            unit_price = float(item.unit_price) if item.unit_price else 0.0
            discount = float(item.discount) if item.discount else 0.0
            item_total = quantity * unit_price * (1 - discount / 100)
            total_amount += item_total

            # Добавляем деталь по позиции
            items_detail.append({
                "product_id": str(item.product_id),
                "product_name": item.product.name if item.product else "",
                "quantity": quantity,
                "unit_price": unit_price,
                "discount": discount,
                "item_total": item_total,
            })

            # Расчёт себестоимости на основе спецификаций
            product = item.product
            product_cost = 0.0

            # 1. Материальные затраты
            spec_mats = product.spec_materials
            for spec_mat in spec_mats:
                mat_qty_per_unit = float(spec_mat.quantity_per_unit)
                mat_qty = mat_qty_per_unit * quantity

                # Получаем цену материала
                price_stmt = select(MaterialPrice).where(
                    MaterialPrice.material_id == spec_mat.material_id
                ).order_by(MaterialPrice.effective_date.desc()).limit(1)
                price_record = db.session.execute(price_stmt).scalar_one_or_none()
                mat_price = float(price_record.price) if price_record else 0.0
                mat_total = mat_qty * mat_price
                product_cost += mat_total

                material = spec_mat.material
                cost_detail["material_costs"]["items"].append({
                    "material_id": str(material.material_id),
                    "material_name": material.name,
                    "quantity_per_unit": mat_qty_per_unit,
                    "total_quantity": mat_qty,
                    "price": mat_price,
                    "total": mat_total
                })

            # 2. Затраты на операции
            spec_ops = product.spec_operations
            for spec_op in spec_ops:
                time_norm = float(spec_op.time_norm)
                op_qty = float(spec_op.op_quantity)
                total_time = time_norm * op_qty * quantity

                # Получаем цену операции
                price_stmt = select(OperationPrice).where(
                    OperationPrice.operation_id == spec_op.operation_id
                ).order_by(OperationPrice.effective_date.desc()).limit(1)
                price_record = db.session.execute(price_stmt).scalar_one_or_none()
                op_price = float(price_record.price) if price_record else 0.0
                op_total = total_time * op_price
                product_cost += op_total

                operation = spec_op.operation
                cost_detail["operation_costs"]["items"].append({
                    "operation_id": str(operation.operation_id),
                    "operation_name": operation.name,
                    "time_norm": time_norm,
                    "op_quantity": op_qty,
                    "total_time": total_time,
                    "price": op_price,
                    "total": op_total
                })

            total_cost += product_cost

        # Суммируем затраты
        cost_detail["material_costs"]["total"] = sum(
            it["total"] for it in cost_detail["material_costs"]["items"]
        )
        cost_detail["operation_costs"]["total"] = sum(
            it["total"] for it in cost_detail["operation_costs"]["items"]
        )

        gross_profit = total_amount - total_cost
        profitability = (gross_profit / total_amount * 100) if total_amount > 0 else 0

        return {
            "sales_order_id": str(order.sales_order_id),
            "order_number": order.order_number,
            "items": items_detail,
            "total_amount": total_amount,
            "total_cost": total_cost,
            "gross_profit": gross_profit,
            "profitability": round(profitability, 2),
            "cost_detail": cost_detail
        }
