"""DTO для спецификаций."""
from dataclasses import dataclass, asdict


@dataclass
class SpecificationMaterialDTO:
    """DTO для спецификации материала."""
    spec_mat_id: str
    product_id: str
    material_id: str
    quantity_per_unit: float

    @classmethod
    def from_model(cls, spec) -> "SpecificationMaterialDTO":
        """Создать DTO из модели."""
        return cls(
            spec_mat_id=str(spec.spec_mat_id), product_id=str(spec.product_id),
            material_id=str(spec.material_id), quantity_per_unit=float(spec.quantity_per_unit),
        )

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)


@dataclass
class SpecificationOperationDTO:
    """DTO для спецификации операции."""
    spec_op_id: str
    product_id: str
    operation_id: str
    time_norm: float
    op_quantity: float

    @classmethod
    def from_model(cls, spec) -> "SpecificationOperationDTO":
        """Создать DTO из модели."""
        return cls(
            spec_op_id=str(spec.spec_op_id), product_id=str(spec.product_id),
            operation_id=str(spec.operation_id), time_norm=float(spec.time_norm),
            op_quantity=float(spec.op_quantity),
        )

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)
