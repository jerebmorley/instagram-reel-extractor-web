"""Configuración local de campañas de sorteos."""

import json
import os
from datetime import date, datetime, time, timedelta, timezone

import streamlit as st
from extraccion import render_extraction
from sorteo import draw_panel, guarded, show_history

from sorteos.credentials import CredentialError, credential_path, load_token
from sorteos.fixtures import fixture_rules, synthetic_comments
from sorteos.graph import Graph, GraphError
from sorteos.participants import consolidate
from sorteos.rules import Rules


def clear_draft():
    st.session_state.pop("draft", None)


def clear_account():
    clear_draft()
    st.session_state.pop("account", None)


def main():
    st.set_page_config(page_title="Preparar sorteo", layout="centered")
    if st.sidebar.checkbox("Ver historial de sorteos"):
        guarded(show_history)
        return
    st.title("Preparar sorteo")
    mode = st.radio(
        "Origen de los comentarios",
        ["Campaña de prueba", "Cuenta autorizada"],
        on_change=clear_account,
        horizontal=True,
    )
    demo = mode == "Campaña de prueba"
    if demo:
        rows = synthetic_comments(100, 16)
        profile = {"id": "demo", "username": "tienda"}
        options = {
            key: f"Publicación de prueba {key}"
            for key in sorted({r.media_id for r in rows})
        }
        st.caption("Cuenta @tienda · 100 comentarios ficticios · 1 de enero de 2026")
    else:
        version = st.text_input(
            "Versión de API indicada en el panel de Meta",
            placeholder="vN.N",
            on_change=clear_account,
        )
        if st.button("Cargar cuenta"):
            clear_account()
            try:
                token = os.getenv("INSTAGRAM_ACCESS_TOKEN") or load_token(
                    credential_path()
                )
                client = Graph(version, token)
                profile = client.profile()
                listing = client.media()
                st.session_state.account = (profile, listing)
            except (GraphError, CredentialError) as exc:
                st.error(str(exc))
        if "account" not in st.session_state:
            st.info(
                "Configurá la credencial local y cargá la cuenta para elegir publicaciones."
            )
            return
        profile, listing = st.session_state.account
        options = {
            p[
                "id"
            ]: f"{p['media_product_type'] or p['media_type'] or 'Publicación'} · {p['id']}"
            for p in listing["publicaciones"]
            if p.get("id")
        }
        st.text(f"Cuenta activa: @{profile['username']}")
        if listing["hay_mas"]:
            st.caption("Se muestran las primeras diez publicaciones de la cuenta.")
    if not options:
        st.info("Esta cuenta no devolvió publicaciones para seleccionar.")
        return
    template = fixture_rules()
    today = template.starts_at.date() if demo else date.today()
    with st.form(f"campaign-{mode}-{profile['id']}"):
        selected = st.multiselect(
            "Publicaciones",
            list(options),
            default=list(options) if demo else [],
            format_func=options.get,
        )
        left, right = st.columns(2)
        start = left.date_input("Primer día (UTC)", today)
        end = right.date_input(
            "Último día incluido (UTC)", today if demo else today + timedelta(days=7)
        )
        minimum = st.number_input(
            "Personas distintas que hay que mencionar",
            min_value=0,
            value=template.required_mentions,
        )
        excluded = st.text_input(
            "Cuentas excluidas, separadas por comas", value="bloqueada" if demo else ""
        )
        identity = st.selectbox("Identificar participantes por", ["id", "username"])
        submitted = st.form_submit_button("Aplicar configuración")
    if submitted:
        clear_draft()
        try:
            if not selected:
                raise ValueError("Seleccioná al menos una publicación.")
            rules = Rules(
                datetime.combine(start, time.min, timezone.utc),
                datetime.combine(end, time.max, timezone.utc),
                frozenset(x.strip() for x in excluded.split(",") if x.strip()),
                minimum,
                profile["username"],
            )
            draft = dict(
                origen=mode,
                cuenta=profile,
                publicaciones=selected,
                identidad=identity,
                reglas=dict(
                    starts_at=rules.starts_at.isoformat(),
                    ends_at=rules.ends_at.isoformat(),
                    excluded_usernames=sorted(rules.excluded_usernames),
                    required_mentions=rules.required_mentions,
                    business_username=rules.business_username,
                ),
            )
            if demo:
                decisions = consolidate(
                    (r for r in rows if r.media_id in selected),
                    rules,
                    identity=identity,
                )
                draft["vista_previa"] = dict(
                    comentarios=len(decisions),
                    elegibles=sum(d.grants_entry for d in decisions),
                )
            else:
                draft["version_api"] = version
            st.session_state.draft = draft
        except ValueError as exc:
            st.error(str(exc))
    if "draft" in st.session_state:
        draft = st.session_state.draft
        st.subheader("Configuración aplicada")
        st.write(
            f"{len(draft['publicaciones'])} publicaciones · {draft['reglas']['required_mentions']} menciones requeridas"
        )
        if "vista_previa" in draft:
            summary = draft["vista_previa"]
            st.write(
                f"{summary['elegibles']} participantes elegibles de {summary['comentarios']} comentarios."
            )
        st.download_button(
            "Descargar configuración",
            json.dumps(draft, ensure_ascii=False, indent=2),
            "campana.json",
            "application/json",
        )

        render_extraction(draft)
        guarded(draw_panel, draft)


main()
