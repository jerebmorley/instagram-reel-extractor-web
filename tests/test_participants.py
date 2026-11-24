from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from sorteos.models import Comment
from sorteos.participants import consolidate
from sorteos.rules import Rules

START = datetime(2026, 1, 1, tzinfo=timezone.utc)
RULES = Rules(
    START, START + timedelta(days=1), required_mentions=2, business_username="tienda"
)
ROOT = Comment("1", "a", "@uno @dos", START, "u1", "Ana")


def test_one_entry_across_media_even_after_rename_and_replay():
    other = replace(ROOT, media_id="b", username="otro_nombre")
    rows = [other, ROOT, ROOT]
    result = consolidate(rows, RULES)
    assert result == consolidate(reversed(rows), RULES)
    assert [d.reasons for d in result] == [(), ("participante_ya_habilitado",)]


def test_invalid_comments_do_not_combine_or_consume_entry():
    rows = [
        replace(ROOT, id="0", parent_id="padre"),
        replace(ROOT, text="@uno"),
        replace(ROOT, id="2", text="@dos"),
        replace(ROOT, id="3"),
    ]
    assert [d.reasons for d in consolidate(rows, RULES)] == [
        ("respuesta_no_admitida",),
        ("menciones_insuficientes",),
        ("menciones_insuficientes",),
        (),
    ]


def test_identity_policy_is_uniform():
    missing = replace(ROOT, id="2", author_id=None, username="ANA")
    assert consolidate([missing], RULES)[0].reasons == ("identidad_no_disponible",)
    assert [
        d.grants_entry for d in consolidate([missing, ROOT], RULES, identity="username")
    ] == [True, False]


def test_conflicting_duplicate_requires_resolution():
    with pytest.raises(ValueError, match="contradictorias"):
        consolidate([ROOT, replace(ROOT, text="otro")], RULES)
