import json

import pytest

from sorteos.sources import FileSource, FixtureSource


def test_equivalent_inputs(tmp_path):
    row = {
        "id": "01",
        "media_id": "m",
        "text": "hola,\n🎉",
        "created_at": "2026-01-01T00:00:00Z",
    }
    path = tmp_path / "demo.json"
    path.write_text(json.dumps([row]))
    csv = tmp_path / "demo.csv"
    csv.write_text(
        'id,media_id,text,created_at,username\n01,m,"hola,\n🎉",2025-12-31T21:00:00-03:00,\n',
        encoding="utf-8",
    )
    assert list(FileSource(csv)) == list(FileSource(path))
    assert list(FileSource(csv))[0].id == "01"
    assert list(FixtureSource(3)) == list(FixtureSource(3))


@pytest.mark.parametrize(
    "name,content,message",
    [
        ("a.json", "{}", "lista"),
        ("a.json", "[{}]", "Registro 1"),
        ("a.csv", "id,media_id,text,created_at\n1,2,solo\n", "Registro 1"),
        ("a.csv", "id,media_id,text,created_at,id\n", "repetidas"),
    ],
)
def test_invalid_input(tmp_path, name, content, message):
    path = tmp_path / name
    path.write_text(content)
    with pytest.raises(ValueError, match=message):
        list(FileSource(path))
