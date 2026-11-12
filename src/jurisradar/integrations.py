"""Acesso HTTP somente leitura à API Pública do DataJud (TJPE)."""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import InvalidDataJudResponse, ProcessRecord, parse_hit

DATAJUD_TJPE_URL = "https://api-publica.datajud.cnj.jus.br/api_publica_tjpe/_search"
SOURCE_FIELDS = [
    "id", "numeroProcesso", "tribunal", "grau", "classe", "assuntos",
    "orgaoJulgador", "dataAjuizamento", "dataHoraUltimaAtualizacao", "movimentos",
]
MAX_RESULTS = 20


class DataJudError(RuntimeError):
    """Falha de conectividade, autenticação ou contrato da API."""


class DataJudClient:
    def __init__(self, api_key: str, *, session: requests.Session | None = None, timeout: int = 30):
        key = api_key.strip()
        if key.lower().startswith("apikey "):
            key = key.split(None, 1)[1].strip()
        if not key:
            raise DataJudError("Configure DATAJUD_API_KEY com a chave pública vigente do CNJ.")
        self.api_key = key
        self.timeout = timeout
        self.session = session or requests.Session()
        if session is None:
            # Retry apenas de consultas POST idempotentes, com backoff e Retry-After.
            retry = Retry(
                total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=frozenset(["POST"]), respect_retry_after_header=True,
            )
            self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def search(self, number: str) -> list[ProcessRecord]:
        payload = {
            "size": MAX_RESULTS,
            "track_total_hits": True,
            "query": {"match": {"numeroProcesso": number}},
            "_source": SOURCE_FIELDS,
        }
        try:
            response = self.session.post(
                DATAJUD_TJPE_URL,
                json=payload,
                headers={
                    "Authorization": f"APIKey {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except requests.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else "desconhecido"
            if code in (401, 403):
                raise DataJudError(f"Autenticação recusada (HTTP {code}); confira a chave na Wiki do CNJ.") from exc
            raise DataJudError(f"Erro HTTP {code} na consulta ao DataJud.") from exc
        except requests.RequestException as exc:
            raise DataJudError("Falha de rede ou tempo limite ao consultar o DataJud.") from exc
        except ValueError as exc:
            raise DataJudError("O DataJud respondeu com JSON inválido.") from exc

        try:
            hits_root = data["hits"]
            hits = hits_root["hits"]
            if not isinstance(hits, list):
                raise TypeError("hits não é uma lista")
            total = hits_root.get("total", {})
            if isinstance(total, dict) and total.get("value", 0) > MAX_RESULTS:
                raise InvalidDataJudResponse("Consulta excedeu o limite do MVP; resultado incompleto.")
            parsed = [parse_hit(hit, expected_number=number) for hit in hits]
            # Resposta do Elasticsearch pode conter matches aproximados.
            return [p for p in parsed if p is not None]
        except (KeyError, TypeError, InvalidDataJudResponse) as exc:
            raise DataJudError(f"Formato inesperado da resposta do DataJud: {exc}") from exc
