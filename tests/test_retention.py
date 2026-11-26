import fcntl

import pytest

from sorteos.campaign import canonical
from sorteos.extraction import workspace
from sorteos.retention import cleanup


def campaign(end):
    draft = {"reglas": {"ends_at": end}}
    path = workspace(draft)
    path.mkdir(parents=True)
    (path / "config.json").write_bytes(canonical(draft))
    (path / "worker.lock").touch()
    return path


def test_preview_and_delete_one_expired_campaign(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    old = campaign("2020-01-01T00:00:00+00:00")
    current = campaign("2099-01-01T00:00:00+00:00")
    assert {r["estado"] for r in cleanup(90)} == {"vencida", "vigente"}
    with pytest.raises(ValueError):
        cleanup(90, current.name)
    with (old / "worker.lock").open() as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        with pytest.raises(ValueError, match="en curso"):
            cleanup(90, old.name)
    outside = tmp_path / "otro"
    outside.write_text("privado")
    (old / "enlace").symlink_to(outside)
    assert cleanup(90, old.name)[0]["estado"] == "eliminada"
    assert not old.exists() and current.exists() and outside.read_text() == "privado"


def test_reject_path_and_changed_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError):
        cleanup(90, "../")
    old = campaign("2020-01-01T00:00:00+00:00")
    (old / "config.json").write_text("{}")
    with pytest.raises(ValueError):
        cleanup(90, old.name)
    assert old.exists()
