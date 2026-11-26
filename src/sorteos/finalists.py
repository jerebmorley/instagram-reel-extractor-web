"""Verificación posterior al sorteo, con las bases declaradas por el operador."""

from datetime import datetime, timezone

from sorteos.campaign import read_record, record, utc_date


def confirm_finalists(database, cutoff, checks):
    data = read_record(database, "sorteo")
    if not data.get("requiere_seguimiento"):
        raise ValueError("La campaña no requiere verificar seguimiento.")
    stamp = utc_date(cutoff)
    if stamp > datetime.now(timezone.utc):
        raise ValueError("La fecha de corte no puede estar en el futuro.")
    ranking = data["resultado"]["ganadores"] + data["resultado"]["suplentes"]
    if set(checks) != set(ranking):
        raise ValueError("Completá únicamente los finalistas sorteados.")
    for status, reason in checks.values():
        if status not in ("sigue", "no sigue") or not reason.strip():
            raise ValueError("Cada finalista requiere estado y motivo.")
    selected = [p for p in ranking if checks[p][0] == "sigue"][
        : data["cupos_ganadores"]
    ]
    result = dict(
        corte=stamp.isoformat(),
        registrado=datetime.now(timezone.utc).isoformat(),
        controles=checks,
        ganadores_confirmados=selected,
        vacantes=data["cupos_ganadores"] - len(selected),
        padron_sha256=data["padron_sha256"],
    )
    record(database, "finalistas", result)
    return result
