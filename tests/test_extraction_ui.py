import time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from sorteos.campaign import read_snapshot
from sorteos.extraction import job_rows, launch, workspace
from sorteos.review import add_review, effective_reviews, history, inspection

APP = Path(__file__).resolve().parents[1] / "app" / "campana.py"


def test_ui_worker_and_persistent_review(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = AppTest.from_file(str(APP)).run()
    app.button[0].click().run()
    draft = app.session_state["draft"]
    directory = workspace(draft)
    next(b for b in app.button if b.label == "Iniciar extracción").click().run()
    deadline = time.monotonic() + 10
    while not (directory / "resultado").exists():
        assert time.monotonic() < deadline
        time.sleep(0.05)
    app.run()
    assert not app.exception
    jobs = job_rows(directory)
    assert len(jobs) == 3 and sum(j["unique_count"] for j in jobs) == 100
    assert launch(draft, directory) is None
    assert job_rows(directory) == jobs
    app.radio[-2].set_value("Con alerta").run()
    assert not app.exception
    app.text_input[-1].set_value("Renuncia en la demo")
    next(b for b in app.button if b.label == "Registrar decisión").click().run()
    log = history(directory)
    assert len(log) == 1 and log[0]["motivo"] == "Renuncia en la demo"
    digest, comments = read_snapshot(directory / (directory / "resultado").read_text())
    rows = inspection(comments, draft)
    assert any(r["alerta"] and not r["motivos"] for r in rows)
    known = {r["participante"] for r in rows}
    with pytest.raises(ValueError):
        add_review(directory, log[0]["participante"], "incluir", " ", known)
    add_review(directory, log[0]["participante"], "incluir", "Corrección", known)
    log = history(directory)
    assert len(log) == 2
    assert effective_reviews(log) == [
        {
            "participante": log[0]["participante"],
            "decision": "incluir",
            "motivo": "Corrección",
        }
    ]
