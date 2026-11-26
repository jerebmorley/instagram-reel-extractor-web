"""Alertas informativas y bitácora de decisiones por participante."""

import sqlite3
from collections import Counter
from contextlib import closing

from sorteos.campaign import parse_rules
from sorteos.participants import consolidate


def inspection(comments, draft):
    decisions = consolidate(
        comments, parse_rules(draft["reglas"]), identity=draft["identidad"]
    )
    # Una repetición literal del mismo autor es una señal para inspección manual.
    texts = {(r.media_id, r.id): r.text for r in comments}
    repeated = Counter(
        (d.participant, texts[d.media_id, d.comment_id]) for d in decisions
    )
    rows = []
    for d in decisions:
        text = texts[d.media_id, d.comment_id]
        alert = bool(
            d.participant and text.strip() and repeated[d.participant, text] > 1
        )
        rows.append(
            dict(
                participante=d.participant,
                publicacion=d.media_id,
                comentario=d.comment_id,
                texto=text,
                motivos=", ".join(d.reasons),
                alerta="Texto repetido por la cuenta" if alert else "",
            )
        )
    return rows


def add_review(directory, participant, decision, reason, known):
    if (
        participant not in known
        or not participant
        or decision not in ("incluir", "excluir")
        or not reason.strip()
    ):
        raise ValueError("Elegí una identidad observada, una decisión y un motivo.")
    with closing(sqlite3.connect(directory / "revision.sqlite3")) as db, db:
        db.execute("""CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY, fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            participante TEXT NOT NULL, decision TEXT NOT NULL, motivo TEXT NOT NULL)""")
        db.execute(
            "INSERT INTO reviews(participante,decision,motivo) VALUES (?,?,?)",
            (participant, decision, reason.strip()),
        )


def history(directory):
    path = directory / "revision.sqlite3"
    if not path.is_file():
        return []
    with closing(sqlite3.connect(path)) as db:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute("SELECT * FROM reviews ORDER BY id")]


def effective_reviews(log):
    latest = {r["participante"]: r for r in log}
    return [
        {k: latest[p][k] for k in ("participante", "decision", "motivo")}
        for p in sorted(latest)
    ]
