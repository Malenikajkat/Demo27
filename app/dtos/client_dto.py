"""DTO для клиента."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ClientDTO:
    """DTO для клиента."""
    client_id: str
    name: str
    inn: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    client_type: str = ""
    created_at: Optional[str] = None

    @classmethod
    def from_model(cls, client) -> "ClientDTO":
        """Создать DTO из модели."""
        return cls(
            client_id=str(client.client_id), name=client.name, inn=client.inn,
            address=client.address, phone=client.phone, client_type=client.client_type,
            created_at=client.created_at.isoformat() if client.created_at else None,
        )

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)
