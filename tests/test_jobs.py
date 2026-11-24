import sqlite3

import pytest

from sorteos.fixtures import synthetic_comments
from sorteos.jobs import run_snapshot


def test_job_progress_and_failure(tmp_path):
    records = synthetic_comments(2, 1)
    job, path, count = run_snapshot(records + records, tmp_path, "demo")

    def interrupted():
        yield records[0]
        raise ValueError("entrada inválida")

    with pytest.raises(ValueError):
        run_snapshot(interrupted(), tmp_path, "demo")
    with sqlite3.connect(tmp_path / "trabajos.sqlite3") as db:
        assert db.execute("pragma journal_mode").fetchone() == ("wal",)
        assert db.execute(
            "select status,processed,unique_count,sha256 from jobs order by id"
        ).fetchall() == [
            ("completo", 4, count, path.stem),
            ("interrumpido", 1, None, None),
        ]


def test_resume_refuses_changed_prefix_then_recovers(tmp_path):
    rows = synthetic_comments(2, 42)

    def interrupted():
        yield rows[0]
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        run_snapshot(interrupted(), tmp_path, "misma")
    with pytest.raises(ValueError, match="prefijo"):
        run_snapshot(reversed(rows), tmp_path, "misma", resume=1)
    assert run_snapshot(rows, tmp_path, "misma", resume=1)[2] == 2
