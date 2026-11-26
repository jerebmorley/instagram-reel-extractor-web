"""Registro local de una campaña. Cada hito se escribe una sola vez."""

import hashlib
import json
import os
import secrets
import sqlite3
from contextlib import closing
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from sorteos.participants import consolidate
from sorteos.rules import Rules
from sorteos.sources import parse_row


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def record(path, name, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.close(os.open(path, os.O_CREAT | os.O_WRONLY, 0o600))
    with closing(sqlite3.connect(path)) as db, db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS records(name TEXT PRIMARY KEY, data BLOB NOT NULL)"
        )
        db.execute("BEGIN IMMEDIATE")
        if name in ("padron", "compromiso"):
            other = "compromiso" if name == "padron" else "padron"
            existing = db.execute(
                "SELECT data FROM records WHERE name=?", (other,)
            ).fetchone()
            if existing:
                previous = json.loads(existing[0])
                roster, commitment = (
                    (value, previous) if name == "padron" else (previous, value)
                )
                if roster["rules"]["ends_at"] != commitment["cierre"]:
                    raise ValueError("El cierre del padrón difiere del compromiso.")
        try:
            db.execute("INSERT INTO records VALUES (?,?)", (name, canonical(value)))
        except sqlite3.IntegrityError:
            raise ValueError(f"El registro {name} ya existe en esta campaña.") from None


def read_snapshot(snapshot):
    raw = snapshot.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if snapshot.name != f"{digest}.jsonl":
        raise ValueError("El snapshot no coincide con su nombre SHA-256.")
    comments = [
        parse_row(json.loads(line), i, csv_input=False)
        for i, line in enumerate(raw.splitlines(), 1)
    ]
    return digest, comments


def freeze(database: Path, snapshot: Path, rules: Rules, identity, reviews):
    digest, comments = read_snapshot(snapshot)
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
    return parse_rules(json.loads(path.read_text(encoding="utf-8")))


def parse_rules(data):
    if not isinstance(data, dict):
        raise ValueError("Se esperaba un objeto de reglas.")
    data = dict(data)
    for key in ("starts_at", "ends_at"):
        data[key] = datetime.fromisoformat(data[key].replace("Z", "+00:00"))
    return Rules(**data)


def commitment_info(path):
    if not path.is_file():
        raise ValueError("Falta la campaña.")
    with closing(sqlite3.connect(path)) as db:
        row = db.execute("SELECT data FROM records WHERE name='compromiso'").fetchone()
    if not row:
        raise ValueError("Falta el compromiso de la campaña.")
    return json.loads(row[0])


def utc_date(value):
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.utcoffset() is None:
        raise ValueError("Indicá una fecha con zona horaria.")
    return stamp.astimezone(timezone.utc)


def commit_seed(path, closing_time):
    end = utc_date(closing_time)
    now = datetime.now(timezone.utc)
    if now >= end:
        raise ValueError("El compromiso debe generarse antes del cierre.")
    seed = secrets.token_hex(32)
    public = {
        "cierre": end.isoformat(),
        "creado": now.isoformat(),
        "sha256": hashlib.sha256(bytes.fromhex(seed)).hexdigest(),
    }
    record(path, "compromiso", dict(public, semilla=seed))
    return public


def register_evidence(path, reference, published):
    info = commitment_info(path)
    stamp = utc_date(published)
    if not reference.strip() or not (
        utc_date(info["creado"]) <= stamp < utc_date(info["cierre"])
        and stamp <= datetime.now(timezone.utc)
    ):
        raise ValueError(
            "Indicá una referencia y una publicación entre la creación y el cierre, ya ocurrida."
        )
    evidence = dict(
        referencia=reference, publicado=stamp.isoformat(), sha256=info["sha256"]
    )
    record(path, "evidencia", evidence)
    return evidence


def reveal(path):
    info = commitment_info(path)
    if datetime.now(timezone.utc) < utc_date(info["cierre"]):
        raise ValueError("La revelación requiere que haya pasado el cierre.")
    with closing(sqlite3.connect(path)) as db:
        evidence = db.execute(
            "SELECT data FROM records WHERE name='evidencia'"
        ).fetchone()
    if not evidence:
        raise ValueError("Falta registrar la evidencia pública.")
    if hashlib.sha256(bytes.fromhex(info["semilla"])).hexdigest() != info["sha256"]:
        raise ValueError("La semilla no coincide con el compromiso.")
    return dict(info, evidencia=json.loads(evidence[0]))


def milestones(path):
    """Devolver los nombres de los hitos persistidos de la campaña."""
    if not path.is_file():
        return set()
    with closing(sqlite3.connect(path)) as db:
        return {row[0] for row in db.execute("SELECT name FROM records")}


def read_record(path, name):
    with closing(sqlite3.connect(path)) as db:
        row = db.execute("SELECT data FROM records WHERE name=?", (name,)).fetchone()
    if not row:
        raise ValueError("Falta el registro de campaña solicitado.")
    return json.loads(row[0])
