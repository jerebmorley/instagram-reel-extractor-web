"""Credencial de la cuenta activa, cifrada en el equipo del operador."""

import json
import os
from datetime import date
from pathlib import Path
from tempfile import NamedTemporaryFile

from cryptography.fernet import Fernet, InvalidToken


class CredentialError(Exception):
    """Mensaje de diagnóstico sin material secreto."""


def credential_path():
    return Path.home() / ".local" / "share" / "sorteos-ig" / "cuenta.fernet"


def cipher():
    try:
        return Fernet(os.environ["SORTEOS_FERNET_KEY"].encode("ascii"))
    except (KeyError, ValueError):
        raise CredentialError(
            "Configurá una clave Fernet válida en SORTEOS_FERNET_KEY."
        ) from None


def check_expiry(expires):
    if expires is not None and date.fromisoformat(expires) <= date.today():
        raise CredentialError("El vencimiento indicado ya se alcanzó. Renová el token.")


def save_token(path, token, expires=None):
    check_expiry(expires)
    data = json.dumps({"token": token, "expires": expires}).encode()
    encrypted = cipher().encrypt(data)
    temp = None
    try:
        path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temp = Path(stream.name)
            stream.write(encrypted)
        temp.replace(path)
    except OSError:
        raise CredentialError("Falló la escritura de la credencial local.") from None
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def load_token(path):
    try:
        encrypted = path.read_bytes()
        record = json.loads(cipher().decrypt(encrypted))
        check_expiry(record["expires"])
        token = record["token"]
        if not isinstance(token, str) or not token:
            raise ValueError
        return token
    except FileNotFoundError:
        raise CredentialError(
            "Configurá INSTAGRAM_ACCESS_TOKEN o usá guardar-token."
        ) from None
    except (InvalidToken, KeyError, ValueError, TypeError, OSError):
        raise CredentialError(
            "No se pudo leer la credencial. Revisá el archivo y la clave."
        ) from None
