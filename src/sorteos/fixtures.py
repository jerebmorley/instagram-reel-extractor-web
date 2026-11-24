"""Campañas sintéticas para pruebas y demos locales."""

from datetime import datetime, timedelta, timezone
from random import Random

from sorteos.models import Comment
from sorteos.rules import Rules

START = datetime(2026, 1, 1, tzinfo=timezone.utc)


def fixture_rules() -> Rules:
    return Rules(START, START + timedelta(days=1), {"bloqueada"}, 2, "tienda")


def synthetic_comments(count: int, seed: int) -> list[Comment]:
    if count < 0:
        raise ValueError("La cantidad debe ser no negativa.")
    rng = Random(seed)
    result = []
    for i in range(count):
        batch, case = divmod(i, 10)
        author = rng.randrange(max(2, count // 4))
        username = f"demo_{author}"
        text = "@amiga @vecino"
        if case == 1:
            text = f"@{username} @tienda"
        elif case == 2:
            text = "Promo https://ejemplo.invalid/@amiga @vecino @VECINO"
        elif case == 3:
            username = "bloqueada"
        # Diez filas comparten instante y publicación para simular ráfagas.
        at = START + timedelta(seconds=batch % 86400)
        result.append(
            Comment(
                id=f"c{i}",
                media_id=f"m{batch % 3}",
                text=text,
                created_at=START - timedelta(seconds=1) if case == 4 else at,
                author_id=None
                if case == 5
                else ("bloqueada" if case == 3 else str(author)),
                username=username,
                parent_id=f"c{i - 6}" if case == 6 else None,
            )
        )
    return result
