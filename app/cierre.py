"""Controles y reporte de una campaña sorteada."""

import json

import streamlit as st

from sorteos.campaign import milestones, read_record, read_snapshot
from sorteos.finalists import confirm_finalists
from sorteos.summary import csv_report, summary


def finalist_panel(directory, data, act_hash):
    db = directory / "campana.db"
    if data.get("requiere_seguimiento"):
        st.subheader("Control manual de seguimiento")
        if "finalistas" not in milestones(db):
            with st.form(f"finalistas-{directory.name}"):
                cutoff = st.text_input(
                    "Fecha de corte con zona horaria",
                    placeholder="2026-11-26T18:00:00-03:00",
                )
                checks = {}
                for person in (
                    data["resultado"]["ganadores"] + data["resultado"]["suplentes"]
                ):
                    state = st.selectbox(
                        f"Seguimiento de {person}", ["pendiente", "sigue", "no sigue"]
                    )
                    reason = st.text_input(f"Motivo del control de {person}")
                    checks[person] = [state, reason]
                submit = st.form_submit_button("Confirmar controles y suplencias")
            if submit:
                confirm_finalists(db, cutoff, checks)
                st.rerun()
        else:
            annex = dict(read_record(db, "finalistas"), acta_sha256=act_hash)
            st.write("Fecha de corte", annex["corte"])
            st.write("Ganadores confirmados", annex["ganadores_confirmados"])
            st.write("Vacantes pendientes", annex["vacantes"])
            st.download_button(
                "Descargar anexo del acta",
                json.dumps(annex, ensure_ascii=False, indent=2),
                "finalistas.json",
                "application/json",
            )


def campaign_report(directory):
    db = directory / "campana.db"
    st.subheader("Reporte de campaña")
    roster = read_record(db, "padron")
    _, comments = read_snapshot(directory / (roster["snapshot_sha256"] + ".jsonl"))
    draft = json.loads((directory / "config.json").read_bytes())
    ref_file = directory / "conteos.json"
    report = summary(
        roster,
        comments,
        draft["publicaciones"],
        json.loads(ref_file.read_bytes()) if ref_file.exists() else {},
    )
    st.dataframe([report["resumen"]], hide_index=True)
    with st.expander("Motivos de descarte, menciones y actividad diaria"):
        st.write("Descartes por motivo", report["descartes"])
        st.write("Cuentas mencionadas", report["menciones"])
        st.write("Comentarios por día (UTC)", report["por_dia"])
    st.write("Cobertura por publicación")
    st.dataframe(report["cobertura"], hide_index=True)
    st.caption(
        "La referencia incluye respuestas y corresponde al momento indicado. Dos conteos iguales pueden contener comentarios distintos."
    )
    st.download_button(
        "Descargar reporte CSV", csv_report(report), "reporte.csv", "text/csv"
    )
