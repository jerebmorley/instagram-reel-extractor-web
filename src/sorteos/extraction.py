"""Coordinación local de una extracción por configuración aplicada."""

import fcntl
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

from sorteos.campaign import canonical, read_snapshot
from sorteos.credentials import CredentialError, credential_path, load_token
from sorteos.fixtures import synthetic_comments
from sorteos.graph import Graph, GraphError
from sorteos.graph_source import GraphSource
from sorteos.jobs import run_snapshot
from sorteos.snapshot import write_snapshot


def workspace(draft, base=Path("exports/interfaz")):
    return base / hashlib.sha256(canonical(draft)).hexdigest()


def job_rows(directory):
    path = directory / "trabajos.sqlite3"
    if not path.exists():
        return []
    with closing(sqlite3.connect(path)) as db:
        db.row_factory = sqlite3.Row
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='jobs'").fetchone():
            return []
        return [dict(row) for row in db.execute("SELECT * FROM jobs ORDER BY id")]


def running(directory):
    path = directory / "worker.lock"
    if not path.exists():
        return False
    with path.open("rb") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
    return False


def launch(draft, directory):
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (directory / "worker.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return None
        if (directory / "resultado").exists():
            return None
        (directory / "config.json").write_bytes(canonical(draft))
        (directory / "error").unlink(missing_ok=True)
        return subprocess.Popen(
            [sys.executable, "-m", "sorteos.extraction", str(directory.resolve())],
            pass_fds=(lock.fileno(),),
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def extract(directory):
    draft = json.loads((directory / "config.json").read_bytes())
    client = None
    if draft["origen"] == "Cuenta autorizada":
        token = os.getenv("INSTAGRAM_ACCESS_TOKEN") or load_token(credential_path())
        client = Graph(draft["version_api"], token)
        if client.profile()["id"] != draft["cuenta"]["id"]:
            raise ValueError("La credencial corresponde a otra cuenta.")
    previous = {row["origin"]: row for row in job_rows(directory)}
    paths = []
    for media in draft["publicaciones"]:
        job = previous.get(media)
        if job and job["status"] == "completo":
            paths.append(directory / (job["sha256"] + ".jsonl"))
            continue
        records = (
            GraphSource(client, media)
            if client
            else (r for r in synthetic_comments(100, 16) if r.media_id == media)
        )
        _, path, _ = run_snapshot(
            records, directory, media, resume=job["id"] if job else None
        )
        paths.append(path)
    combined, _ = write_snapshot(
        (r for path in paths for r in read_snapshot(path)[1]), directory
    )
    temp = directory / "resultado.tmp"
    temp.write_text(combined.name)
    temp.replace(directory / "resultado")


if __name__ == "__main__":
    target = Path(sys.argv[1])
    try:
        extract(target)
    except (GraphError, CredentialError, ValueError, OSError, sqlite3.Error) as exc:
        (target / "error").write_text(str(exc), encoding="utf-8")
        sys.exit(1)
