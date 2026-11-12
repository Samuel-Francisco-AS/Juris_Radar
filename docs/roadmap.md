# Roadmap — JurisRadar

**Objetivo:** desenvolver portfólio funcional com integrações reais e um fluxo de RPA demonstrável, mantendo compatibilidade com uso local e termos oficiais.

## MVP 1 — Integração DataJud/TJPE (implementado; homologação externa pendente)

- [x] Estrutura de pacote Python, CLI, configuração de API key externa.
- [x] Consulta pontual via POST oficial do TJPE; controle de timeout/retry e erros de autenticação/rede.
- [x] Parsing de metadados, filtro de número exato e registros de múltiplas origens.
- [x] SQLite transacional; histórico de consultas e atualização de registros existentes.
- [x] Testes unitários/offline e documentação de setup.
- [ ] **Gate externo:** consulta autenticada real com processo público do TJPE, conferência dos campos e avaliação da cobertura/limitações. Não realizada neste ambiente por falta de resolução DNS.

**Aceite:** com chave vigente e conectividade, o usuário consegue consultar um número público e depois verificar os dados salvos pelo comando `listar`; testes offline passam. Documentar eventuais limitações observadas na homologação.

## MVP 2 — Monitoramento e relatórios (planejado)

- [ ] Modelo de snapshots e comparação entre consultas sem confundir ausência de resposta com exclusão de movimentos.
- [ ] Deduplificação com identificadores robustos para eventos repetidos e trilha de alterações.
- [ ] Histórico de falhas, reexecução controlada, limites de consumo e logs sem dados sensíveis.
- [ ] CSV/Excel, agendamento opt-in e relatório de verificações.

**Aceite:** detectar alterações entre duas respostas de teste, registrar apenas diferenças consistentes e gerar relatório, sem transformar achados em avisos oficiais de prazo.

## MVP 3 — Robô RPA operacional (planejado; foco do portfólio)

- [ ] Definir processo administrativo de ponta a ponta em interface própria ou explicitamente autorizada.
- [ ] Implementar Playwright com seletores resilientes, preenchimento, validação e evidências.
- [ ] Incluir reexecução segura, checkpoints, estados de tarefa e recuperação após falha.
- [ ] Testes E2E do fluxo operacional, com falhas simuladas e vídeo curto de demonstração.

**Aceite:** executar uma rotina observável de interface de forma repetível, com logs e validação do resultado; não contornar CAPTCHA, autenticação ou proteções de portais.

## MVP 4 — Apresentação profissional (planejado)

- [ ] Painel local opcional, métricas de execução, documentação final.
- [ ] Tutorial reproduzível, diagrama atualizado, roteiro de demonstração e screenshots com dados fictícios.
- [ ] Revisão de acessibilidade, privacidade, licença e publicação do portfólio.

**Aceite:** terceiro consegue instalar, executar testes offline e compreender claramente os recursos e limitações sem credenciais privadas.
