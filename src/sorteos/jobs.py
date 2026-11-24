"""Registro local de trabajos de snapshot."""

import sqlite3
from contextlib import closing
from pathlib import Path

from sorteos.snapshot import write_snapshot


def run_snapshot(records, directory: Path, origin: str):
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    with closing(sqlite3.connect(directory / "trabajos.sqlite3")) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("""CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY, origin TEXT NOT NULL, status TEXT NOT NULL,
            processed INTEGER NOT NULL DEFAULT 0, unique_count INTEGER, sha256 TEXT
        )""")
        with db:
            job = db.execute(
                "INSERT INTO jobs(origin,status) VALUES (?, 'activo')", (origin,)
            ).lastrowid
        processed = 0

        def tracked():
            nonlocal processed
            for row in records:
                processed += 1
                if processed % 100 == 0:
                    with db:
                        db.execute(
                            "UPDATE jobs SET processed=? WHERE id=?", (processed, job)
                        )
                yield row

        try:
            path, count = write_snapshot(tracked(), directory)
        except (Exception, KeyboardInterrupt):
            with db:
                db.execute(
                    "UPDATE jobs SET status='interrumpido', processed=? WHERE id=?",
                    (processed, job),
                )
            raise
        with db:
            db.execute(
                "UPDATE jobs SET status='completo', processed=?, unique_count=?, sha256=? WHERE id=?",
                (processed, count, path.stem, job),
            )
        return job, path, count
