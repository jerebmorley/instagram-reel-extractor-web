#!/usr/bin/env python3
import argparse
import csv
import getpass
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import instaloader
import requests

QUERY_HASH = "bc3296d1ce80a24b1b6e40b1e72903f5"
DEFAULT_OUTPUT_DIR = Path("exports")


def print_banner():
    print("=" * 70)
    print("Instagram Reel Comment Extractor")
    print("Flujo guiado para iniciar sesión, pegar un enlace de reel y exportar comentarios.")
    print("=" * 70)


def safe_input(prompt):
    try:
        return input(prompt)
    except EOFError:
        return ""


def parse_shortcode_from_url(url: str) -> str:
    if not url:
        raise ValueError("Debes ingresar una URL válida del reel.")

    cleaned = url.strip()
    match = re.search(r"/reel/([A-Za-z0-9_-]{11})/?", cleaned)
    if match:
        return match.group(1)

    parsed = urlparse(cleaned)
    if parsed.netloc:
        if parsed.path.startswith("/reel/"):
            parts = parsed.path.split("/")
            for part in parts:
                if len(part) == 11 and re.fullmatch(r"[A-Za-z0-9_-]+", part):
                    return part
    raise ValueError("La URL no parece ser un reel de Instagram. Usa algo como https://www.instagram.com/reel/XXXXXXXXXXX/")


def ensure_session(username: str, password: str) -> instaloader.Instaloader:
    loader = instaloader.Instaloader()
    loader.context.log_level = "INFO"

    try:
        loader.load_session_from_file(username)
        print(f"Sesión cargada para usuario: {username}")
        return loader
    except FileNotFoundError:
        pass

    print(f"Iniciando sesión en Instagram como {username}...")
    try:
        loader.login(username, password)
    except instaloader.exceptions.BadCredentialsException:
        raise ValueError("Credenciales incorrectas. Verifica usuario y contraseña.")
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        raise ValueError("Instagram requiere autenticación en dos pasos. Este script no la soporta automáticamente.")
    except instaloader.exceptions.InvalidArgumentException:
        raise ValueError("El nombre de usuario no es válido.")
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"No se pudo iniciar sesión. Error: {exc}")

    loader.save_session_to_file()
    print("Sesión guardada correctamente en disco.")
    return loader


def export_comments(shortcode: str, loader: instaloader.Instaloader, output_file: Path) -> int:
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
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        print(f"Reel detectado. Media ID: {post.mediaid}")
        print(f"Comentarios reportados por Instagram: {post.comments}")
    except Exception as exc:
        raise RuntimeError(f"No se pudo acceder al reel '{shortcode}'. Verifica que la URL sea válida o que tengas permisos. Error: {exc}")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "username", "text", "created_at", "likes_count"]

    with output_file.open("w", newline="", encoding="utf-8-sig") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=fieldnames)
        writer.writeheader()

        end_cursor = None
        has_next_page = True
        total_descargados = 0
        print("Descargando comentarios...")

        while has_next_page:
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
                print("Límite de velocidad alcanzado. Esperando 60 segundos antes de reintentar...")
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
                print("No se encontraron comentarios en este reel.")
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

            archivo.flush()
            print(f"Comentarios guardados: {total_descargados}", end="\r")

            page_info = edge_media.get("page_info", {})
            has_next_page = page_info.get("has_next_page", False)
            end_cursor = page_info.get("end_cursor")

            if has_next_page:
                time.sleep(1.8)

    print(f"\nProceso finalizado. Total de comentarios exportados: {total_descargados}")
    print(f"Archivo generado: {output_file}")
    return total_descargados


def run_interactive_flow(username: str | None = None, password: str | None = None, reel_url: str | None = None):
    if username is None:
        username = safe_input("Usuario de Instagram: ").strip()
    if not username:
        raise ValueError("El usuario no puede estar vacío.")

    if password is None:
        password = getpass.getpass("Contraseña de Instagram: ")
    if not password:
        raise ValueError("La contraseña no puede estar vacía.")

    loader = ensure_session(username, password)

    if reel_url is None:
        reel_url = safe_input("Pega la URL del reel: ").strip()
    shortcode = parse_shortcode_from_url(reel_url)

    output_path = DEFAULT_OUTPUT_DIR / f"comentarios_{shortcode}.csv"
    print(f"Se guardará la exportación en: {output_path}")
    export_comments(shortcode, loader, output_path)


def parse_args():
    parser = argparse.ArgumentParser(description="Extrae comentarios de un reel de Instagram con un flujo guiado.")
    parser.add_argument("--username", help="Usuario de Instagram")
    parser.add_argument("--password", help="Contraseña de Instagram")
    parser.add_argument("--reel-url", help="URL del reel a analizar")
    parser.add_argument("--output", help="Ruta del archivo CSV de salida (opcional)")
    return parser.parse_args()


def main():
    args = parse_args()
    print_banner()

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = DEFAULT_OUTPUT_DIR

    try:
        if args.username or args.password or args.reel_url:
            if not args.username:
                raise ValueError("Si usas argumentos de línea de comandos, debe indicar --username.")
            if not args.password:
                raise ValueError("Si usas argumentos de línea de comandos, debe indicar --password.")
            if not args.reel_url:
                raise ValueError("Si usas argumentos de línea de comandos, debe indicar --reel-url.")

            loader = ensure_session(args.username, args.password)
            shortcode = parse_shortcode_from_url(args.reel_url)
            target = output_path if output_path.suffix.lower() == ".csv" else output_path / f"comentarios_{shortcode}.csv"
            export_comments(shortcode, loader, target)
            return 0

        run_interactive_flow()
        return 0
    except KeyboardInterrupt:
        print("\nProceso cancelado por el usuario.")
        return 130
    except ValueError as exc:
        print(f"\nError: {exc}")
        return 1
    except RuntimeError as exc:
        print(f"\nError al extraer comentarios: {exc}")
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"\nOcurrió un error inesperado: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())