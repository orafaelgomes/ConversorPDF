# UI — Esqueleto do Workspace

Este diretório contém um esqueleto de interface usando `tkinter` para a Fase 3.

Como executar:

```bash
python -m ui.app
```

Funcionalidades atuais (esqueleto):

- Adicionar arquivo / Adicionar pasta (varredura recursiva usando `importer.scan_folder`).
- Remover item da lista de trabalho.
- Iniciar processamento: executa validação em background (thread) e atualiza o status por item.

Observações:

- Este é um ponto de partida — para produção considere usar `asyncio`+`tkinter` integration, ou migrar para framework com threads/loop reativo.
