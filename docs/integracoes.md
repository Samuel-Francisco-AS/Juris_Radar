# Contrato de integração — DataJud e TJPE

## Escopo inicial

- Endpoint oficial: `POST https://api-publica.datajud.cnj.jus.br/api_publica_tjpe/_search`.
- Cabeçalhos: `Authorization: APIKey <CHAVE_PUBLICA_VIGENTE>`; `Content-Type: application/json`.
- Corpo: Elasticsearch Query DSL (`match` por `numeroProcesso`), `size` limitado a 20 e seleção explícita de campos públicos (`_source`).
- Resposta esperada: `hits.hits[*]._source`, incluindo `numeroProcesso`, `tribunal`, `id`, `grau`, `classe`, `assuntos`, `orgaoJulgador`, `movimentos`, datas. Alguns campos podem estar ausentes.
- Estratégia: rejeitar dados estruturalmente inválidos ou tribunal divergente, ignorar matches aproximados e nunca gravar uma resposta parcial conhecida como completa.
- Chave vigente é divulgada pelo próprio CNJ e pode ser rotacionada; não manter hardcode no projeto.
- O CNJ restringe finalidades e não garante atualização/integridade. Não usar como sistema oficial de prazos.

## TJPE e interfaces RPA

O TJPE publica endpoints do DataJud e documentação de serviços PJe/MNI (SOAP). A divulgação de WSDL não equivale a concessão de acesso autenticado. A interface web de consulta pública pode impor desafios/captcha e outras restrições. **Não automatizar acessos não autorizados, burlar medidas técnicas ou raspar o Jusbrasil.** No MVP 3, o primeiro robô operará em interface controlada pelo próprio projeto, abastecida pela fonte real do DataJud.

## Referências verificadas em 2026-11-12

1. https://datajud-wiki.cnj.jus.br/api-publica/acesso/
2. https://datajud-wiki.cnj.jus.br/api-publica/endpoints/
3. https://datajud-wiki.cnj.jus.br/api-publica/exemplos/exemplo1/
4. https://datajud-wiki.cnj.jus.br/api-publica/glossario/
5. https://datajud-wiki.cnj.jus.br/api-publica/termo-uso/
6. https://portal.tjpe.jus.br/web/transparencia/tic/dados-abertos

## Gate externo pendente

O ambiente de execução usado na implementação não resolve o host `api-publica.datajud.cnj.jus.br`. Portanto não há evidência de sucesso de POST autenticado nem de dados TJPE persistidos a partir da API real. Executar o CLI em ambiente com conexão, registrar status HTTP/estrutura geral sem compartilhar chave ou dados pessoais e ajustar o parser se o esquema observado diferir do documentado.
