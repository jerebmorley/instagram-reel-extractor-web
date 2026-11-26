"""Preparación del compromiso, cierre e historial de actas locales."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from sorteos.campaign import (
    commit_seed,
    freeze,
    milestones,
    parse_rules,
    read_record,
    register_evidence,
)
from sorteos.draw import draw
from sorteos.extraction import workspace
from sorteos.fixtures import prepare_demo_commitment
from sorteos.report import export, verify
from sorteos.review import effective_reviews, history


def show_act(directory):
    data = read_record(directory / "campana.db", "sorteo")
    path = directory / "acta.html"
    digest = export(data, path)
    result = verify(path, digest)
    st.subheader("Resultado del sorteo")
    for title, key in [("Ganadores", "ganadores"), ("Suplentes en orden", "suplentes")]:
        st.text(title + ": " + (", ".join(result[key]) or "ninguno"))
    st.caption("SHA-256 del acta")
    st.code(digest)
    st.download_button(
        "Descargar acta verificable",
        path.read_bytes(),
        "acta.html",
        "text/html",
        key=f"acta-{directory.name}",
    )


def draw_panel(draft):
    directory = workspace(draft)
    db = directory / "campana.db"
    stages = milestones(db)
    if "sorteo" in stages:
        show_act(directory)
        return
    rules = parse_rules(draft["reglas"])
    st.subheader("Compromiso de semilla")
    if draft["origen"] == "Campaña de prueba":
        if "evidencia" not in stages:
            st.caption("La demo usa una semilla fija y una publicación simulada.")
            if st.button("Preparar compromiso de prueba"):
                prepare_demo_commitment(db, draft)
                st.rerun()
            return
    else:
        if "compromiso" not in stages:
            if st.button("Generar compromiso antes del cierre"):
                commit_seed(db, rules.ends_at.isoformat())
                st.rerun()
            return
        st.caption("Publicá esta huella junto con las bases y el cierre de la campaña.")
        st.code(read_record(db, "compromiso")["sha256"])
        if "evidencia" not in stages:
            with st.form("evidencia"):
                ref = st.text_input("Referencia de la publicación")
                stamp = st.text_input(
                    "Fecha y hora de publicación con zona horaria",
                    placeholder="2026-11-26T12:00:00-03:00",
                )
                submitted = st.form_submit_button("Registrar publicación")
            if submitted:
                register_evidence(db, ref, stamp)
                st.rerun()
            return
    if datetime.now(timezone.utc) < rules.ends_at:
        st.info(f"El cierre de la campaña es {rules.ends_at.isoformat()}.")
        return
    if not (directory / "resultado").exists():
        return
    st.subheader("Cerrar el padrón y sortear")
    if "padron" not in stages:
        st.write("Al congelar se fijan los participantes y las revisiones vigentes.")
        if st.button("Congelar padrón"):
            snapshot = directory / (directory / "resultado").read_text()
            freeze(
                db,
                snapshot,
                rules,
                draft["identidad"],
                effective_reviews(history(directory)),
            )
            st.rerun()
        return
    count = len(read_record(db, "padron")["participants"])
    st.write(f"Padrón congelado: {count} participantes elegibles.")
    if not count:
        st.info("La campaña cerró sin participantes elegibles.")
        return
    with st.form("cupos"):
        winners = st.number_input(
            "Cantidad de ganadores", min_value=1, max_value=count, value=1
        )
        reserves = st.number_input("Cantidad de suplentes", min_value=0, value=0)
        submitted = st.form_submit_button("Realizar sorteo")
    if submitted:
        draw(db, winners, reserves)
        st.rerun()


def show_history():
    st.title("Historial de sorteos")
    completed = []
    for db in sorted(Path("exports/interfaz").glob("*/campana.db")):
        if "sorteo" in milestones(db):
            completed.append(db.parent)
    if not completed:
        st.info("Todavía no hay sorteos finalizados.")
        return

    def label(directory):
        config = json.loads((directory / "config.json").read_bytes())
        return f"@{config['cuenta']['username']} · {config['reglas']['ends_at']} · {directory.name[:8]}"

    selected = st.selectbox("Campaña finalizada", completed, format_func=label)
    show_act(selected)


def guarded(view, *args):
    try:
        view(*args)
    except (ValueError, OSError, sqlite3.Error) as exc:
        st.error(str(exc))
