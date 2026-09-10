from __future__ import annotations

import csv
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse

import instaloader
import requests
from flask import Flask, jsonify, render_template, request, send_from_directory, url_for


BASE_DIR = Path(__file__).resolve().parent
EXPORTS_DIR = BASE_DIR / "exports"
STATUS_FILE = BASE_DIR / "status.json"
HISTORY_FILE = BASE_DIR / "history.json"
QUERY_HASH = "bc3296d1ce80a24b1b6e40b1e72903f5"

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "public" / "static"),
    static_url_path="/static",
)
status_lock = Lock()


def default_status():
    return {
        "status": "idle",
        "step": "login",
        "percent": 0,
        "message": "Listo para iniciar.",
        "error": "",
    }


def write_status(data: dict) -> None:
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_status() -> dict:
    if not STATUS_FILE.exists():
        return default_status()
    try:
        content = STATUS_FILE.read_text(encoding="utf-8")
        if not content.strip():
            return default_status()
        data = json.loads(content)
        merged = default_status()
        merged.update(data)
        return merged
    except json.JSONDecodeError:
        return default_status()


def set_status(step: str, percent: int, message: str, status: str = "running", error: str = "") -> None:
    payload = {
        "status": status,
        "step": step,
        "percent": max(0, min(100, percent)),
        "message": message,
        "error": error,
    }
    with status_lock:
        write_status(payload)


def reset_status() -> None:
    set_status("login", 0, "Listo para iniciar.", status="idle")


def read_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        content = HISTORY_FILE.read_text(encoding="utf-8")
        if not content.strip():
            return []
        history = json.loads(content)
        return history if isinstance(history, list) else []
    except json.JSONDecodeError:
        return []


def save_history(entry: dict) -> None:
    history = read_history()
    history.insert(0, entry)
    history = history[:8]
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_shortcode(url: str) -> str:
    if not url or not url.strip():
        raise ValueError("Debes ingresar una URL del reel.")

    cleaned = url.strip()
    match = re.search(r"/reel/([A-Za-z0-9_-]{11})/?", cleaned)
    if match:
        return match.group(1)

    parsed = urlparse(cleaned)
    if parsed.netloc and parsed.path.startswith("/reel/"):
        parts = parsed.path.split("/")
        for part in parts:
            if len(part) == 11 and re.fullmatch(r"[A-Za-z0-9_-]+", part):
                return part

    raise ValueError("La URL no parece ser un reel válido. Usa algo como https://www.instagram.com/reel/XXXXXXXXXXX/")


def ensure_session(username: str, password: str) -> instaloader.Instaloader:
    loader = instaloader.Instaloader()
    try:
        loader.load_session_from_file(username)
        return loader
    except FileNotFoundError:
        pass

    try:
        loader.login(username, password)
        loader.save_session_to_file()
        return loader
    except instaloader.exceptions.BadCredentialsException as exc:
        raise ValueError("Credenciales incorrectas. Revisá usuario y contraseña.") from exc
    except instaloader.exceptions.TwoFactorAuthRequiredException as exc:
        raise ValueError("Instagram requiere autenticación en dos pasos. Esta versión no la soporta automáticamente.") from exc
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"No pudo iniciarse la sesión: {exc}") from exc


