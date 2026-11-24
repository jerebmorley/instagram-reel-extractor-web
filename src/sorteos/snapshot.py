"""Snapshot JSONL canónico del conjunto de comentarios de una campaña."""

import hashlib
import json
import os
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from sorteos.models import Comment


def write_snapshot(comments: Iterable[Comment], directory: Path) -> tuple[Path, int]:
    unique = {}
    for comment in comments:
        key = (comment.media_id, comment.id)
        if unique.setdefault(key, comment) != comment:
            raise ValueError("Hay versiones contradictorias del mismo comentario.")

    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    digest = hashlib.sha256()
    with NamedTemporaryFile(dir=directory, delete=False) as stream:
        temporary = Path(stream.name)
    try:
        with temporary.open("wb") as stream:
            for key in sorted(unique):
                comment = unique[key]
                row = asdict(comment)
                row["created_at"] = comment.created_at.isoformat(
                    timespec="microseconds"
                )
                line = json.dumps(row, sort_keys=True, separators=(",", ":"))
                data = (line + "\n").encode("utf-8")
                digest.update(data)
                stream.write(data)
        target = directory / f"{digest.hexdigest()}.jsonl"
        try:
            os.link(temporary, target)
        except FileExistsError:
            if hashlib.sha256(target.read_bytes()).digest() != digest.digest():
                raise ValueError(
                    "El snapshot existente no coincide con su hash."
                ) from None
        return target, len(unique)
    finally:
        temporary.unlink(missing_ok=True)
