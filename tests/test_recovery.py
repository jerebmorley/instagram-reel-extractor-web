import json
import sqlite3
import subprocess
import sys
from unittest.mock import Mock

import pytest

from sorteos.graph import GraphError
from sorteos.graph_source import GraphSource
from sorteos.jobs import run_snapshot


def test_process_loss_halfway_through_10000(tmp_path):
    child = """
import os, sys
from pathlib import Path
from sorteos.jobs import run_snapshot
from sorteos.sources import FixtureSource

def interrupted():
    for i, row in enumerate(FixtureSource(10000, 16)):
        if i == 5000:
            os._exit(77)
        yield row

run_snapshot(interrupted(), Path(sys.argv[1]), "sintéticos: cantidad=10000, semilla=16")
"""
    dest = tmp_path / "recovery"
    assert subprocess.run([sys.executable, "-c", child, str(dest)]).returncode == 77
    with sqlite3.connect(dest / "trabajos.sqlite3") as db:
        assert db.execute("SELECT status,processed FROM jobs").fetchone() == (
            "activo",
            5000,
        )
    base = [
        sys.executable,
        "-m",
        "sorteos",
        "snapshot",
        "--sinteticos",
        "10000",
        "--destino",
    ]
    restored = json.loads(
        subprocess.check_output([*base, str(dest), "--reanudar", "1"])
    )
    other = tmp_path / "complete"
    complete = json.loads(subprocess.check_output([*base, str(other)]))
    assert restored["trabajo"] == 1
    assert restored["comentarios"] == complete["comentarios"] == 10000
    assert restored["sha256"] == complete["sha256"]
    assert (
        next(dest.glob("*.jsonl")).read_bytes()
        == next(other.glob("*.jsonl")).read_bytes()
    )
    with sqlite3.connect(dest / "trabajos.sqlite3") as db:
        assert db.execute("SELECT status,processed FROM jobs").fetchall() == [
            ("completo", 10000)
        ]


def test_graph_resumes_from_pending_reply_page(tmp_path):
    graph = Mock()

    def page(id):
        return {
            "data": [{"id": id, "timestamp": "2026-01-01T00:00:00Z", "text": "demo"}]
        }

    graph.read.side_effect = [
        page("1"),
        dict(page("2"), paging={"next": "ignored", "cursors": {"after": "r2"}}),
        GraphError("corte"),
    ]
    with pytest.raises(GraphError):
        run_snapshot(GraphSource(graph, "100"), tmp_path, "demo")
    recovered = Mock()
    recovered.read.side_effect = [page("3")]
    _, path, count = run_snapshot(
        GraphSource(recovered, "100"), tmp_path, "demo", resume=1
    )
    assert count == 3
    assert recovered.read.call_count == 1
    call = recovered.read.call_args
    assert (call.args[0], call.kwargs["after"]) == ("1/replies", "r2")
    assert [
        json.loads(line)["parent_id"] for line in path.read_text().splitlines()
    ] == [None, "1", "1"]
