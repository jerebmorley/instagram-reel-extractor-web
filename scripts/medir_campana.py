"""Ejecutar con uv run --locked python scripts/medir_campana.py."""

from time import perf_counter

from sorteos.fixtures import fixture_rules, synthetic_comments
from sorteos.participants import consolidate


def main():
    rules = fixture_rules()
    rows = synthetic_comments(10_000, seed=16)
    start = perf_counter()
    first = consolidate(rows, rules)
    elapsed = perf_counter() - start
    other = synthetic_comments(10_000, seed=16)
    if rows != other or first != consolidate(reversed(other), rules):
        raise RuntimeError(
            "La campaña o sus decisiones cambiaron al repetir la prueba."
        )
    print(
        f"{len(first)} decisiones, {sum(d.grants_entry for d in first)} entradas, "
        f"{elapsed:.3f} segundos en la primera evaluación. Repetición idéntica."
    )


if __name__ == "__main__":
    main()
