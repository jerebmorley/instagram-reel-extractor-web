import hashlib
import json
import subprocess
import sys

import pytest

from sorteos.campaign import freeze, record
from sorteos.draw import select
from sorteos.fixtures import fixture_rules, synthetic_comments
from sorteos.snapshot import write_snapshot


def test_ranking_is_independent_of_input_order():
    seed = "00" * 32
    people = ["c", "a", "b"]
    ranked = sorted(
        people, key=lambda p: hashlib.sha256(bytes(32) + p.encode()).hexdigest()
    )
    expected = {"ganadores": ranked[:1], "suplentes": ranked[1:]}
    assert select(people, seed, 1, 2) == select(people[::-1], seed, 1, 2) == expected
    for population, winners, alternates in [
        (["a", "a"], 1, 0),
        (people, 0, 1),
        (people, 2, 2),
    ]:
        with pytest.raises(ValueError):
            select(population, seed, winners, alternates)


def test_export_and_independent_verification(tmp_path):
    db = tmp_path / "demo.db"
    rules = fixture_rules()
    snap, _ = write_snapshot(synthetic_comments(100, 16), tmp_path)
    freeze(db, snap, rules, "id", [])
    seed = "ab" * 32
    digest = hashlib.sha256(bytes.fromhex(seed)).hexdigest()
    created = "2025-12-01T00:00:00+00:00"
    record(
        db,
        "compromiso",
        dict(
            semilla=seed,
            sha256=digest,
            creado=created,
            cierre=rules.ends_at.isoformat(),
        ),
    )
    record(db, "evidencia", dict(sha256=digest, publicado=created, referencia="<demo>"))
    path = tmp_path / "acta.html"
    cli = [sys.executable, "-m", "sorteos"]
    args = [*cli, "sortear", str(db), str(path), "--ganadores", "2", "--suplentes", "1"]
    output = json.loads(subprocess.check_output(args))
    assert json.loads(subprocess.check_output(args)) == output
    assert subprocess.run(args[:-1] + ["2"], capture_output=True).returncode == 1
    db.unlink()
    assert (
        json.loads(
            subprocess.check_output(
                [*cli, "verify", path, "--sha256", output["sha256"]]
            )
        )
        == output
    )
    html = path.read_bytes()
    assert b"&lt;demo&gt;" in html
    path.write_bytes(html.replace(b"<h2>Ganadores", b"<h2>Alterado"))
    assert subprocess.run([*cli, "verify", path], capture_output=True).returncode == 1
