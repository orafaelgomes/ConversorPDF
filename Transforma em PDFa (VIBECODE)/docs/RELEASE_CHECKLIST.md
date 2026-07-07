# Release Checklist — Versão 3.0

## Pré-release

- [ ] Atualizar dependências em `requirements.txt`
- [ ] Verificar se `scripts/bootstrap.ps1` funciona no ambiente Windows
- [ ] Confirmar que `verificador_pdfa.py` está operacional com PyPDF2 ou verapdf
- [ ] Confirmar que `converter.py` executa Ghostscript sem abrir janela CMD
- [ ] Verificar `ui/app.py` e o fluxo de workspace
- [ ] Validar logs estruturados em `logs/import.log`

## Testes

- [ ] Executar `python -m pytest -q` com sucesso
- [ ] Verificar testes de cancelamento e importação em lote
- [ ] Testar UI manualmente em Windows
- [ ] Validar arquivos de saída gerados com sufixo `_pdfa.pdf`

## Empacotamento

- [ ] Gerar executável PyInstaller usando `pyinstaller --noconsole --onefile main.py`
- [ ] Confirmar inclusão de `gs10071w64.exe` ou instalador nos artefatos
- [ ] Verificar que a aplicação não exibe o prompt de comando ao converter

## Release

- [ ] Atualizar `README.md` e `ROADMAP.md` com status final
- [ ] Criar tag `v3.0.0`
- [ ] Empurrar release no GitHub com notas de mudança
- [ ] Confirmar artefatos de release disponíveis para download
