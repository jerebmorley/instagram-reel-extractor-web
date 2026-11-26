"""Controles de extracción y revisión del asistente local."""

import json
import sqlite3
from datetime import datetime, timezone

import streamlit as st

from sorteos.campaign import milestones, read_snapshot, utc_date
from sorteos.extraction import job_rows, launch, running, workspace
from sorteos.review import add_review, effective_reviews, history, inspection


def extraction_panel(draft):
    directory = workspace(draft)
    st.subheader("Extracción")
    finished = directory / "resultado"
    busy = running(directory)
    jobs = job_rows(directory)
    if (
        draft["origen"] == "Cuenta autorizada"
        and not jobs
        and not busy
        and datetime.now(timezone.utc) < utc_date(draft["reglas"]["ends_at"])
    ):
        st.info("La extracción para el sorteo estará disponible después del cierre.")
        return
    if not finished.exists():
        if busy:
            st.info("Extracción en curso.")
        else:
            error = directory / "error"
            if error.exists():
                st.error(error.read_text())
            if st.button("Continuar extracción" if jobs else "Iniciar extracción"):
                launch(draft, directory)
                st.rerun()
        st.button("Actualizar progreso")
    if jobs:
        st.dataframe(
            [
                {
                    "Publicación": j["origin"],
                    "Estado": j["status"],
                    "Comentarios leídos": j["processed"],
                }
                for j in jobs
            ],
            hide_index=True,
        )
    if not finished.exists():
        return
    path = directory / finished.read_text()
    _, comments = read_snapshot(path)
    rows = inspection(comments, draft)
    st.subheader("Revisión de participantes")
    if not rows:
        st.info("Las publicaciones seleccionadas no tienen comentarios.")
        return
    scope = st.radio(
        "Mostrar comentarios", ["Descartados", "Con alerta", "Todos"], horizontal=True
    )
    visible = [
        r
        for r in rows
        if scope == "Todos" or (r["alerta"] if scope == "Con alerta" else r["motivos"])
    ]
    if visible:
        st.dataframe(visible, hide_index=True)
    else:
        st.info("No hay comentarios en esta vista.")
    known = sorted({r["participante"] for r in rows if r["participante"]})
    if known and "padron" not in milestones(directory / "campana.db"):
        with st.form(f"revision-{directory.name}", clear_on_submit=True):
            person = st.selectbox("Participante", known)
            action = st.radio(
                "Decisión manual", ["excluir", "incluir"], horizontal=True
            )
            reason = st.text_input("Motivo de la excepción")
            save = st.form_submit_button("Registrar decisión")
        if save:
            try:
                add_review(directory, person, action, reason, known)
                st.success("Decisión registrada.")
            except ValueError as exc:
                st.error(str(exc))
    log = history(directory)
    if log:
        st.write("Registro de decisiones (UTC)")
        st.dataframe(log, hide_index=True)
        st.download_button(
            "Descargar revisiones vigentes",
            json.dumps(effective_reviews(log), ensure_ascii=False),
            "revisiones.json",
            "application/json",
        )


def render_extraction(draft):
    try:
        extraction_panel(draft)
    except (OSError, ValueError, sqlite3.Error) as exc:
        st.error(f"No se pudo cargar la extracción: {exc}")
