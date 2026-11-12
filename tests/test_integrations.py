import pytest
import requests

from jurisradar.integrations import DATAJUD_TJPE_URL, DataJudClient, DataJudError


class FakeResponse:
    def __init__(self, payload=None, status=200):
        self.payload = payload
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError("fake error")
            error.response = self
            raise error

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.calls = response, error, []

    def post(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self.error:
            raise self.error
        return self.response


def test_query_uses_official_endpoint_and_auth(number, hit):
    session = FakeSession(FakeResponse({"hits": {"total": {"value": 1}, "hits": [hit]}}))
    records = DataJudClient("APIKey public-test-key", session=session).search(number)
    assert len(records) == 1
    args, kwargs = session.calls[0]
    assert args[0] == DATAJUD_TJPE_URL
    assert kwargs["headers"]["Authorization"] == "APIKey public-test-key"
    assert kwargs["json"]["query"] == {"match": {"numeroProcesso": number}}
    assert kwargs["timeout"] == 30


def test_no_results_is_a_success(number):
    session = FakeSession(FakeResponse({"hits": {"hits": []}}))
    assert DataJudClient("key", session=session).search(number) == []


def test_unauthorized_does_not_leak_key(number):
    session = FakeSession(FakeResponse(status=401))
    with pytest.raises(DataJudError, match="Autenticação recusada") as error:
        DataJudClient("super-public-example-key", session=session).search(number)
    assert "super-public-example-key" not in str(error.value)


def test_http_503_is_handled(number):
    with pytest.raises(DataJudError, match="HTTP 503"):
        DataJudClient("key", session=FakeSession(FakeResponse(status=503))).search(number)


def test_network_timeout_is_handled(number):
    with pytest.raises(DataJudError, match="Falha de rede"):
        DataJudClient("key", session=FakeSession(error=requests.Timeout())).search(number)


def test_malformed_payload_is_rejected(number):
    with pytest.raises(DataJudError, match="Formato inesperado"):
        DataJudClient("key", session=FakeSession(FakeResponse({"other": []}))).search(number)


def test_result_limit_is_guarded(number, hit):
    session = FakeSession(FakeResponse({"hits": {"total": {"value": 21}, "hits": [hit]}}))
    with pytest.raises(DataJudError, match="excedeu o limite"):
        DataJudClient("key", session=session).search(number)


def test_key_is_required():
    with pytest.raises(DataJudError, match="DATAJUD_API_KEY"):
        DataJudClient(" ")
