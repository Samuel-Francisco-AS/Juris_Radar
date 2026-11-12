from dataclasses import replace

import pytest

from jurisradar.storage import Repository


def test_persists_and_upserts_without_duplicate_rows(tmp_path, number, record):
    path = tmp_path / "nested" / "test.sqlite3"
    with Repository(path) as repo:
        repo.save_query(number, [record])
        repo.save_query(number, [replace(record, class_name="Classe atualizada")])
        rows = repo.connection.execute("SELECT * FROM processos").fetchall()
        assert len(rows) == 1
        assert rows[0]["classe_nome"] == "Classe atualizada"
        assert "Movimento de teste" in rows[0]["movimentos_json"]
        assert repo.connection.execute("SELECT COUNT(*) FROM consultas").fetchone()[0] == 2
    assert path.exists()


def test_multiple_source_ids_for_same_number(tmp_path, number, record):
    with Repository(tmp_path / "test.sqlite3") as repo:
        repo.save_query(number, [record, replace(record, source_key="TJPE:another-id", degree="G2")])
        assert len(repo.list_processes()) == 2


def test_empty_response_registers_query_without_deleting_previous_data(tmp_path, number, record):
    with Repository(tmp_path / "test.sqlite3") as repo:
        repo.save_query(number, [record])
        repo.save_query(number, [])
        assert len(repo.list_processes()) == 1
        assert repo.connection.execute("SELECT quantidade FROM consultas ORDER BY id DESC LIMIT 1").fetchone()[0] == 0


def test_rolls_back_invalid_batch(tmp_path, number, record):
    with Repository(tmp_path / "test.sqlite3") as repo:
        with pytest.raises(ValueError):
            repo.save_query(number, [record, replace(record, number="9" * 20)])
        assert len(repo.list_processes()) == 0
        assert repo.connection.execute("SELECT COUNT(*) FROM consultas").fetchone()[0] == 0
