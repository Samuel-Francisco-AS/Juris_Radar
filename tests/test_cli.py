from jurisradar import cli


def test_cli_consulta_and_list(monkeypatch, tmp_path, capsys, number, record):
    db = tmp_path / "test.sqlite3"
    monkeypatch.setenv("DATAJUD_API_KEY", "public-key-example")

    class StubClient:
        def __init__(self, key):
            assert key == "public-key-example"

        def search(self, query_number):
            assert query_number == number
            return [record]

    monkeypatch.setattr(cli, "DataJudClient", StubClient)
    assert cli.main(["consultar", number, "--db", str(db)]) == 0
    assert "1 registro(s)" in capsys.readouterr().out
    assert cli.main(["listar", "--db", str(db)]) == 0
    assert "Classe fictícia" in capsys.readouterr().out


def test_cli_rejects_invalid_number_without_calling_api(capsys):
    assert cli.main(["consultar", "123"]) == 1
    assert "20 dígitos" in capsys.readouterr().err
