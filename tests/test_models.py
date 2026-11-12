import pytest

from jurisradar.models import InvalidDataJudResponse, InvalidProcessNumber, normalize_number, parse_hit


def test_normalizes_formatted_cnj_number():
    assert normalize_number("0000000-00.0000.0.00.0000") == "0" * 20


@pytest.mark.parametrize("value", ["123", "a" * 20, "1" * 21, "0000000000000000000x"])
def test_rejects_invalid_numbers(value):
    with pytest.raises(InvalidProcessNumber):
        normalize_number(value)


def test_parses_source_and_preserves_movements(number, hit):
    record = parse_hit(hit, expected_number=number)
    assert record.source_key.startswith("TJPE:")
    assert record.class_name == "Classe fictícia"
    assert record.movements[0]["codigo"] == 26


def test_discards_another_process_number(number, hit):
    hit["_source"]["numeroProcesso"] = "9" * 20
    assert parse_hit(hit, expected_number=number) is None


def test_rejects_missing_source(number):
    with pytest.raises(InvalidDataJudResponse):
        parse_hit({"_id": "a"}, expected_number=number)


def test_rejects_wrong_court(number, hit):
    hit["_source"]["tribunal"] = "TJSP"
    with pytest.raises(InvalidDataJudResponse):
        parse_hit(hit, expected_number=number)


def test_rejects_no_source_identifier(number, hit):
    del hit["_id"]
    del hit["_source"]["id"]
    with pytest.raises(InvalidDataJudResponse):
        parse_hit(hit, expected_number=number)
