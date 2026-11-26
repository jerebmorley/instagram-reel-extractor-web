import time
from pathlib import Path

from streamlit.testing.v1 import AppTest

from sorteos.campaign import read_record
from sorteos.extraction import workspace
from sorteos.report import verify

APP = Path(__file__).resolve().parents[1] / "app" / "campana.py"


def click(app, label):
    next(b for b in app.button if b.label == label).click().run()
    assert not app.exception


def test_complete_demo_and_reopen_act_from_history(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = AppTest.from_file(str(APP)).run()
    click(app, "Aplicar configuración")
    directory = workspace(app.session_state["draft"])
    click(app, "Preparar compromiso de prueba")
    click(app, "Iniciar extracción")
    deadline = time.monotonic() + 10
    while not (directory / "resultado").exists():
        assert time.monotonic() < deadline
        time.sleep(0.05)
    app.run()
    click(app, "Congelar padrón")
    assert not any(b.label == "Registrar decisión" for b in app.button)
    next(w for w in app.number_input if w.label == "Cantidad de suplentes").set_value(1)
    click(app, "Realizar sorteo")
    result = verify(directory / "acta.html")
    assert len(result["ganadores"]) == len(result["suplentes"]) == 1
    assert (
        "simulada" in read_record(directory / "campana.db", "evidencia")["referencia"]
    )
    other = AppTest.from_file(str(APP)).run()
    other.checkbox[0].check().run()
    assert not other.exception
    assert other.code[0].value == result["sha256"]
