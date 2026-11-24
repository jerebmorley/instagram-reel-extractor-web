"""Lecturas de diagnóstico para Instagram Login."""

import json
import re
from http.client import HTTPException, HTTPSConnection
from urllib.parse import urlencode


class GraphError(Exception):
    """Error que puede mostrarse al operador."""


class Graph:
    def __init__(self, version, token):
        if not re.fullmatch(r"v[0-9]+\.[0-9]+", version):
            raise GraphError("Usá la versión del panel con formato vN.N.")
        if not re.fullmatch(r"[!-~]+", token):
            raise GraphError("Configurá INSTAGRAM_ACCESS_TOKEN en el entorno local.")
        self.version = version
        self._token = token

    def read(self, path, fields, **params):
        connection = HTTPSConnection("graph.instagram.com", timeout=15)
        query = urlencode({"fields": fields, **params})
        try:
            connection.request(
                "GET",
                f"/{self.version}/{path}?{query}",
                headers={"Authorization": f"Bearer {self._token}"},
            )
            response = connection.getresponse()
            if response.status != 200:
                raise GraphError(
                    f"Meta devolvió HTTP {response.status}. Revisá el token, "
                    "los permisos, la versión y los límites de uso."
                )
            payload = json.load(response)
            if not isinstance(payload, dict) or "error" in payload:
                raise GraphError("La API devolvió una respuesta inesperada.")
            return payload
        except (ValueError, HTTPException, OSError):
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
