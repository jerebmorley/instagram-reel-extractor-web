"""Trabajos de snapshot con puntos de continuación transaccionales."""

import fcntl
import json
import sqlite3
from contextlib import ExitStack, closing
from dataclasses import asdict
from pathlib import Path

from sorteos.graph_source import GraphSource
from sorteos.snapshot import write_snapshot
from sorteos.sources import parse_row


def encode(row):
    values = asdict(row)
    values["created_at"] = row.created_at.isoformat()
    return json.dumps(values, sort_keys=True)


def local_batches(records, previous):
    source = iter(records)
    for (expected,) in previous:
        row = next(source, None)
        if row is None or encode(row) != expected:
            raise ValueError("El prefijo de la fuente cambió desde la interrupción.")
    batch = []
    try:
        for row in source:
            batch.append(row)
            if len(batch) == 100:
                yield batch, {}
                batch = []
    except (Exception, KeyboardInterrupt):
        if batch:
            yield batch, {}
        raise
    if batch:
        yield batch, {}


def run_snapshot(records, directory: Path, origin: str, *, resume=None):
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    with ExitStack() as stack:
        db = stack.enter_context(
            closing(sqlite3.connect(directory / "trabajos.sqlite3"))
        )
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY, origin TEXT NOT NULL, status TEXT NOT NULL,
                processed INTEGER NOT NULL DEFAULT 0, unique_count INTEGER, sha256 TEXT
            );
            CREATE TABLE IF NOT EXISTS checkpoints(job INTEGER PRIMARY KEY, cursor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS staged(job INTEGER, pos INTEGER, payload TEXT NOT NULL,
                PRIMARY KEY(job,pos));
        """)
        with db:
            db.execute("BEGIN IMMEDIATE")
            if resume is None:
                job = db.execute(
                    "INSERT INTO jobs(origin,status) VALUES (?, 'activo')", (origin,)
                ).lastrowid
                db.execute("INSERT INTO checkpoints VALUES (?, 'null')", (job,))
            else:
                job = resume
            state = db.execute(
                """SELECT origin,status,processed,cursor FROM jobs
                JOIN checkpoints ON checkpoints.job=jobs.id WHERE jobs.id=?""",
                (job,),
            ).fetchone()
            if not state or state[0] != origin or state[1] == "completo":
                raise ValueError(
                    "El trabajo no es reanudable con esta fuente y destino."
                )
            lock = stack.enter_context((directory / f".trabajo-{job}.lock").open("a"))
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError("El trabajo ya está en ejecución.") from None
            db.execute("UPDATE jobs SET status='activo' WHERE id=?", (job,))

        processed = state[2]

        def saved():
            return db.execute(
                "SELECT payload FROM staged WHERE job=? ORDER BY pos", (job,)
            )

        try:
            batches = (
                records.batches(json.loads(state[3]))
                if isinstance(records, GraphSource)
                else local_batches(records, saved())
            )
            for rows, cursor in batches:
                with db:
                    db.executemany(
                        "INSERT INTO staged VALUES (?,?,?)",
                        (
                            (job, processed + i, encode(row))
                            for i, row in enumerate(rows)
                        ),
                    )
                    processed += len(rows)
                    db.execute(
                        "UPDATE jobs SET processed=? WHERE id=?", (processed, job)
                    )
                    db.execute(
                        "UPDATE checkpoints SET cursor=? WHERE job=?",
                        (json.dumps(cursor), job),
                    )
            comments = (
                parse_row(json.loads(payload), i, csv_input=False)
                for i, (payload,) in enumerate(saved(), 1)
            )
            path, count = write_snapshot(comments, directory)
            with db:
                db.execute(
                    "UPDATE jobs SET status='completo', unique_count=?, sha256=? WHERE id=?",
                    (count, path.stem, job),
                )
                db.execute("DELETE FROM staged WHERE job=?", (job,))
                db.execute("DELETE FROM checkpoints WHERE job=?", (job,))
        except (Exception, KeyboardInterrupt):
            with db:
                db.execute("UPDATE jobs SET status='interrumpido' WHERE id=?", (job,))
            raise
        return job, path, count
