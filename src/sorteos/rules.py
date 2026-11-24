"""Reglas de campaña aplicadas a un comentario por vez."""

from dataclasses import dataclass
from datetime import datetime, timezone

from sorteos.mentions import mentions, normalize_username
from sorteos.models import Comment


@dataclass(frozen=True)
class Rules:
    starts_at: datetime
    ends_at: datetime
    excluded_usernames: frozenset[str] = frozenset()

    required_mentions: int = 0
    business_username: str | None = None

    def __post_init__(self):
        if type(self.required_mentions) is not int or self.required_mentions < 0:
            raise ValueError("La cantidad de menciones debe ser un entero no negativo.")
        if self.required_mentions and self.business_username is None:
            raise ValueError("Indicá la cuenta del comercio para evaluar menciones.")
        if self.business_username is not None:
            object.__setattr__(
                self, "business_username", normalize_username(self.business_username)
            )
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
    if author is None and (rules.excluded_usernames or rules.required_mentions):
        reasons.append("autor_no_verificable")
    if author in rules.excluded_usernames:
        reasons.append("autor_excluido")
    if rules.required_mentions:
        candidates = set(mentions(comment.text)) - {author, rules.business_username}
        if len(candidates) < rules.required_mentions:
            reasons.append("menciones_insuficientes")
    return tuple(reasons)
