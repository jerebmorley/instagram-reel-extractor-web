"""Lecturas de diagnóstico para Instagram Login."""

import json
import re
import time
from http.client import HTTPException, HTTPSConnection
from urllib.parse import urlencode


class GraphError(Exception):
    """Error que puede mostrarse al operador."""


class TransientError(GraphError):
    """Una lectura GET puede volver a intentarse."""


class Graph:
    def __init__(self, version, token, *, request_budget=500):
        if type(request_budget) is not int or request_budget < 1:
            raise GraphError("El presupuesto de peticiones debe ser positivo.")
        self.remaining = request_budget
        if not re.fullmatch(r"v[0-9]+\.[0-9]+", version):
            raise GraphError("Usá la versión del panel con formato vN.N.")
        if not re.fullmatch(r"[!-~]+", token):
            raise GraphError("Configurá INSTAGRAM_ACCESS_TOKEN en el entorno local.")
        self.version = version
        self._token = token

    def read(self, path, fields, **params):
        for attempt in range(3):
            if self.remaining == 0:
                raise GraphError("Presupuesto local de peticiones agotado.")
            self.remaining -= 1
            try:
                return self._read_once(path, fields, **params)
            except TransientError:
                if attempt == 2 or self.remaining == 0:
                    raise
                time.sleep(2**attempt)

    def _read_once(self, path, fields, **params):
        connection = HTTPSConnection("graph.instagram.com", timeout=15)
        query = urlencode({"fields": fields, **params})
        try:
            connection.request(
                "GET",
                f"/{self.version}/{path}?{query}",
                headers={"Authorization": f"Bearer {self._token}"},
            )
            response = connection.getresponse()
            if response.status == 429:
                raise GraphError("HTTP 429: Meta limitó el uso. Reintentá más tarde.")
            if response.status in (500, 502, 503, 504) and not response.getheader(
                "Retry-After"
            ):
                raise TransientError(f"Fallo transitorio HTTP {response.status}.")
            if response.status != 200:
                raise GraphError(
                    f"Meta devolvió HTTP {response.status}. Revisá el token, "
                    "los permisos, la versión y los límites de uso."
                )
            payload = json.load(response)
            if not isinstance(payload, dict) or "error" in payload:
                raise GraphError("La API devolvió una respuesta inesperada.")
            return payload
        except (HTTPException, OSError):
            raise TransientError("Falló la conexión con Meta.") from None
        except ValueError:
            raise GraphError(
                "Falló la conexión o la lectura de la respuesta."
            ) from None
        finally:
            connection.close()

    def profile(self):
        result = self.read("me", "id,username")
        if not result.get("id") or not result.get("username"):
            raise GraphError("El perfil recibido carece de id o username.")
        return {key: result[key] for key in ("id", "username")}

    def page(self, path, fields):
        payload = self.read(path, fields, limit=10)
        rows = payload.get("data")
        if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
            raise GraphError("Se esperaba una página de resultados.")
        paging = payload.get("paging") or {}
        if not isinstance(paging, dict):
            raise GraphError("Paginación inesperada.")
        return rows, bool(paging.get("next"))

    def media(self):
        rows, more = self.page("me/media", "id,media_type,media_product_type")
        keys = ("id", "media_type", "media_product_type")
        return {
            "publicaciones": [{k: row.get(k) for k in keys} for row in rows],
            "hay_mas": more,
        }

    def comments(self, media_id):
        if not re.fullmatch(r"[0-9]+", media_id):
            raise GraphError("El ID de publicación debe ser numérico.")
        fields = "id,text,timestamp,username"
        rows, more = self.page(f"{media_id}/comments", fields)
        comments = []
        for row in rows:
            comment_id = row.get("id")
            if not isinstance(comment_id, str) or not re.fullmatch(
                r"[0-9]+", comment_id
            ):
                raise GraphError(
                    "Comentario sin identificador válido para leer respuestas."
                )
            replies, more_replies = self.page(f"{comment_id}/replies", fields)
            comments.append(
                {
                    "campos_presentes": [
                        k for k in fields.split(",") if row.get(k) is not None
                    ],
                    "respuestas": [
                        [k for k in fields.split(",") if reply.get(k) is not None]
                        for reply in replies
                    ],
                    "hay_mas_respuestas": more_replies,
                }
            )
        return {"limite_por_pagina": 10, "comentarios": comments, "hay_mas": more}
