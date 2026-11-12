import pytest

from jurisradar.models import ProcessRecord


@pytest.fixture
def number():
    return "00000000000000000000"  # Número fictício para testes, nunca consultar na rede.


@pytest.fixture
def hit(number):
    return {
        "_id": "fake-es-id",
        "_source": {
            "id": "TJPE_111_G1_222_" + number,
            "numeroProcesso": number,
            "tribunal": "TJPE",
            "grau": "G1",
            "classe": {"codigo": 111, "nome": "Classe fictícia"},
            "orgaoJulgador": {"codigo": 222, "nome": "Vara fictícia"},
            "assuntos": [{"codigo": 123, "nome": "Assunto de teste"}],
            "movimentos": [{"codigo": 26, "nome": "Movimento de teste", "dataHora": "2026-01-02T00:00:00Z"}],
            "dataAjuizamento": "2025-01-01T00:00:00Z",
            "dataHoraUltimaAtualizacao": "2026-01-03T00:00:00Z",
        },
    }


@pytest.fixture
def record(number, hit):
    src = hit["_source"]
    return ProcessRecord(
        source_key="TJPE:" + src["id"], number=number, court="TJPE", degree="G1",
        class_code=111, class_name="Classe fictícia", body_code=222,
        body_name="Vara fictícia", filing_date=src["dataAjuizamento"],
        updated_at=src["dataHoraUltimaAtualizacao"],
        subjects=src["assuntos"], movements=src["movimentos"],
    )
