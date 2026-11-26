"""Registro local de una campaña. Cada hito se escribe una sola vez."""

import hashlib
import json
import sqlite3
from contextlib import closing
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from sorteos.participants import consolidate
from sorteos.rules import Rules
from sorteos.sources import parse_row


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def record(path, name, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as db, db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS records(name TEXT PRIMARY KEY, data BLOB NOT NULL)"
        )
        try:
            db.execute("INSERT INTO records VALUES (?,?)", (name, canonical(value)))
        except sqlite3.IntegrityError:
            raise ValueError(f"El registro {name} ya existe en esta campaña.") from None


def freeze(database: Path, snapshot: Path, rules: Rules, identity, reviews):
    raw = snapshot.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if snapshot.name != f"{digest}.jsonl":
        raise ValueError("El snapshot no coincide con su nombre SHA-256.")
    comments = [
        parse_row(json.loads(line), i, csv_input=False)
        for i, line in enumerate(raw.splitlines(), 1)
    ]
    decisions = consolidate(comments, rules, identity=identity)
    known = {d.participant for d in decisions if d.participant is not None}
    eligible = {d.participant for d in decisions if d.grants_entry}
    if not isinstance(reviews, list):
        raise ValueError("Las revisiones deben ser una lista.")
    reviewed = set()
    for review in reviews:
        if not isinstance(review, dict) or set(review) != {
            "participante",
            "decision",
            "motivo",
        }:
            raise ValueError("Cada revisión requiere participante, decision y motivo.")
        person = review["participante"]
        if not isinstance(person, str) or person not in known or person in reviewed:
            raise ValueError("Participante desconocido o revisión duplicada.")
        if not isinstance(review["motivo"], str) or not review["motivo"].strip():
            raise ValueError("La revisión requiere un motivo.")
        reviewed.add(person)
        if review["decision"] == "incluir":
            eligible.add(person)
        elif review["decision"] == "excluir":
            eligible.discard(person)
        else:
            raise ValueError("Decisión manual desconocida.")
    config = dict(
        asdict(rules),
        starts_at=rules.starts_at.isoformat(),
        ends_at=rules.ends_at.isoformat(),
        excluded_usernames=sorted(rules.excluded_usernames),
    )
    payload = dict(
        version=1,
        snapshot_sha256=digest,
        identity=identity,
        rules=config,
        decisions=[asdict(d) for d in decisions],
        reviews=sorted(reviews, key=lambda r: r["participante"]),
        participants=sorted(eligible),
    )
    record(database, "padron", payload)
    return {
        "elegibles": len(eligible),
        "sha256": hashlib.sha256(canonical(payload)).hexdigest(),
    }


def load_rules(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Se esperaba un objeto de reglas.")
    for key in ("starts_at", "ends_at"):
        data[key] = datetime.fromisoformat(data[key].replace("Z", "+00:00"))
    return Rules(**data)
