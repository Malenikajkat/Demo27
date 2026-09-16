"""DTO для продукции."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ProductDTO:
    """DTO для продукции."""
    product_id: str
    name: str
    code: str
    created_at: Optional[str] = None

    @classmethod
    def from_model(cls, product) -> "ProductDTO":
        """Создать DTO из модели."""
        return cls(
            product_id=str(product.product_id), name=product.name,
            code=product.code, created_at=product.created_at.isoformat() if product.created_at else None,
        )

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)
