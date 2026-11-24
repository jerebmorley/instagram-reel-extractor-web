"""CLI local de diagnóstico."""

import argparse
import csv
import json
import os
from datetime import date
from pathlib import Path

from sorteos.credentials import CredentialError, credential_path, load_token, save_token
from sorteos.graph import Graph, GraphError
from sorteos.jobs import run_snapshot
from sorteos.sources import FileSource, FixtureSource


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version-api", help="Versión del panel de Meta")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("perfil", help="Identificar la cuenta autorizada")
    commands.add_parser("publicaciones", help="Listar una muestra de publicaciones")
    comments = commands.add_parser(
        "comentarios", help="Inspeccionar comentarios y respuestas"
    )
    comments.add_argument("id_publicacion")
    save = commands.add_parser(
        "guardar-token", help="Validar y reemplazar la cuenta activa"
    )
    save.add_argument(
        "--vence", type=date.fromisoformat, help="Primer día sin acceso, AAAA-MM-DD"
    )
    snapshot = commands.add_parser("snapshot", help="Crear un JSONL canónico local")
    source = snapshot.add_mutually_exclusive_group(required=True)
    source.add_argument("--archivo", type=Path)
    source.add_argument("--sinteticos", type=int, metavar="CANTIDAD")
    snapshot.add_argument("--semilla", type=int)
    snapshot.add_argument("--destino", type=Path, default=Path("exports/snapshots"))
    args = parser.parse_args()
    if args.command == "snapshot":
        if args.archivo and args.semilla is not None:
            parser.error("--semilla requiere --sinteticos")
        seed = 16 if args.semilla is None else args.semilla
        try:
            if args.archivo:
                records = FileSource(args.archivo)
                origin = str(args.archivo)
            else:
                records = FixtureSource(args.sinteticos, seed)
                origin = f"sintéticos: cantidad={args.sinteticos}, semilla={seed}"
            job, path, count = run_snapshot(records, args.destino, origin)
        except (ValueError, OSError, csv.Error) as error:
            parser.exit(1, f"No se pudo crear el snapshot: {error}\n")
        print(
            json.dumps(
                {
                    "trabajo": job,
                    "archivo": str(path),
                    "sha256": path.stem,
                    "comentarios": count,
                    "origen": origin,
                }
            )
        )
        return
    if not args.version_api:
        parser.error("Este comando requiere --version-api")
    try:
        token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        if args.command == "guardar-token":
            graph = Graph(args.version_api, token or "")
            profile = graph.profile()
            save_token(
                credential_path(), token, args.vence.isoformat() if args.vence else None
            )
            print(json.dumps({"cuenta_guardada": profile["username"]}))
            return
        graph = Graph(args.version_api, token or load_token(credential_path()))
        if args.command == "perfil":
            result = graph.profile()
        elif args.command == "publicaciones":
            result = graph.media()
        else:
            result = graph.comments(args.id_publicacion)
    except (GraphError, CredentialError) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
