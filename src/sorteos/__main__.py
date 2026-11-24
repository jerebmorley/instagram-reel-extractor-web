"""CLI local de diagnóstico."""

import argparse
import json
import os

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
    args = parser.parse_args()
    try:
        graph = Graph(args.version_api, os.getenv("INSTAGRAM_ACCESS_TOKEN", ""))
        if args.command == "perfil":
            result = graph.profile()
        elif args.command == "publicaciones":
            result = graph.media()
        else:
            result = graph.comments(args.id_publicacion)
    except GraphError as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
