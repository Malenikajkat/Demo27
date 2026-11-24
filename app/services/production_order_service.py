"""Сервис для работы с заказами на производство."""
from typing import Optional, List
from app.services.base_service import BaseService
from app.repositories.production_order_repository import ProductionOrderRepository
from app.dtos.production_order_dto import ProductionOrderDTO


class ProductionOrderService(BaseService):
    """Сервис для работы с заказами на производство."""

    def __init__(self):
        super().__init__(ProductionOrderRepository())

    def get_all_dto(self, skip: int = 0, limit: int = 100) -> List[ProductionOrderDTO]:
        """Получить список заказов на производство в формате DTO."""
        orders = self.get_all(skip, limit)
        return [ProductionOrderDTO.from_model(o) for o in orders]

    def get_by_id_dto(self, order_id) -> Optional[ProductionOrderDTO]:
        """Получить заказ на производство по ID в формате DTO."""
        order = self.get_by_id(order_id)
        return ProductionOrderDTO.from_model(order) if order else None

    def get_order_with_details(self, order_id) -> dict:
        """Получить заказ на производство с материалами и операциями."""
        from app.models import MaterialPrice, OperationPrice
        from app.extensions import db
        from sqlalchemy import select

        order = self.get_by_id(order_id)
        if not order:
            return {"error": "Заказ не найден"}

        result = {
            "order_id": str(order.order_id),
            "order_number": order.order_number,
            "order_date": order.order_date.isoformat() if order.order_date else None,
            "subdivision": order.subdivision,
            "client_id": str(order.client_id) if order.client_id else None,
            "total_amount": float(order.total_amount) if order.total_amount else 0,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "items": []
        }

        for item in order.items:
            product = item.product

            # Проверяем, существует ли продукт
            if not product:
                product_data = {
                    "order_item_id": str(item.order_item_id),
                    "product_id": str(item.product_id),
                    "product_name": "Удалённая продукция",
                    "product_code": "",
                    "quantity": float(item.quantity),
                    "completed_quantity": float(item.completed_quantity),
                    "unit_price": float(item.unit_price),
                    "total_price": float(item.total_price),
                    "materials": [],
                    "operations": []
                }
                result["items"].append(product_data)
                continue

            product_data = {
                "order_item_id": str(item.order_item_id),
                "product_id": str(product.product_id),
                "product_name": product.name,
                "product_code": product.code,
                "quantity": float(item.quantity),
                "completed_quantity": float(item.completed_quantity),
                "unit_price": float(item.unit_price),
                "total_price": float(item.total_price),
                "materials": [],
                "operations": []
            }

            # Получаем спецификацию материалов
            spec_mats = product.spec_materials
            for spec_mat in spec_mats:
                material = spec_mat.material
                mat_qty_per_unit = float(spec_mat.quantity_per_unit)
                mat_qty = mat_qty_per_unit * float(item.quantity)

                # Получаем цену материала
                price_stmt = select(MaterialPrice).where(
                    MaterialPrice.material_id == spec_mat.material_id
                ).order_by(MaterialPrice.effective_date.desc()).limit(1)
                price_record = db.session.execute(price_stmt).scalar_one_or_none()
                mat_price = float(price_record.price) if price_record else 0.0
                mat_total = mat_qty * mat_price

                product_data["materials"].append({
                    "material_id": str(material.material_id),
                    "material_name": material.name,
                    "material_code": material.code,
                    "quantity_per_unit": mat_qty_per_unit,
                    "total_quantity": mat_qty,
                    "material_price": mat_price,
                    "total_price": mat_total
                })

            # Получаем спецификацию операций
            spec_ops = product.spec_operations
            for spec_op in spec_ops:
                operation = spec_op.operation
                time_norm = float(spec_op.time_norm)
                op_qty = float(spec_op.op_quantity)
                total_time = time_norm * op_qty * float(item.quantity)

                # Получаем цену операции
                price_stmt = select(OperationPrice).where(
                    OperationPrice.operation_id == spec_op.operation_id
                ).order_by(OperationPrice.effective_date.desc()).limit(1)
                price_record = db.session.execute(price_stmt).scalar_one_or_none()
                op_price = float(price_record.price) if price_record else 0.0
                op_total = total_time * op_price

                product_data["operations"].append({
                    "operation_id": str(operation.operation_id),
                    "operation_name": operation.name,
                    "operation_code": operation.code,
                    "time_norm": time_norm,
                    "op_quantity": op_qty,
                    "total_time": total_time,
                    "operation_price": op_price,
                    "total_price": op_total
                })

            result["items"].append(product_data)

        return result
