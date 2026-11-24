"""Reglas de campaña aplicadas a un comentario por vez."""

from dataclasses import dataclass
from datetime import datetime, timezone

from sorteos.mentions import normalize_username
from sorteos.models import Comment


@dataclass(frozen=True)
class Rules:
    starts_at: datetime
    ends_at: datetime
    excluded_usernames: frozenset[str] = frozenset()

    def __post_init__(self):
        for field in ("starts_at", "ends_at"):
            value = getattr(self, field)
            if not isinstance(value, datetime) or value.utcoffset() is None:
                raise ValueError("La ventana requiere fechas con zona horaria.")
            object.__setattr__(self, field, value.astimezone(timezone.utc))
        if self.starts_at > self.ends_at:
            raise ValueError("El cierre debe ser igual o posterior al inicio.")
        if isinstance(self.excluded_usernames, str):
            raise ValueError("Se requiere una colección de cuentas excluidas.")
        names = frozenset(normalize_username(name) for name in self.excluded_usernames)
        object.__setattr__(self, "excluded_usernames", names)


def evaluate(comment: Comment, rules: Rules) -> tuple[str, ...]:
    """Una tupla vacía indica que pasó las reglas configuradas."""
    reasons = []
    if not rules.starts_at <= comment.created_at <= rules.ends_at:
        reasons.append("fuera_de_fecha")
    try:
        author = normalize_username(comment.username or "")
    except ValueError:
        author = None
    if rules.excluded_usernames:
        if author is None:
            reasons.append("autor_no_verificable")
        elif author in rules.excluded_usernames:
            reasons.append("autor_excluido")
    return tuple(reasons)
