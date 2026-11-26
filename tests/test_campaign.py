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


def test_commit_publish_reveal(tmp_path, monkeypatch):
    import hashlib
    from datetime import datetime, timedelta, timezone

    from sorteos import campaign

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return now

    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(campaign, "datetime", Clock)
    db = tmp_path / "campaign.db"
    end = now + timedelta(days=1)
    info = campaign.commit_seed(db, end.isoformat())
    assert "semilla" not in info
    assert db.stat().st_mode & 0o077 == 0
    with pytest.raises(ValueError, match="ya existe"):
        campaign.commit_seed(db, end.isoformat())
    with pytest.raises(ValueError, match="cierre"):
        campaign.reveal(db)
    with pytest.raises(ValueError):
        campaign.register_evidence(db, "demo", end.isoformat())
    now += timedelta(hours=1)
    campaign.register_evidence(db, "referencia ficticia", now.isoformat())
    now = end
    result = campaign.reveal(db)
    assert (
        hashlib.sha256(bytes.fromhex(result["semilla"])).hexdigest() == info["sha256"]
    )
    assert result["evidencia"]["referencia"] == "referencia ficticia"
