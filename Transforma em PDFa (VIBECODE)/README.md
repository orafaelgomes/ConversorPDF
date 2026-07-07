# Transforma em PDFa

Conversor de arquivos PDF para PDF/A com validação, importação em lote, UI de workspace e execução assíncrona/sem janela de console no Windows.

> Consulte também:
>
> - `QUICKSTART.md` — guia rápido de setup e uso.
> - `README_TECHNICAL.md` — visão técnica e resumo dos componentes.

## Índice rápido

- [Visão geral do estado atual](#vis%C3%A3o-geral-do-estado-atual)
- [Como executar](#como-executar)
- [Principais recursos atuais](#principais-recursos-atuais)
- [CI e Release](#ci-e-release)
- [Dependências](#depend%C3%AAncias)
- [Observações de arquitetura](#observa%C3%A7%C3%B5es-de-arquitetura)
- [Próximos passos](#pr%C3%B3ximos-passos)

## Visão geral do estado atual

O projeto já conta com:

- `main.py`: aplicação principal com interface Tkinter para seleção de PDFs, escolha de pasta de saída, conversão em lote, progresso e cancelamento.
- `ghostscript_bundle.py`: busca do Ghostscript no sistema, projeto local ou instalação silenciosa a partir de instalador presente.
- `verificador_pdfa.py`: backend de validação PDF/A com suporte a `verapdf` e fallback heurístico usando `PyPDF2`.
- `importer.py`: módulo de importação em lote com varredura de diretórios e opção `--skip-if-pdfa`.
- `converter.py`: executor seguro de Ghostscript em background para conversões sem janela de console no Windows.
- `logger_json.py`: logger JSONL para eventos de arquivo e leitura de logs recentes/completos.
- `ui/app.py`: protótipo de workspace dinâmico com painel de status, controles de workers e logs por item.

Também há suporte adicional:

- `scripts/bootstrap.ps1`: bootstrap para criar ambiente virtual, instalar dependências e executar testes no Windows.
- `.github/workflows/python-ci.yml`: pipeline GitHub Actions para validar código e executar testes.
- `RELEASE_CHECKLIST.md`: checklist de release orientado para distribuição Windows.
- `ROADMAP.md`: roadmap com sprints e tarefas para as fases de desenvolvimento.

## Estrutura de arquivos

- `main.py` — UI principal desktop para converter PDFs em lote.
- `ui/app.py` — workspace de status com lista dinâmica e worker pool.
- `verificador_pdfa.py` — validação de conformidade PDF/A.
- `importer.py` — varredura e importação em lote de pastas.
- `converter.py` — conversor Ghostscript que evita janelas de CMD no Windows.
- `logger_json.py` — logs estruturados em `logs/import.log`.
- `ghostscript_bundle.py` — busca e instalação silenciosa de Ghostscript.
- `requirements.txt` — dependências do projeto.

## Como executar

### Usar a aplicação principal

```powershell
python main.py
```

### Usar o workspace protótipo

```powershell
python -m ui.app
```

### Validar um PDF individualmente

```powershell
python -m verificador_pdfa --input documents/test_samples/sample.pdf
```

### Executar importação em lote

```powershell
python -m importer --path "documents/batch-folder" --recursivo --skip-if-pdfa
```

### Preparar ambiente de desenvolvimento

```powershell
.\scripts\bootstrap.ps1
```

### Rodar testes

```powershell
python -m pytest -q
```

## Principais recursos atuais

- Conversão em lote de PDFs para PDF/A.
- Busca automática de Ghostscript e instalação silenciosa se disponível.
- Validação prévia de PDF/A com fallback heurístico.
- Pipeline de worker em background para manter a UI responsiva.
- Controle de paralelismo com número de workers configurável.
- Logs estruturados JSONL por arquivo com preview e visualização completa.
- Cancelamento de processamento em andamento.
- Pipeline de CI GitHub Actions configurado para Windows.

## CI e Release

- CI configurado em `.github/workflows/python-ci.yml`.
- Release checklist em `RELEASE_CHECKLIST.md`.
- Use `pyinstaller --noconsole --onefile main.py` para empacotar a aplicação.
- Inclua `gs10071w64.exe` ou instalador de Ghostscript junto ao artefato de release.

## Dependências

- Python 3.10+
- `pyinstaller`
- `PyPDF2`
- `pytest`

Instale todas as dependências com:

```powershell
pip install -r requirements.txt
```

## Observações de arquitetura

- A conversão usa `subprocess.Popen` com `creationflags=subprocess.CREATE_NO_WINDOW` no Windows para evitar janelas de CMD.
- A UI secundária em `ui/app.py` demonstra workflow de workspace com atualização de status e logs por item.
- O módulo `importer.py` registra itens enfileirados usando `logger_json.log_event` para rastreabilidade.
- `verificador_pdfa.py` tenta `verapdf` e, se indisponível, usa `PyPDF2` para inferir conformidade.

## Próximos passos

- Consolidar o workspace `ui/app.py` como interface principal de gestão de fila.
- Expandir validação de PDF/A além do fallback heurístico.
- Adicionar relatórios de performance e métricas de throughput.
- Formalizar release final com artefatos PyInstaller.

---

_Documento reconstruído com base no estado atual do projeto._
