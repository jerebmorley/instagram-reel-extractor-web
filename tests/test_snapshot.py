import hashlib
import json
from dataclasses import replace

import pytest

from sorteos.fixtures import synthetic_comments
from sorteos.snapshot import write_snapshot


def test_order_duplicates_and_integrity(tmp_path):
    rows = synthetic_comments(12, 16)
    path, count = write_snapshot([*rows, rows[0]], tmp_path)
    data = path.read_bytes()
    assert count == 12
    assert path.stem == hashlib.sha256(data).hexdigest()
    assert len([json.loads(line) for line in data.splitlines()]) == count
    assert write_snapshot(reversed(rows), tmp_path / "other")[0].read_bytes() == data
    assert write_snapshot(rows, tmp_path) == (path, count)
    path.write_bytes(b"alterado")
    with pytest.raises(ValueError, match="hash"):
        write_snapshot(rows, tmp_path)
    assert path.read_bytes() == b"alterado"


def test_conflict_aborts(tmp_path):
    (row,) = synthetic_comments(1, 0)
    with pytest.raises(ValueError, match="contradictorias"):
        write_snapshot([row, replace(row, text="cambio")], tmp_path)
    assert not list(tmp_path.iterdir())