def export_comments(shortcode: str, loader: instaloader.Instaloader, progress_callback=None) -> tuple[int, Path]:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = EXPORTS_DIR / f"comentarios_{shortcode}.csv"

    if progress_callback:
        progress_callback("validation", 35, "Reel validado. Preparando la extracción.")

    session = loader.context._session
    cookies = session.cookies.get_dict()
    csrf_token = cookies.get("csrftoken", "")

    headers = {
        "User-Agent": "Mozilla/5.0 (X-UA-Compatible; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "X-CSRFToken": csrf_token,
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.instagram.com/reel/{shortcode}/",
        "Accept": "*/*",
    }

    try:
        instaloader.Post.from_shortcode(loader.context, shortcode)
    except Exception as exc:
        raise RuntimeError(f"No se pudo acceder al reel '{shortcode}'. Verificá la URL o los permisos. Error: {exc}") from exc

    with output_file.open("w", newline="", encoding="utf-8-sig") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=["id", "username", "text", "created_at", "likes_count"])
        writer.writeheader()

        end_cursor = None
        has_next_page = True
        total_descargados = 0
        page_index = 0

        if progress_callback:
            progress_callback("extracting", 45, "Descargando comentarios del reel...")

        while has_next_page:
            page_index += 1
            variables = {"shortcode": shortcode, "first": 50}
            if end_cursor:
                variables["after"] = end_cursor

            params = {
                "query_hash": QUERY_HASH,
                "variables": json.dumps(variables, separators=(",", ":")),
            }

            response = requests.get(
                "https://www.instagram.com/graphql/query/",
                headers=headers,
                cookies=cookies,
                params=params,
                timeout=30,
            )

            if response.status_code == 429:
                if progress_callback:
                    progress_callback("extracting", max(45, min(90, 50 + page_index * 8)), "Límite temporal de Instagram. Reintentando en 60 segundos...")
                time.sleep(60)
                continue
            if response.status_code != 200:
                raise RuntimeError(f"Instagram respondió con estado {response.status_code}: {response.text[:300]}")

            payload = response.json()
            edge_media = (
                payload.get("data", {})
                .get("shortcode_media", {})
                .get("edge_media_to_parent_comment", {})
            )
            edges = edge_media.get("edges", [])

            if not edges:
                break

            for edge in edges:
                node = edge.get("node", {})
                owner = node.get("owner", {})
                writer.writerow({
                    "id": node.get("id", ""),
                    "username": owner.get("username", ""),
                    "text": node.get("text", "").replace("\n", " "),
                    "created_at": node.get("created_at", ""),
                    "likes_count": node.get("edge_liked_by", {}).get("count", 0),
                })
                total_descargados += 1

            if progress_callback:
                progress_callback("extracting", min(95, 55 + page_index * 8), f"Comentarios descargados: {total_descargados}")

            page_info = edge_media.get("page_info", {})
            has_next_page = page_info.get("has_next_page", False)
            end_cursor = page_info.get("end_cursor")

            if has_next_page:
                time.sleep(1.5)

    if progress_callback:
        progress_callback("saving", 98, "Guardando exportación final...")

    return total_descargados, output_file


@app.route("/")
def index():
    return render_template("index.html", history=read_history())


@app.route("/api/status")
def api_status():
    return jsonify(read_status())


@app.route("/api/history")
def api_history():
    return jsonify(read_history())


@app.route("/api/extract", methods=["POST"])
def api_extract():
    payload = request.get_json(silent=True) or request.form.to_dict()
    username = (payload.get("username") or "").strip()
    password = (payload.get("password") or "").strip()
    reel_url = (payload.get("reel_url") or "").strip()

    try:
        if not username or not password:
            raise ValueError("Completa usuario y contraseña.")
        if not reel_url:
            raise ValueError("Pegá la URL del reel.")

        set_status("login", 15, "Iniciando sesión en Instagram...")
        shortcode = parse_shortcode(reel_url)
        loader = ensure_session(username, password)

        set_status("validation", 30, "Validando acceso al reel...")
        total, output_file = export_comments(shortcode, loader, progress_callback=set_status)
        download_url = url_for("download_file", filename=output_file.name)

        # Guardar historial
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        save_history({
            "timestamp": now,
            "shortcode": shortcode,
            "username": username,
            "file_name": output_file.name,
            "total": total,
            "download_url": download_url,
        })

        set_status("done", 100, f"Listo. Se exportaron {total} comentarios.", status="done")
        return jsonify({
            "success": True,
            "shortcode": shortcode,
            "total": total,
            "file_name": output_file.name,
            "download_url": download_url,
        })
    except Exception as exc:
        set_status("error", 100, str(exc), status="error", error=str(exc))
        return jsonify({"success": False, "error": str(exc)}), 400


@app.route("/download/<filename>")
def download_file(filename: str):
    return send_from_directory(EXPORTS_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    reset_status()
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
