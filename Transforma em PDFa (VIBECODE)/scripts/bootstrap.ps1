<#
Bootstrap PowerShell para desenvolvimento (Windows)

Uso:
  - Executar apenas bootstrap (cria venv e instala dependências):
      .\scripts\bootstrap.ps1

  - Executar bootstrap e rodar testes:
      .\scripts\bootstrap.ps1 -RunTests

Observações:
  - Requer `python` no PATH (Python 3.10+).
  - O script usa um ambiente virtual em `.venv`.
  - `verapdf` não é instalado automaticamente; instale-o separadamente se desejar validação completa.
#>

param(
    [switch]$RunTests
)

$ErrorActionPreference = 'Stop'

Write-Host "[bootstrap] Criando ambiente virtual (.venv)..."
python -m venv .venv

if (-not (Test-Path -Path ".venv")) {
    Write-Error "Falha ao criar o ambiente virtual. Verifique se 'python' está no PATH.";
    exit 1
}

Write-Host "[bootstrap] Ativando .venv..."
. .\.venv\Scripts\Activate.ps1

Write-Host "[bootstrap] Atualizando pip..."
python -m pip install --upgrade pip

Write-Host "[bootstrap] Instalando dependências de requirements.txt..."
pip install -r requirements.txt

if (Get-Command verapdf -ErrorAction SilentlyContinue) {
    Write-Host "[bootstrap] verapdf encontrado no PATH. Validação avançada disponível."
} else {
    Write-Warning "[bootstrap] verapdf não encontrado. Validação via verapdf não estará disponível. Instale verapdf se necessário: https://www.verapdf.org/"
}

if ($RunTests) {
    Write-Host "[bootstrap] Executando testes (pytest)..."
    python -m pytest -q
    $code = $LASTEXITCODE
    Write-Host "[bootstrap] pytest finalizado com código: $code"
    exit $code
} else {
    Write-Host "[bootstrap] Concluído. Para executar testes: .\scripts\bootstrap.ps1 -RunTests"
}
