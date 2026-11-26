"""Acta HTML v1 autocontenida con datos para reproducir el sorteo."""

import base64
import hashlib
import json
import re
from html import escape
from pathlib import Path

from sorteos.campaign import canonical
from sorteos.draw import validate


def render(data):
    info = data["compromiso"]
    evidence = info["evidencia"]

    def listing(key):
        return (
            "<ol>"
            + "".join(f"<li>{escape(p)}</li>" for p in data["resultado"][key])
            + "</ol>"
        )

    payload = base64.b64encode(canonical(data)).decode("ascii")
    return f"""<!doctype html>
<html lang="es"><meta charset="utf-8"><title>Acta de sorteo</title>
<style>body{{font:1rem system-ui;max-width:48rem;margin:2rem auto}}code{{overflow-wrap:anywhere}}li{{break-inside:avoid}}</style>
<h1>Acta de sorteo</h1>
<p>Elegibles: {len(data["participantes"])} · Identidad: {escape(data["identidad"])}</p>
<h2>Ganadores</h2>{listing("ganadores")}
<h2>Suplentes en orden</h2>{listing("suplentes")}
<h2>Verificación</h2>
<p>Algoritmo: {escape(data["algoritmo"])}</p>
<p>Padrón: <code>{escape(data["padron_sha256"])}</code></p>
<p>Snapshot: <code>{escape(data["snapshot_sha256"])}</code></p>
<p>Semilla: <code>{escape(info["semilla"])}</code></p>
<p>Compromiso SHA-256: <code>{escape(info["sha256"])}</code></p>
<p>Referencia declarada: {escape(evidence["referencia"])}</p>
<p>Publicación: {escape(evidence["publicado"])} · Cierre: {escape(info["cierre"])}</p>
<script type="application/octet-stream" id="datos">{payload}</script></html>
""".encode()


def export(data, path: Path):
    content = render(data)
    # Publicación sin reemplazo, incluso si dos procesos exportan al mismo destino.
    import os
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
    try:
        temp.write_bytes(content)
        try:
            os.link(temp, path)
        except FileExistsError:
            if path.read_bytes() != content:
                raise ValueError("El destino ya contiene otro archivo.") from None
    finally:
        temp.unlink(missing_ok=True)
    return hashlib.sha256(content).hexdigest()


def verify(path, expected=None):
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if expected is not None and expected != digest:
        raise ValueError("El SHA-256 externo difiere del acta.")
    match = re.search(
        rb'<script type="application/octet-stream" id="datos">([A-Za-z0-9+/=]+)</script>',
        content,
    )
    if not match:
        raise ValueError("Faltan los datos verificables del acta.")
    data = json.loads(base64.b64decode(match[1], validate=True))
    validate(data)
    if render(data) != content:
        raise ValueError("El HTML difiere del acta reproducida.")
    return {"sha256": digest, **data["resultado"]}
