# Quickstart — Transforma em PDFa

Este guia rápido mostra como preparar o ambiente, executar a aplicação e testar os módulos principais.

## 1. Preparar o ambiente

1. Abra PowerShell no diretório do projeto.
2. Verifique se o Python 3.10+ está disponível:

```powershell
python --version
```

3. Crie e ative o ambiente virtual (Windows):

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

4. Instale dependências:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. (Opcional) Rodar bootstrap com testes

```powershell
.\scripts\bootstrap.ps1 -RunTests
```

## 3. Executar a aplicação principal

```powershell
python main.py
```

Isso inicia a interface Tkinter para:

- selecionar arquivos PDF
- escolher pasta de saída
- iniciar conversão em lote
- cancelar a conversão

## 4. Rodar o workspace protótipo

```powershell
python -m ui.app
```

Funcionalidades principais:

- adicionar arquivo e pasta
- remover item da lista de trabalho
- iniciar processamento em background
- visualizar status e logs por arquivo

## 5. Validar um PDF individualmente

```powershell
python -m verificador_pdfa --input <caminho_para_arquivo.pdf>
```

O módulo tenta usar `verapdf` quando disponível e faz fallback para uma checagem básica via `PyPDF2`.

## 6. Importar PDFs em lote

```powershell
python -m importer --path "<caminho>" --recursivo --skip-if-pdfa
```

Opções importantes:

- `--recursivo`: varre subpastas
- `--skip-if-pdfa`: pula arquivos já conformes
- `--padroes "*.pdf"`: padrões glob para seleção

## 7. Executar testes

```powershell
python -m pytest -q
```

## 8. Instalar Ghostscript

- Ghostscript é necessário para conversão em PDF/A.
- O projeto tenta localizar o binário automaticamente em PATH ou em caminhos padrão do Windows.
- Se houver instalador local, `ghostscript_bundle.py` pode instalar silenciosamente.

## 9. Dicas rápidas

- Para empacotar o aplicativo:

```powershell
pyinstaller --noconsole --onefile main.py
```

- Se `verapdf` não estiver instalado, a validação usa fallback heurístico com `PyPDF2`.
- Mantenha o diretório `docs/` para guias específicos como `docs/IMPORTER.md`.
