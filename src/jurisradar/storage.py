"""Persistência transacional local em SQLite, sem dados de partes processuais."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from .models import ProcessRecord

DEFAULT_DB = Path("data/jurisradar.sqlite3")


class Repository:
    def __init__(self, path: str | Path = DEFAULT_DB):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS processos (
              source_key TEXT PRIMARY KEY,
              numero TEXT NOT NULL,
              tribunal TEXT NOT NULL,
              grau TEXT,
              classe_codigo INTEGER,
              classe_nome TEXT,
              orgao_codigo INTEGER,
              orgao_nome TEXT,
              data_ajuizamento TEXT,
              ultima_atualizacao TEXT,
              assuntos_json TEXT NOT NULL,
              movimentos_json TEXT NOT NULL,
              consultado_em TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_processos_numero ON processos(numero);
            CREATE TABLE IF NOT EXISTS consultas (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              numero TEXT NOT NULL,
              consultado_em TEXT NOT NULL,
              quantidade INTEGER NOT NULL
            );
            """
        )

    def __enter__(self) -> "Repository":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.connection.close()

    def save_query(self, number: str, processes: Sequence[ProcessRecord]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        # Persiste apenas respostas exitosas. Ausência de resultado não remove dados anteriores.
        with self.connection:
            for process in processes:
                if process.number != number or process.court != "TJPE":
                    raise ValueError("Registro incompatível com a consulta atual.")
                self.connection.execute(
                    """
                    INSERT INTO processos (
                      source_key, numero, tribunal, grau, classe_codigo, classe_nome,
                      orgao_codigo, orgao_nome, data_ajuizamento, ultima_atualizacao,
                      assuntos_json, movimentos_json, consultado_em
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(source_key) DO UPDATE SET
                      numero=excluded.numero, tribunal=excluded.tribunal,
                      grau=excluded.grau, classe_codigo=excluded.classe_codigo,
                      classe_nome=excluded.classe_nome, orgao_codigo=excluded.orgao_codigo,
                      orgao_nome=excluded.orgao_nome, data_ajuizamento=excluded.data_ajuizamento,
                      ultima_atualizacao=excluded.ultima_atualizacao,
                      assuntos_json=excluded.assuntos_json,
                      movimentos_json=excluded.movimentos_json,
                      consultado_em=excluded.consultado_em
                    """,
                    (
                        process.source_key, process.number, process.court, process.degree,
                        process.class_code, process.class_name, process.body_code, process.body_name,
                        process.filing_date, process.updated_at,
                        json.dumps(process.subjects, ensure_ascii=False),
                        json.dumps(process.movements, ensure_ascii=False), now,
                    ),
                )
            self.connection.execute(
                "INSERT INTO consultas (numero, consultado_em, quantidade) VALUES (?, ?, ?)",
                (number, now, len(processes)),
            )

    def list_processes(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """SELECT numero, tribunal, grau, classe_nome, ultima_atualizacao,
                      consultado_em FROM processos ORDER BY consultado_em DESC, numero"""
        ).fetchall()
