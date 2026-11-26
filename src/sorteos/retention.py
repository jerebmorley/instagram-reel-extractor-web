"""Limpieza local de campañas de la interfaz por fecha de cierre."""

import fcntl
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sorteos.campaign import utc_date
from sorteos.extraction import workspace


def cleanup(days, campaign=None):
    root = Path("exports/interfaz")
    if days < 1:
        raise ValueError("Indicá un plazo positivo en días.")
    if campaign is not None and not re.fullmatch("[0-9a-f]{64}", campaign):
        raise ValueError("Indicá el identificador completo de la vista previa.")
    if root.is_symlink() or root.parent.is_symlink():
        raise ValueError("El directorio de campañas debe ser local.")
    if campaign is None and not root.exists():
        return []
    paths = [root / campaign] if campaign else sorted(root.iterdir())
    now = datetime.now(timezone.utc)
    results = []
    for path in paths:
        if not campaign and re.fullmatch(r"\.purga-[0-9a-f]{64}", path.name):
            results.append(
                {"campana": path.name[7:], "estado": "eliminación pendiente"}
            )
            continue
        if not re.fullmatch("[0-9a-f]{64}", path.name):
            continue
        pending = root / (".purga-" + path.name)
        if campaign and pending.exists():
            # El traslado solo ocurre después de validar plazo, origen y bloqueo.
            shutil.rmtree(pending)
            return [{"campana": campaign, "estado": "eliminación completada"}]
        config = path / "config.json"
        row = {"campana": path.name}
        results.append(row)
        if path.is_symlink() or config.is_symlink() or not config.is_file():
            row["estado"] = "sin configuración verificable"
        else:
            try:
                draft = json.loads(config.read_bytes())
                if workspace(draft, root) != path:
                    raise ValueError("Configuración modificada")
                expiry = utc_date(draft["reglas"]["ends_at"]) + timedelta(days=days)
            except (AttributeError, KeyError, TypeError, ValueError, OverflowError):
                if campaign:
                    raise ValueError("Configuración sin cierre verificable.") from None
                row["estado"] = "sin configuración verificable"
                continue
            row.update(vence=expiry.isoformat(), estado="vigente")
            if expiry <= now:
                row["estado"] = "vencida"
        if campaign:
            if row["estado"] != "vencida":
                raise ValueError(
                    "Solo se pueden eliminar campañas vencidas verificadas."
                )
            lock = path / "worker.lock"
            if lock.is_symlink() or not lock.is_file():
                raise ValueError("Falta el bloqueo local de la extracción.")
            with lock.open("rb") as handle:
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    raise ValueError("Hay una extracción en curso.") from None
                path.rename(pending)
                shutil.rmtree(pending)
            row["estado"] = "eliminada"
    return results
