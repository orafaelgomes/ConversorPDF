# ROADMAP detalhado — Fase 3 (UI/UX e Workspace)

Este roadmap organiza a Fase 3 em sprints curtos e tarefas atômicas para implementar o workspace interativo e o painel de status em tempo real.

Visão: entregar uma interface desktop mínima e extensível que permita criar uma lista de trabalho, adicionar/remover arquivos e acompanhar o status de cada arquivo sem bloquear a UI.

Formato: sprints de 2 semanas (estimativa), cada tarefa listada com criticidade e saída esperada.

## Sprint 1 (2 semanas) — Esqueleto e Fluxo Básico

- Tarefa 1.1: Criar esqueleto da aplicação UI (Tkinter) — Alta
  - Entregável: `ui/app.py` com janela principal, lista de trabalho, botões `Adicionar arquivo`, `Adicionar pasta`, `Remover`, `Iniciar`.

- Tarefa 1.2: Background worker simples — Alta
  - Entregável: worker em thread que executa processamento sem bloquear UI; canal de comunicação via fila (queue) e polling de eventos.

- Tarefa 1.3: Integração com `importer` e `verificador_pdfa` — Alta
  - Entregável: botão `Iniciar` dispara varredura/importação e validação; atualiza estados no UI.

## Sprint 2 (2 semanas) — Painel de Status e Logs

- Tarefa 2.1: Painel de status por arquivo — Alta
  - Entregável: colunas/ícones para `Convertido`, `Já é PDF/A`, `Em processamento`, `Falha/Erro`.

- Tarefa 2.2: Exibição de log curto (3 linhas) por item — Média
  - Entregável: painel de detalhe que mostra resumo do log e link/abertura para logs completos (arquivos JSONL).

- Tarefa 2.3: Persistência temporária do workspace — Baixa
  - Entregável: salvar/recuperar lista de trabalho em arquivo `workspace.json`.

## Sprint 3 (2 semanas) — Operações Dinâmicas e Performance

- Tarefa 3.1: Adicionar/Remover dinamicamente durante execução — Alta
  - Entregável: suportar enfileiramento e remoção de itens enquanto workers estão rodando.

- Tarefa 3.2: Controle de paralelismo e limites de workers — Média
  - Entregável: opção para configurar número de workers e ver métricas básicas (throughput).

## Sprint 4 (2 semanas) — UI/UX Polishing e Internacionalização

- Tarefa 4.1: Melhorias visuais e mensagens de erro claras — Média
  - Entregável: layout responsivo, textos traduzíveis.

- Tarefa 4.2: Testes de usabilidade rápidos e correções — Média
  - Entregável: ajustar fluxos críticos com base em feedback.

## Critérios de aceitação da Fase 3

- A interface não deve travar durante operações de I/O e conversão (todos os trabalhos rodam em background).
- Estados por item atualizados em tempo real (latência aceitável: <1s).
- Logs de falha devem ser visíveis no UI e persistidos em `logs/import.log`.

## Dependências e Riscos

- `verapdf` (opcional) para validação completa — se ausente, o sistema usa heurísticas (PyPDF2).
- A escolha de toolkit UI (Tkinter) mantém baixa complexidade; migrar para Electron/PyQt pode ser considerado se for necessária maior sofisticação.

## Próximos passos imediatos

1. Criar `ui/app.py` com funcionalidade mínima (sprint 1 entregável 1.1).
2. Implementar worker em thread e comunicação por fila.
3. Integrar chamadas a `importer.import_folder` e `verificador_pdfa.validar_pdfa`.
