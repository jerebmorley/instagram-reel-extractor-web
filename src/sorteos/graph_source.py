"""Lectura paginada de una publicación autorizada."""

import re
from dataclasses import dataclass

from sorteos.graph import Graph, GraphError
from sorteos.sources import parse_row


@dataclass(frozen=True)
class GraphSource:
    graph: Graph
    media_id: str

    def _comments(self, path, parent_id=None):
        params = {"limit": 50}
        seen = set()
        while True:
            payload = self.graph.read(path, "id,text,timestamp,username,from", **params)
            rows = payload.get("data")
            if not isinstance(rows, list):
                raise GraphError("Página de comentarios inválida.")
            for index, row in enumerate(rows, 1):
                if (
                    not isinstance(row, dict)
                    or not isinstance(row.get("id"), str)
                    or not re.fullmatch("[0-9]+", row["id"])
                ):
                    raise GraphError("Comentario sin ID válido.")
                author = row.get("from") or {}
                if not isinstance(author, dict):
                    raise GraphError("Autor inválido.")
                yield parse_row(
                    dict(
                        id=row["id"],
                        media_id=self.media_id,
                        parent_id=parent_id,
                        text=row.get("text"),
                        created_at=row.get("timestamp"),
                        author_id=author.get("id"),
                        username=row.get("username") or author.get("username"),
                    ),
                    index,
                    csv_input=False,
                )
            paging = payload.get("paging", {})
            if not isinstance(paging, dict):
                raise GraphError("Paginación inválida.")
            if not paging.get("next"):
                return
            cursors = paging.get("cursors")
            after = cursors.get("after") if isinstance(cursors, dict) else None
            if not isinstance(after, str) or not after or after in seen:
                raise GraphError("Cursor de continuación ausente o repetido.")
            seen.add(after)
            params["after"] = after

    def __iter__(self):
        if not re.fullmatch("[0-9]+", self.media_id):
            raise GraphError("La publicación requiere un ID numérico.")
        for root in self._comments(f"{self.media_id}/comments"):
            yield root
            yield from self._comments(f"{root.id}/replies", root.id)
