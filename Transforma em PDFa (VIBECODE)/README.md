# Conversor de PDF para PDF/A

Esta é a versão inicial de uma aplicação simples para Windows, com interface baseada em menus e fluxo básico para selecionar um arquivo PDF e gerar uma saída em formato PDF/A.

## Como executar

1. Instale o Python 3.10 ou superior.
2. Mantenha o instalador do Ghostscript chamado `gs10071w64.exe` na pasta do projeto.
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute a aplicação:
   ```bash
   python main.py
   ```

## Empacotamento para distribuição

Para gerar um executável Windows preparado para uso, execute:

```bash
pyinstaller --noconsole --onefile --add-binary "gs10071w64.exe;." main.py
```

O aplicativo tentará instalar automaticamente o Ghostscript a partir do instalador incluído na pasta do executável.

## Observação
A saída será gerada como um novo arquivo com o sufixo `_pdfa.pdf` no mesmo diretório do arquivo de origem.

## Próximos passos

- adicionar um verificador de conformidade PDF/A;
- permitir seleção de diretório de saída;
- tratar arquivos já em PDF/A e conversão em lote.
