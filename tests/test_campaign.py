import json
import sqlite3

import pytest

from sorteos.campaign import freeze
from sorteos.fixtures import fixture_rules, synthetic_comments
from sorteos.snapshot import write_snapshot


def test_freeze_records_override_and_refuses_replacement(tmp_path):
    comments = synthetic_comments(1, 16)
    path, _ = write_snapshot(comments, tmp_path)
    db = tmp_path / "campaign.db"
    reviews = [
        {
            "participante": comments[0].author_id,
            "decision": "excluir",
            "motivo": "Renuncia",
        }
    ]
    assert freeze(db, path, fixture_rules(), "id", reviews)["elegibles"] == 0
    with sqlite3.connect(db) as con:
        padron = json.loads(
            con.execute("SELECT data FROM records WHERE name='padron'").fetchone()[0]
        )
    assert padron["reviews"] == reviews and padron["decisions"][0]["reasons"] == []
    with pytest.raises(ValueError, match="ya existe"):
        freeze(db, path, fixture_rules(), "id", [])
    path.write_bytes(b"")
    with pytest.raises(ValueError, match="SHA-256"):
        freeze(db, path, fixture_rules(), "id", [])
