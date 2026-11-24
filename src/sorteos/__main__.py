"""CLI local de diagnóstico."""

import argparse
import json
import os
from datetime import date

from sorteos.credentials import CredentialError, credential_path, load_token, save_token
from sorteos.graph import Graph, GraphError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version-api", required=True, help="Versión del panel de Meta"
    )
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
    args = parser.parse_args()
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
