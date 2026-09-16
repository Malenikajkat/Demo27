"""DTO для заметки."""
from dataclasses import dataclass
from app.utils import format_note_id, format_date


@dataclass
class NoteDTO:
    """DTO для заметки."""
    id: str
    title_user: str
    content: str
    formatted_date: str

    @classmethod
    def from_model(cls, note, login: str) -> "NoteDTO":
        """Создать DTO из модели."""
        return cls(
            id=format_note_id(note.note_id),
            title_user=f"{note.title} - {login}",
            content=note.content,
            formatted_date=format_date(note.created_at),
        )
