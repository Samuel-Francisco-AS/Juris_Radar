# JurisRadar · MVP 1

**Aplicação Python educacional para consultar metadados públicos de processos do TJPE via API Pública do DataJud/CNJ, interpretar a resposta e salvar registros em SQLite.** O projeto evoluirá para um RPA operacional com Playwright (MVP 3).

> **Situação:** MVP 1 implementado e testado localmente com respostas simuladas. A conexão real com o CNJ **não foi comprovada neste ambiente** (sem conectividade DNS para o endpoint). Não confunda testes automatizados com homologação externa.

## Funcionalidades do MVP 1

- Consulta **pontual, por número CNJ informado**, sem varreduras em massa.
- HTTP POST + JSON (`requests`), `Authorization: APIKey` configurada fora do código, timeout e tentativas limitadas para indisponibilidades transitórias.
- Normalização do número com 20 dígitos, filtro exato dos resultados e interpretação de classe, grau, órgão, assuntos e movimentações.
- Persistência transacional em **SQLite**, separando registros do processo e histórico de consultas. Atualizações não duplicam a mesma chave de origem.
- Comandos para consultar e listar os registros locais; testes automatizados totalmente offline.

## Preparação

Requisitos: **Python 3.10+**. Em Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

No PowerShell, ative `.venv\Scripts\Activate.ps1` em vez de `source`.

**1.** Consulte a [chave pública vigente na Wiki oficial do CNJ](https://datajud-wiki.cnj.jus.br/api-publica/acesso/). Ela pode ser alterada pelo CNJ; não há chave embutida no projeto.

**2.** Configure-a somente na sessão do terminal, sem publicar a chave em issues, screenshots ou commits:

```bash
export DATAJUD_API_KEY='COLE_A_CHAVE_PUBLICA_VIGENTE_AQUI'
```

No PowerShell: `$env:DATAJUD_API_KEY = 'COLE_A_CHAVE_PUBLICA_VIGENTE_AQUI'`.

**3.** Consulte **um processo público do TJPE** para o qual você possua um número CNJ legítimo:

```bash
jurisradar consultar 'NNNNNNN-DD.AAAA.J.TR.OOOO'
jurisradar listar
```

Substitua o número ilustrativo pelo número público de 20 dígitos. Também é possível executar `python -m jurisradar consultar NUMERO` e adicionar `--db caminho/arquivo.sqlite3` a qualquer comando.

**4.** Teste sem internet nem credenciais:

```bash
pytest
```

O banco padrão fica em `data/jurisradar.sqlite3`, ignorado pelo Git. **Não publique exportações de processos reais, dados pessoais ou bancos SQLite** no repositório. O programa não requisita dados de partes ou documentos, apenas metadados.

## Limitações e cuidados

- A API é **beta**, pode estar indisponível, incompleta ou desatualizada. A ausência de registros na resposta **não prova inexistência** de processo.
- Sem consulta a processos sigilosos, sem acesso ao conteúdo de autos, sem automação de CAPTCHA/login do PJe e sem integração não autorizada com Jusbrasil.
- **Não** é sistema jurídico de prazos, avisos de intimação ou aconselhamento jurídico. Não se deve inferir ciência processual por movimentação do DataJud.
- Uso submetido ao [Termo de Uso oficial](https://datajud-wiki.cnj.jus.br/api-publica/termo-uso/) (finalidades legais, não comerciais e autorizadas; observe obrigações de divulgação pública). O usuário deve respeitar limites de uso e privacidade.
- Se houver mais de 20 hits para um número, o programa **interrompe** a persistência em vez de apresentar o resultado como completo; paginação é uma evolução futura.
- Número CNJ é validado quanto a formato e extensão, **não** quanto a dígitos verificadores.

## Arquitetura e evolução

- [ADR 0001 — Arquitetura modular e integração oficial](docs/adr/0001-arquitetura.md)
- [Roadmap e critérios de aceite](docs/roadmap.md)
- [Contrato da API e observações para RPA](docs/integracoes.md)

## Documentação oficial

- [CNJ: acesso e autenticação](https://datajud-wiki.cnj.jus.br/api-publica/acesso/)
- [CNJ: endpoint por tribunal](https://datajud-wiki.cnj.jus.br/api-publica/endpoints/)
- [CNJ: exemplo de busca por número](https://datajud-wiki.cnj.jus.br/api-publica/exemplos/exemplo1/)
- [CNJ: glossário](https://datajud-wiki.cnj.jus.br/api-publica/glossario/)
- [TJPE: acesso automatizado por sistemas externos](https://portal.tjpe.jus.br/web/transparencia/tic/dados-abertos)

*Projeto independente, sem vínculo institucional com CNJ/TJPE.*
