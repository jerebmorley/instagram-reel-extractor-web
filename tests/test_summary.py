import csv
import io

from sorteos.fixtures import synthetic_comments
from sorteos.summary import csv_report, summary


def test_report_distinguishes_missing_reference_from_zero():
    comment = next(iter(synthetic_comments(100, 16)))
    roster = {"decisions": [{"participant": "a", "reasons": []}], "participants": ["a"]}
    pubs = [comment.media_id, "empty", "missing", "legacy"]
    refs = {pub: {"cantidad": n} for pub, n in zip(pubs, (0, 0, 3))}
    report = summary(roster, [comment], pubs, refs)
    assert report["resumen"] == dict(
        comentarios=1,
        participantes_identificados=1,
        entradas_automaticas=1,
        comentarios_descartados=0,
        entradas_tras_revision=1,
    )
    assert report["por_dia"] == {comment.created_at.date().isoformat(): 1}
    rows = [
        r
        for r in csv.DictReader(io.StringIO(csv_report(report)))
        if r["seccion"] == "cobertura"
    ]
    assert [(r["estado"], r["diferencia"]) for r in rows] == [
        ("excedente", "1"),
        ("coinciden", "0"),
        ("faltante", "-3"),
        ("desconocida", ""),
    ]


def test_report_counts_each_reason_and_each_mention_once_per_comment():
    from dataclasses import replace

    base = next(iter(synthetic_comments(100, 16)))
    comments = [
        replace(base, id=str(i), text=text)
        for i, text in enumerate(["@demo @demo", "@demo @otra"])
    ]
    roster = {
        "decisions": [
            {"participant": "a", "reasons": []},
            {"participant": "a", "reasons": ["motivo_a", "motivo_b"]},
        ],
        "participants": [],
    }
    report = summary(roster, comments, [base.media_id], {})
    assert report["resumen"]["comentarios_descartados"] == 1
    assert report["resumen"]["participantes_identificados"] == 1
    assert report["resumen"]["entradas_tras_revision"] == 0
    assert report["descartes"] == {"motivo_a": 1, "motivo_b": 1}
    assert report["menciones"] == {"demo": 2, "otra": 1}
