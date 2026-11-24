"""API для спецификаций."""
import uuid
from flask import request, Blueprint
from app.views.base_view import BaseAPIView
from app.models import SpecificationMaterial, SpecificationOperation, MaterialPrice, OperationPrice
from app.extensions import db
from sqlalchemy import select

specifications_bp = Blueprint("specifications", __name__)


class SpecificationMaterialListAPI(BaseAPIView):
    """Список и создание спецификаций материалов."""

    def get(self):
        """Список спецификаций материалов с наименованиями и ценами."""
        specs = db.session.execute(db.select(SpecificationMaterial)).scalars().all()
        specs_list = []
        for s in specs:
            # Получаем текущую цену материала
            price_stmt = select(MaterialPrice).where(
                MaterialPrice.material_id == s.material_id
            ).order_by(MaterialPrice.effective_date.desc()).limit(1)
            price_record = db.session.execute(price_stmt).scalar_one_or_none()
            material_price = float(price_record.price) if price_record else 0.0

            specs_list.append({
                "spec_mat_id": str(s.spec_mat_id),
                "product_id": str(s.product_id),
                "product_name": s.product.name if s.product else "",
                "product_code": s.product.code if s.product else "",
                "material_id": str(s.material_id),
                "material_name": s.material.name if s.material else "",
                "material_code": s.material.code if s.material else "",
                "quantity_per_unit": float(s.quantity_per_unit),
                "material_price": material_price,
                "total_price": float(s.quantity_per_unit) * material_price
            })
        return self._success_response({"specifications": specs_list})

    def post(self):
        """Создание спецификации."""
        data = request.get_json()
        if not data or "product_id" not in data or "material_id" not in data or "quantity_per_unit" not in data:
            return self._error_response("Укажите product_id, material_id, quantity_per_unit")

        try:
            product_uuid = uuid.UUID(data["product_id"])
            material_uuid = uuid.UUID(data["material_id"])
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        new_spec = SpecificationMaterial(
            product_id=product_uuid, material_id=material_uuid,
            quantity_per_unit=data["quantity_per_unit"]
        )
        db.session.add(new_spec)
        db.session.commit()
        return self._success_response(
            {"message": "Спецификация создана", "spec_mat_id": str(new_spec.spec_mat_id)}, 201
        )


class SpecificationOperationListAPI(BaseAPIView):
    """Список и создание спецификаций операций."""

    def get(self):
        """Список спецификаций операций с наименованиями и ценами."""
        specs = db.session.execute(db.select(SpecificationOperation)).scalars().all()
        specs_list = []
        for s in specs:
            # Получаем текущую цену операции
            price_stmt = select(OperationPrice).where(
                OperationPrice.operation_id == s.operation_id
            ).order_by(OperationPrice.effective_date.desc()).limit(1)
            price_record = db.session.execute(price_stmt).scalar_one_or_none()
            operation_price = float(price_record.price) if price_record else 0.0

            specs_list.append({
                "spec_op_id": str(s.spec_op_id),
                "product_id": str(s.product_id),
                "product_name": s.product.name if s.product else "",
                "product_code": s.product.code if s.product else "",
                "operation_id": str(s.operation_id),
                "operation_name": s.operation.name if s.operation else "",
                "operation_code": s.operation.code if s.operation else "",
                "time_norm": float(s.time_norm),
                "op_quantity": float(s.op_quantity),
                "operation_price": operation_price,
                "total_price": float(s.time_norm) * float(s.op_quantity) * operation_price
            })
        return self._success_response({"specifications": specs_list})

    def post(self):
        """Создание спецификации."""
        data = request.get_json()
        if not data or "product_id" not in data or "operation_id" not in data:
            return self._error_response("Укажите product_id и operation_id")

        try:
            product_uuid = uuid.UUID(data["product_id"])
            operation_uuid = uuid.UUID(data["operation_id"])
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        new_spec = SpecificationOperation(
            product_id=product_uuid, operation_id=operation_uuid,
            time_norm=data.get("time_norm", 1.0),
            op_quantity=data.get("op_quantity", 1.0)
        )
        db.session.add(new_spec)
        db.session.commit()
        return self._success_response(
            {"message": "Спецификация создана", "spec_op_id": str(new_spec.spec_op_id)}, 201
        )


specifications_bp.add_url_rule("/materials/", view_func=SpecificationMaterialListAPI.as_view("spec_materials_list"))
specifications_bp.add_url_rule("/operations/", view_func=SpecificationOperationListAPI.as_view("spec_operations_list"))
