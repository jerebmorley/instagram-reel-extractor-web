"""Reporte agregado del padrón y su snapshot."""

import csv
import io
from collections import Counter

from sorteos.mentions import mentions


def summary(roster, comments, publications, references):
    decisions = roster["decisions"]
    reasons = Counter(reason for d in decisions for reason in d["reasons"])
    valid = sum(not d["reasons"] for d in decisions)
    metrics = {
        "comentarios": len(comments),
        "participantes_identificados": len(
            {d["participant"] for d in decisions if d["participant"] is not None}
        ),
        "entradas_automaticas": valid,
        "comentarios_descartados": len(decisions) - valid,
        "entradas_tras_revision": len(roster["participants"]),
    }
    tags = Counter(tag for c in comments for tag in mentions(c.text))
    daily = Counter(c.created_at.date().isoformat() for c in comments)
    totals = Counter(c.media_id for c in comments)
    coverage = []
    for media in publications:
        observed = references.get(media, {})
        expected = observed.get("cantidad")
        actual = totals[media]
        delta = actual - expected if type(expected) is int and expected >= 0 else None
        coverage.append(
            dict(
                publicacion=media,
                extraidos=actual,
                referencia=expected,
                diferencia=delta,
                estado="desconocida"
                if delta is None
                else "coinciden"
                if delta == 0
                else "faltante"
                if delta < 0
                else "excedente",
                observado=observed.get("fecha", ""),
            )
        )
    return dict(
        resumen=metrics,
        descartes=dict(sorted(reasons.items())),
        menciones=dict(sorted(tags.items(), key=lambda item: (-item[1], item[0]))),
        por_dia=dict(sorted(daily.items())),
        cobertura=coverage,
    )


def csv_report(report):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(
        [
            "seccion",
            "concepto",
            "cantidad",
            "referencia",
            "diferencia",
            "estado",
            "observado",
        ]
    )
    for section in ("resumen", "descartes", "menciones", "por_dia"):
        for key, value in report[section].items():
            writer.writerow([section, key, value, "", "", "", ""])
    for row in report["cobertura"]:
        writer.writerow(
            [
                "cobertura",
                row["publicacion"],
                row["extraidos"],
                row["referencia"],
                row["diferencia"],
                row["estado"],
                row["observado"],
            ]
        )
    return output.getvalue()
