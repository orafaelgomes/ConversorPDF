# README Técnico — Transforma em PDFa

## Objetivo do projeto

Transforma em PDFa é uma ferramenta para converter arquivos PDF em PDF/A, com foco em:

- validação de conformidade PDF/A,
- processamento em lote,
- execução em background sem janelas de console no Windows,
- interface de gerenciamento de fila em Tkinter.

## Componentes principais

### `main.py`

- Interface principal do usuário em Tkinter.
- Seleção de múltiplos arquivos PDF.
- Escolha de pasta de saída.
- Conversão em lote com barra de progresso.
- Cancelamento de processamento.

### `ui/app.py`

- Workspace protótipo para Fase 3.
- Adição de arquivo e pasta com varredura recursiva.
- Worker pool com número configurável de threads.
- Atualização de status por item e logs por item.

### `verificador_pdfa.py`

- Validação de PDF/A com `verapdf` quando disponível.
- Fallback heurístico usando `PyPDF2`.
- Saída estruturada em dicionário: `status` + `detalhes`.

### `importer.py`

- Varredura de diretórios recursiva ou não.
- Publica eventos JSONL (`logger_json.log_event`).
- Opção `--skip-if-pdfa` para pular arquivos conformes.

### `converter.py`

- Wrapper de Ghostscript com execução segura.
- No Windows, usa `CREATE_NO_WINDOW` para evitar janelas de CMD.
- Retorna `returncode`, `stdout`, `stderr` e `timeout`.

### `ghostscript_bundle.py`

- Localiza Ghostscript no PATH, instalado ou em pastas padrão.
- Pode instalar silenciosamente se o instalador local estiver presente.

### `logger_json.py`

- Gerenciamento de logs estruturados em JSONL.
- Facilita leitura de últimos eventos e logs completos.

## Módulos de documentação existentes

- `docs/IMPORTER.md`: guia de uso do importador em lote.
- `ui/README.md`: documentação do workspace Tkinter.
- `RELEASE_CHECKLIST.md`: passos para release.
- `ROADMAP.md`: plano de desenvolvimento.

## Dependências

- Python 3.10+
- `pyinstaller`
- `PyPDF2`
- `pytest`

Instalação:

```powershell
pip install -r requirements.txt
```

## Execução

### Aplicação principal

```powershell
python main.py
```

### Workspace protótipo

```powershell
python -m ui.app
```

### Importador

```powershell
python -m importer --path "documents/batch-folder" --recursivo --skip-if-pdfa
```

### Validador

```powershell
python -m verificador_pdfa --input <arquivo.pdf>
```

## Pipeline de CI

- `.github/workflows/python-ci.yml`
- Executa testes no Windows e valida instalação.

## Instruções de release

- Gerar artefato com PyInstaller:

```powershell
pyinstaller --noconsole --onefile main.py
```

- Incluir instalador Ghostscript ou binários compatíveis.

## Próximos passos sugeridos

- Unificar `main.py` e `ui/app.py` em uma interface única.
- Externalizar a fila de trabalho para um serviço de background.
- Melhorar a validação PDF/A com suporte a `veraPDF` e múltiplas normas.
- Adicionar testes de integração da interface Tkinter.
