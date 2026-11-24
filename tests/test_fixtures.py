from sorteos.fixtures import fixture_rules, synthetic_comments
from sorteos.participants import consolidate


def test_seeded_campaign_exercises_eligibility_rules():
    rows = synthetic_comments(100, 16)
    assert rows == synthetic_comments(100, 16)
    assert rows != synthetic_comments(100, 17)
    decisions = consolidate(rows, fixture_rules())
    assert decisions == consolidate(reversed(rows), fixture_rules())
    assert {reason for d in decisions for reason in d.reasons} == {
        "identidad_no_disponible",
        "autor_excluido",
        "fuera_de_fecha",
        "respuesta_no_admitida",
        "menciones_insuficientes",
        "participante_ya_habilitado",
    }
    entries = [d.participant for d in decisions if d.grants_entry]
    assert len(entries) == len(set(entries)) > 0
