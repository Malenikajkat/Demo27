"""DTO для материала."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class MaterialDTO:
    """DTO для материала."""
    material_id: str
    name: str
    code: str
    created_at: Optional[str] = None

    @classmethod
    def from_model(cls, material) -> "MaterialDTO":
        """Создать DTO из модели."""
        return cls(
            material_id=str(material.material_id), name=material.name,
            code=material.code, created_at=material.created_at.isoformat() if material.created_at else None,
        )

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)
