"""Ponto de entrada via terminal: consultar e listar processos TJPE."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys

from .integrations import DataJudClient, DataJudError
from .models import InvalidProcessNumber, normalize_number
from .storage import DEFAULT_DB, Repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jurisradar", description="Consulta educacional de metadados processuais do TJPE via DataJud."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    consult = commands.add_parser("consultar", help="Consultar um processo por número CNJ")
    consult.add_argument("numero", help="Número CNJ com 20 dígitos, formatado ou não")
    consult.add_argument("--db", default=str(DEFAULT_DB), help="Caminho do banco SQLite local")
    listing = commands.add_parser("listar", help="Mostrar registros já salvos no SQLite")
    listing.add_argument("--db", default=str(DEFAULT_DB), help="Caminho do banco SQLite local")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "listar":
            with Repository(args.db) as repo:
                processes = repo.list_processes()
            if not processes:
                print("Nenhum processo salvo ainda.")
                return 0
            for p in processes:
                print(f"{p['numero']} | {p['tribunal']} | {p['grau'] or '-'} | {p['classe_nome'] or '-'}")
            return 0

        number = normalize_number(args.numero)
        api_key = os.getenv("DATAJUD_API_KEY", "")
        client = DataJudClient(api_key)
        processes = client.search(number)
        with Repository(args.db) as repo:
            repo.save_query(number, processes)
        print(f"Consulta concluída: {len(processes)} registro(s) para {number}.")
        if not processes:
            print("Nenhum registro público encontrado. Isso não prova inexistência do processo.")
        for process in processes:
            print(f"- {process.court} | {process.degree or '-'} | {process.class_name or '-'}")
            print(f"  Órgão: {process.body_name or 'não informado'}")
            print(f"  Movimentações retornadas: {len(process.movements)}")
            print(f"  Atualização na origem: {process.updated_at or 'não informada'}")
        print(f"Banco SQLite: {args.db}")
        return 0
    except (InvalidProcessNumber, DataJudError, sqlite3.Error, OSError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
