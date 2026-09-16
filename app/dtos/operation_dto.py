"""DTO для операции."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class OperationDTO:
    """DTO для операции."""
    operation_id: str
    name: str
    code: str
    created_at: Optional[str] = None

    @classmethod
    def from_model(cls, operation) -> "OperationDTO":
        """Создать DTO из модели."""
        return cls(
            operation_id=str(operation.operation_id), name=operation.name,
            code=operation.code, created_at=operation.created_at.isoformat() if operation.created_at else None,
        )

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)
