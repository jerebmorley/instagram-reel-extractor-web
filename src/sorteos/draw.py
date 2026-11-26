"""Selección reproducible sobre el padrón congelado."""

import hashlib
import json
import re
import sqlite3
from contextlib import closing

from sorteos.campaign import canonical, record, reveal, utc_date

ALGORITHM = "sha256-seed32-id-utf8-v1"


def select(participants, seed, winners, alternates):
    if not isinstance(seed, str) or not re.fullmatch("[a-f0-9]{64}", seed):
        raise ValueError("Semilla inválida.")
    if not isinstance(participants, list) or not all(
        isinstance(p, str) and p.strip() for p in participants
    ):
        raise ValueError("El padrón requiere identidades válidas.")
    if len(set(participants)) != len(participants):
        raise ValueError("Identidades duplicadas en el padrón.")
    if (
        type(winners) is not int
        or type(alternates) is not int
        or winners < 1
        or alternates < 0
        or winners + alternates > len(participants)
    ):
        raise ValueError("Cupos inválidos para la cantidad de elegibles.")
    prefix = bytes.fromhex(seed)

    def rank(person):
        identity = person.encode("utf-8")
        return hashlib.sha256(prefix + identity).digest(), identity

    ranked = sorted(participants, key=rank)
    return {
        "ganadores": ranked[:winners],
        "suplentes": ranked[winners : winners + alternates],
    }


def validate(data):
    if data["algoritmo"] != ALGORITHM or data["version"] != 1:
        raise ValueError("Versión de acta desconocida.")
    info = data["compromiso"]
    evidence = info["evidencia"]
    result = select(
        data["participantes"],
        info["semilla"],
        data["cupos_ganadores"],
        data["cupos_suplentes"],
    )
    digest = hashlib.sha256(bytes.fromhex(info["semilla"])).hexdigest()
    if digest != info["sha256"] or digest != evidence["sha256"]:
        raise ValueError("La semilla difiere del compromiso.")
    if not (
        evidence["referencia"].strip()
        and utc_date(info["creado"])
        <= utc_date(evidence["publicado"])
        < utc_date(info["cierre"])
    ):
        raise ValueError("Evidencia de compromiso inconsistente.")
    if result != data["resultado"]:
        raise ValueError("Los resultados difieren del ranking reproducido.")


def draw(database, winners, alternates, *, require_follow=False):
    info = reveal(database)
    with closing(sqlite3.connect(database)) as db:
        row = db.execute("SELECT data FROM records WHERE name='padron'").fetchone()
    if not row:
        raise ValueError("Primero congelá el padrón.")
    roster = json.loads(row[0])
    data = dict(
        version=1,
        algoritmo=ALGORITHM,
        participantes=roster["participants"],
        identidad=roster["identity"],
        snapshot_sha256=roster["snapshot_sha256"],
        padron_sha256=hashlib.sha256(canonical(roster)).hexdigest(),
        compromiso=info,
        cupos_ganadores=winners,
        cupos_suplentes=alternates,
        resultado=select(roster["participants"], info["semilla"], winners, alternates),
    )
    if require_follow:
        data["requiere_seguimiento"] = True
    validate(data)
    # Un reintento puede volver a exportar el mismo sorteo tras un error de disco.
    with closing(sqlite3.connect(database)) as db:
        previous = db.execute("SELECT data FROM records WHERE name='sorteo'").fetchone()
    if previous:
        if previous[0] != canonical(data):
            raise ValueError("Ya existe un sorteo con otros datos en esta campaña.")
    else:
        record(database, "sorteo", data)
    return data
