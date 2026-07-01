# Plano de desenvolvimento da versão 2.0

## Objetivo
Ampliar a aplicação para oferecer uma experiência mais robusta, ágil e preparada para uso em lote, mantendo a simplicidade da interface.

## Fases de desenvolvimento

### Fase 1 - Conversão em lote
- permitir selecionar vários arquivos PDF de uma vez;
- ajustar a lógica para processar múltiplos arquivos;
- pesquisar e aplicar execução paralela para reduzir o tempo total.

### Fase 2 - Interface com status de lote
- exibir o número de arquivos selecionados;
- mostrar uma lista simples dos arquivos em fila;
- adicionar indicadores de status para cada arquivo (pendente, em progresso, concluído, falha).

### Fase 3 - Barra de progresso e controle de saída
- implementar uma barra de progresso geral e local;
- permitir escolher uma pasta de saída comum para todos os arquivos;
- manter opção de salvar no mesmo diretório de origem;
- evitar sobrescritas usando nomes automáticos inteligentes.

### Fase 4 - Tratamento de erros e relatório final
- validar arquivos antes da conversão;
- continuar o processamento mesmo se alguns arquivos falharem;
- gerar um relatório final com número de sucessos e falhas;
- exibir mensagens claras de erro e motivo por arquivo.

### Fase 5 - Aperfeiçoamentos de usabilidade e distribuição
- permitir cancelar a conversão em andamento;
- melhorar a organização visual da tela principal;
- garantir a instalação automática do Ghostscript no pacote final;
- preparar o executável Windows para distribuição.

## Entrega inicial da versão 2.0
Uma versão 2.0 com:
- seleção múltipla de arquivos;
- processamento em lote e execução paralela;
- feedback visual de progresso e resultados;
- relatório de conversão com sucessos e falhas;
- controle de pasta de saída.
