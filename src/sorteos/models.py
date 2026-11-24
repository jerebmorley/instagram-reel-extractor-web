"""Contrato compartido por las futuras fuentes de comentarios."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Comment:
    """Un comentario raíz o una respuesta. Los identificadores son opacos."""

    id: str
    media_id: str
    text: str
    created_at: datetime
    author_id: str | None = None
    username: str | None = None
    parent_id: str | None = None

    def __post_init__(self):
        for field in ("id", "media_id", "author_id", "username", "parent_id"):
            value = getattr(self, field)
            if value is None and field not in ("id", "media_id"):
                continue
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} requiere una cadena con contenido.")
        if self.parent_id == self.id:
            raise ValueError("Un comentario no puede ser su propia raíz.")
        if not isinstance(self.text, str):
            raise ValueError("text requiere una cadena.")
        if (
            not isinstance(self.created_at, datetime)
            or self.created_at.utcoffset() is None
        ):
            raise ValueError("created_at requiere fecha y hora con zona horaria.")
        object.__setattr__(self, "created_at", self.created_at.astimezone(timezone.utc))
