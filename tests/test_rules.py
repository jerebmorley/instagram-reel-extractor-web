from datetime import datetime, timedelta, timezone

import pytest

from sorteos.models import Comment
from sorteos.rules import Rules, evaluate

START = datetime(2026, 11, 24, tzinfo=timezone(timedelta(hours=-3)))
END = START + timedelta(days=1)


def comment(at=START, username="Ana", text=""):
    return Comment("c1", "m1", text, at, username=username)


@pytest.mark.parametrize("at", [START, END])
def test_inclusive_window(at):
    assert evaluate(comment(at.astimezone(timezone.utc)), Rules(START, END)) == ()


@pytest.mark.parametrize(
    "at", [START - timedelta(microseconds=1), END + timedelta(microseconds=1)]
)
def test_reports_all_reasons(at):
    assert evaluate(comment(at), Rules(START, END, {"@ANA"})) == (
        "fuera_de_fecha",
        "autor_excluido",
    )


def test_missing_author_only_matters_for_active_exclusion():
    assert evaluate(comment(username=None), Rules(START, END)) == ()
    assert evaluate(comment(username=None), Rules(START, END, {"ana"})) == (
        "autor_no_verificable",
    )


@pytest.mark.parametrize(
    "start", [END + timedelta(seconds=1), START.replace(tzinfo=None)]
)
def test_invalid_window(start):
    with pytest.raises(ValueError):
        Rules(start, END)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("@ANA @tienda @Luis @LUIS.", ("menciones_insuficientes",)),
        ("@Ana @tienda @Luis @Sol", ()),
        (
            "correo@ejemplo.com https://ejemplo.com/@luis @Sol",
            ("menciones_insuficientes",),
        ),
    ],
)
def test_required_distinct_mentions(text, expected):
    rules = Rules(START, END, required_mentions=2, business_username="@TIENDA")
    assert evaluate(comment(text=text), rules) == expected


def test_unknown_author_cannot_pass_self_mention_check():
    rules = Rules(START, END, {"bloqueada"}, 1, "tienda")
    assert evaluate(comment(username=None, text="@ana"), rules) == (
        "autor_no_verificable",
    )


@pytest.mark.parametrize(
    ("count", "business"), [(-1, "demo"), (True, "demo"), (1, None)]
)
def test_invalid_mention_rules(count, business):
    with pytest.raises(ValueError):
        Rules(START, END, required_mentions=count, business_username=business)
