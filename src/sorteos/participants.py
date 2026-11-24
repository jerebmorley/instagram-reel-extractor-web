"""Consolidación determinista de una campaña completa."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from sorteos.mentions import normalize_username
from sorteos.models import Comment
from sorteos.rules import Rules, evaluate


@dataclass(frozen=True)
class Decision:
    media_id: str
    comment_id: str
    participant: str | None
    reasons: tuple[str, ...]

    @property
    def grants_entry(self) -> bool:
        return not self.reasons


def consolidate(
    comments: Iterable[Comment],
    rules: Rules,
    *,
    identity: Literal["id", "username"] = "id",
) -> tuple[Decision, ...]:
    """Una decisión por comentario único, con una sola clave de identidad por campaña."""
    if identity not in ("id", "username"):
        raise ValueError("Seleccioná id o username como identidad de campaña.")
    unique = {}
    for item in comments:
        key = (item.media_id, item.id)
        if unique.setdefault(key, item) != item:
            raise ValueError("Hay versiones contradictorias del mismo comentario.")

    seen = set()
    decisions = []
    for item in sorted(unique.values(), key=lambda c: (c.created_at, c.media_id, c.id)):
        participant = item.author_id
        if identity == "username":
            try:
                participant = normalize_username(item.username or "")
            except ValueError:
                participant = None
        reasons = list(evaluate(item, rules))
        if item.parent_id is not None:
            reasons.append("respuesta_no_admitida")
        if participant is None:
            reasons.append("identidad_no_disponible")
        if not reasons:
            if participant in seen:
                reasons.append("participante_ya_habilitado")
            else:
                seen.add(participant)
        decisions.append(Decision(item.media_id, item.id, participant, tuple(reasons)))
    return tuple(decisions)
