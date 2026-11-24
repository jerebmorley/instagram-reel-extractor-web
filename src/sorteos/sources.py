"""Fuentes locales iterables de Comment."""

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sorteos.fixtures import synthetic_comments
from sorteos.models import Comment

REQUIRED = {"id", "media_id", "text", "created_at"}
OPTIONAL = {"author_id", "username", "parent_id"}


def check_fields(keys):
    if not REQUIRED <= set(keys) <= REQUIRED | OPTIONAL:
        raise ValueError(
            "Se requieren id, media_id, text y created_at; revisá los campos adicionales."
        )


def parse_row(row, index, *, csv_input):
    try:
        if not isinstance(row, dict):
            raise ValueError("Se esperaba un objeto.")
        check_fields(row)
        if csv_input and None in row.values():
            raise ValueError("Faltan columnas en el registro.")
        values = dict(row)
        stamp = values["created_at"]
        if not isinstance(stamp, str):
            raise ValueError("created_at debe ser una fecha ISO con zona.")
        try:
            values["created_at"] = datetime.fromisoformat(
                stamp.removesuffix("Z") + ("+00:00" if stamp.endswith("Z") else "")
            )
        except ValueError:
            raise ValueError("created_at debe ser una fecha ISO con zona.") from None
        if csv_input:
            for key in OPTIONAL:
                if values.get(key) == "":
                    values[key] = None
        return Comment(**values)
    except ValueError as exc:
        raise ValueError(f"Registro {index}: {exc}") from None


@dataclass(frozen=True)
class FileSource:
    path: Path

    def __iter__(self):
        suffix = self.path.suffix.lower()
        with self.path.open(encoding="utf-8-sig", newline="") as stream:
            if suffix == ".json":
                rows = json.load(stream)
                if not isinstance(rows, list):
                    raise ValueError("El JSON debe contener una lista de comentarios.")
            elif suffix == ".csv":
                rows = csv.DictReader(stream, strict=True)
                keys = rows.fieldnames or []
                check_fields(keys)
                if len(set(keys)) != len(keys):
                    raise ValueError("Hay columnas repetidas en el CSV.")
            else:
                raise ValueError("Elegí un archivo .json o .csv.")
            for index, row in enumerate(rows, 1):
                yield parse_row(row, index, csv_input=suffix == ".csv")


@dataclass(frozen=True)
class FixtureSource:
    count: int
    seed: int = 16

    def __iter__(self):
        return iter(synthetic_comments(self.count, self.seed))
