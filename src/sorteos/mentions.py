"""Convenciones de menciones para las reglas locales de campaña."""

import re
import unicodedata

_URL = re.compile(r"(?i)(?:[a-z][a-z0-9+.-]*://|\bwww\.|\b[\w.-]+\.[a-z]{2,}/)[^\s<>]*")
_NAME = re.compile(r"[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*")
_CANDIDATE = re.compile(r"(?<![\w@./+%-])@([\w.\u0300-\u036f]+)")


def normalize_username(value: str) -> str:
    name = value.strip().removeprefix("@")
    if len(name) > 30 or not _NAME.fullmatch(name):
        raise ValueError("Nombre de cuenta inválido.")
    return name.lower()


def mentions(text: str) -> tuple[str, ...]:
    """Devuelve cuentas distintas en orden de aparición."""
    clean = _URL.sub(" ", text)
    found = {}
    for match in _CANDIDATE.finditer(clean):
        following = clean[match.end() : match.end() + 1]
        if following and unicodedata.category(following).startswith("M"):
            continue
        try:
            name = normalize_username(match[1].rstrip("."))
        except ValueError:
            continue
        found[name] = None
    return tuple(found)
