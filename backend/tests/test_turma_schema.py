from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.turma_schema import AvaliacaoResponseSchema, TurmaCreateSchema, TurmaResponseSchema


def payload(**overrides):
    data = {
        "idCurso": 1,
        "idProfessor": 2,
        "capacidade": 20,
        "dataInicio": date(2026, 3, 1),
        "dataFim": date(2026, 6, 30),
        "diasAula": "1,3,5",
    }
    data.update(overrides)
    return data


def test_accepts_complete_payload():
    schema = TurmaCreateSchema(**payload())

    assert schema.capacidade == 20
    assert schema.diasAula == "1,3,5"
    assert schema.avaliacoes is None


def test_accepts_valid_avaliacoes():
    schema = TurmaCreateSchema(
        **payload(
            avaliacoes=[
                {"nome": "Prova 1", "tipo": "prova", "peso": 4},
                {"nome": "Trabalho final", "tipo": "trabalho", "peso": 2.5},
            ]
        )
    )

    assert schema.avaliacoes is not None
    assert schema.avaliacoes[0].nome == "Prova 1"
    assert schema.avaliacoes[1].peso == 2.5


@pytest.mark.parametrize("capacidade", [0, -1])
def test_rejects_non_positive_capacidade(capacidade):
    with pytest.raises(ValidationError):
        TurmaCreateSchema(**payload(capacidade=capacidade))


@pytest.mark.parametrize(
    "diasAula",
    ["", "7", "Seg", "1,", ",1", "1,,2", "1, 2", "1,1"],
)
def test_rejects_invalid_dias_aula(diasAula):
    with pytest.raises(ValidationError):
        TurmaCreateSchema(**payload(diasAula=diasAula))


@pytest.mark.parametrize("diasAula", ["0", "0,6", "1,3,5"])
def test_accepts_valid_dias_aula(diasAula):
    schema = TurmaCreateSchema(**payload(diasAula=diasAula))

    assert schema.diasAula == diasAula


@pytest.mark.parametrize(
    "avaliacao",
    [
        {"nome": "", "tipo": "prova", "peso": 10},
        {"nome": "   ", "tipo": "prova", "peso": 10},
        {"nome": "Prova 1", "tipo": "seminario", "peso": 10},
        {"nome": "Prova 1", "tipo": "prova", "peso": 0},
        {"nome": "Prova 1", "tipo": "prova", "peso": -1},
    ],
)
def test_rejects_invalid_avaliacao(avaliacao):
    with pytest.raises(ValidationError):
        TurmaCreateSchema(**payload(avaliacoes=[avaliacao]))


@pytest.mark.parametrize(
    "missing_field",
    ["idCurso", "idProfessor", "capacidade", "dataInicio", "dataFim", "diasAula"],
)
def test_rejects_missing_required_field(missing_field):
    data = payload()
    data.pop(missing_field)

    with pytest.raises(ValidationError):
        TurmaCreateSchema(**data)


def test_response_accepts_legacy_null_fields():
    schema = TurmaResponseSchema.model_validate(
        {
            "idTurma": 1,
            "idCurso": 1,
            "capacidade": None,
            "dataInicio": None,
            "dataFim": None,
            "idProfessor": None,
            "diasAula": None,
            "avaliacoes": None,
        }
    )

    assert schema.capacidade is None
    assert schema.avaliacoes is None


def test_response_aceita_avaliacoes_legadas():
    schema = TurmaResponseSchema.model_validate(
        {
            "idTurma": 1,
            "idCurso": 1,
            "avaliacoes": [
                {"nome": "Legada", "tipo": "seminario", "peso": 10, "observacao": "antiga"}
            ],
        }
    )

    assert schema.avaliacoes[0].tipo == "seminario"
    assert schema.avaliacoes[0].model_dump()["observacao"] == "antiga"


@pytest.mark.parametrize(
    ("raw", "normalized"),
    [
        ("Prova", "prova"),
        ("prova", "prova"),
        ("TRABALHO", "trabalho"),
        ("trabalho", "trabalho"),
    ],
)
def test_response_avaliacao_normaliza_tipo_conhecido(raw, normalized):
    schema = AvaliacaoResponseSchema.model_validate({"tipo": raw})

    assert schema.tipo == normalized


def test_response_avaliacao_preserva_tipo_desconhecido():
    schema = AvaliacaoResponseSchema.model_validate(
        {"nome": "Legada", "tipo": "seminario", "peso": 10}
    )

    assert schema.tipo == "seminario"


def test_response_avaliacao_aceita_campos_ausentes():
    schema = AvaliacaoResponseSchema.model_validate({})

    assert schema.nome is None
    assert schema.tipo is None
    assert schema.peso is None


def test_response_avaliacao_preserva_chave_extra():
    schema = AvaliacaoResponseSchema.model_validate(
        {"nome": "Legada", "tipo": "seminario", "peso": 10, "observacao": "antiga"}
    )

    assert schema.model_dump()["observacao"] == "antiga"
