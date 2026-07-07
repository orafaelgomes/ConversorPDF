# Importer — Importação em Lote (Fase 2)

Este documento descreve o uso básico do módulo `importer` responsável pela varredura de diretórios e enfileiramento de arquivos PDF para processamento pela pipeline.

Uso (CLI):

```bash
python -m importer --path <caminho> [--recursivo] [--skip-if-pdfa] [--padroes "*.pdf"]
```

Opções principais:

- `--path, -p`: Caminho para arquivo ou diretório a ser varrido.
- `--recursivo`: Habilita busca recursiva em subpastas (padrão: desabilitado no CLI, mas a função aceita True/False).
- `--skip-if-pdfa`: Pula arquivos que já estejam em conformidade com PDF/A (usa `verificador_pdfa`).
- `--padroes, -g`: Lista de padrões glob para seleção (ex.: `"*.pdf" "*.PDF"`).

Exemplos:

1. Importar todos os PDFs na pasta atual (não recursivo):

```bash
python -m importer --path . --padroes "*.pdf"
```

2. Importar recursivamente e pular arquivos já conformes:

```bash
python -m importer --path "documents/batch-folder" --recursivo --skip-if-pdfa
```

Integração com o verificador:

Ao usar `--skip-if-pdfa`, o `importer` chamará `verificador_pdfa.validar_pdfa` para cada arquivo detectado. A integração é assíncrona e retorna uma lista simplificada dos itens enfileirados para conversão.

Observações de implementação:

- A função `import_folder` devolve uma lista de dicionários com metadados básicos (`path`, `size`, `mtime`).
- Para uso em produção recomenda-se acoplar `importer` a um sistema de filas (Redis/Celery, RQ) quando o volume for alto.
