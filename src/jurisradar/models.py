"""Modelos internos desacoplados da resposta JSON do DataJud."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


class InvalidProcessNumber(ValueError):
    """Número CNJ não possui 20 dígitos."""


class InvalidDataJudResponse(ValueError):
    """Formato inesperado dos metadados recebidos do DataJud."""


def normalize_number(value: str) -> str:
    """Aceita número CNJ formatado ou apenas dígitos; não verifica dígitos de controle."""
    if not re.fullmatch(r"[\d.\-\s]+", value, flags=re.ASCII):
        raise InvalidProcessNumber("O número deve conter apenas dígitos, pontos, traços e espaços.")
    digits = re.sub(r"[^0-9]", "", value)
    if len(digits) != 20:
        raise InvalidProcessNumber("Informe um número CNJ com exatamente 20 dígitos.")
    return digits


def _obj(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _array(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


@dataclass(frozen=True)
class ProcessRecord:
    source_key: str
    number: str
    court: str
    degree: str | None
    class_code: int | None
    class_name: str | None
    body_code: int | None
    body_name: str | None
    filing_date: str | None
    updated_at: str | None
    subjects: list[dict[str, Any]]
    movements: list[dict[str, Any]]


def parse_hit(hit: Any, *, expected_number: str, court: str = "TJPE") -> ProcessRecord | None:
    """Descarta matches inexatos; rejeita entradas estruturalmente inválidas."""
    if not isinstance(hit, dict) or not isinstance(hit.get("_source"), dict):
        raise InvalidDataJudResponse("Um resultado veio sem o objeto _source.")
    source = hit["_source"]
    number = source.get("numeroProcesso")
    if not isinstance(number, str):
        raise InvalidDataJudResponse("Resultado sem numeroProcesso válido.")
    if number != expected_number:
        return None
    tribunal = source.get("tribunal")
    if tribunal != court:
        raise InvalidDataJudResponse("O tribunal retornado difere do endpoint solicitado.")

    degree = source.get("grau")
    classification = _obj(source.get("classe"))
    body = _obj(source.get("orgaoJulgador"))
    # O ID de origem documentado pelo CNJ identifica o registro melhor que apenas
    # o número, que pode possuir mais de uma ocorrência em graus diferentes.
    origin_id = source.get("id") or hit.get("_id")
    if not isinstance(origin_id, str) or not origin_id.strip():
        raise InvalidDataJudResponse("Registro sem identificador de origem (id/_id).")
    return ProcessRecord(
        source_key=f"{court}:{origin_id}",
        number=number,
        court=tribunal,
        degree=str(degree) if degree is not None else None,
        class_code=classification.get("codigo"),
        class_name=classification.get("nome"),
        body_code=body.get("codigo"),
        body_name=body.get("nome"),
        filing_date=source.get("dataAjuizamento"),
        updated_at=source.get("dataHoraUltimaAtualizacao"),
        subjects=_array(source.get("assuntos")),
        movements=_array(source.get("movimentos")),
    )
