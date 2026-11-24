"""Lectura paginada de una publicación autorizada."""

import re
from dataclasses import dataclass

from sorteos.graph import Graph, GraphError
from sorteos.sources import parse_row


@dataclass(frozen=True)
class GraphSource:
    graph: Graph
    media_id: str

    def _page(self, path, after, parent_id):
        params = {"limit": 50}
        if after:
            params["after"] = after
        payload = self.graph.read(path, "id,text,timestamp,username,from", **params)
        rows = payload.get("data")
        if not isinstance(rows, list):
            raise GraphError("Página de comentarios inválida.")
        result = []
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
            result.append(
                parse_row(
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
            )
        paging = payload.get("paging", {})
        if not isinstance(paging, dict):
            raise GraphError("Paginación inválida.")
        if not paging.get("next"):
            return result, None
        cursors = paging.get("cursors")
        after = cursors.get("after") if isinstance(cursors, dict) else None
        if not isinstance(after, str) or not after:
            raise GraphError("Cursor de continuación ausente o repetido.")
        return result, after

    def batches(self, cursor):
        if not re.fullmatch("[0-9]+", self.media_id):
            raise GraphError("La publicación requiere un ID numérico.")
        state = cursor or dict(
            root=None,
            roots_done=False,
            parents=[],
            reply=None,
            root_seen=[],
            reply_seen=[],
        )
        while state["parents"] or not state["roots_done"]:
            parents = list(state["parents"])
            parent = parents[0] if parents else None
            edge = "reply" if parent else "root"
            path = f"{parent}/replies" if parent else f"{self.media_id}/comments"
            rows, after = self._page(path, state[edge], parent)
            seen = state[edge + "_seen"]
            if after and after in seen:
                raise GraphError("Cursor de continuación repetido.")
            state = dict(state, parents=parents)
            state[edge] = after
            state[edge + "_seen"] = [*seen, after] if after else []
            if parent:
                if not after:
                    parents.pop(0)
            else:
                parents.extend(row.id for row in rows)
                state["roots_done"] = after is None
            yield rows, state

    def __iter__(self):
        for rows, _ in self.batches(None):
            yield from rows
