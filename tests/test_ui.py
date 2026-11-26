from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app" / "campana.py"


def test_demo_and_invalid_selection():
    app = AppTest.from_file(str(APP)).run()
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["draft"]["vista_previa"]["comentarios"] == 100
    app.multiselect[0].set_value([])
    app.button[0].click().run()
    assert "Seleccioná" in app.error[0].value
    assert "draft" not in app.session_state


def test_live_rerun_reuses_catalog(monkeypatch):
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "synthetic-test")
    with (
        patch(
            "sorteos.graph.Graph.profile", return_value={"id": "1", "username": "demo"}
        ) as profile,
        patch(
            "sorteos.graph.Graph.media",
            return_value={
                "publicaciones": [
                    {"id": "10", "media_type": "IMAGE", "media_product_type": None}
                ],
                "hay_mas": False,
            },
        ) as media,
    ):
        app = AppTest.from_file(str(APP)).run()
        app.radio[0].set_value("Cuenta autorizada").run()
        app.text_input[0].set_value("v25.0").run()
        app.button[0].click().run()
        app.multiselect[0].set_value(["10"])
        app.button[1].click().run()
        assert not app.exception
        assert app.session_state["draft"]["publicaciones"] == ["10"]
        profile.assert_called_once()
        media.assert_called_once()


def test_account_without_posts(monkeypatch):
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "synthetic-test")
    with (
        patch(
            "sorteos.graph.Graph.profile", return_value={"id": "1", "username": "demo"}
        ),
        patch(
            "sorteos.graph.Graph.media",
            return_value={"publicaciones": [], "hay_mas": False},
        ),
    ):
        app = AppTest.from_file(str(APP)).run()
        app.radio[0].set_value("Cuenta autorizada").run()
        app.text_input[0].set_value("v25.0").run()
        app.button[0].click().run()
        assert "no devolvió publicaciones" in app.info[0].value
        assert not app.multiselect
