# 01 · Inventário e triagem das automações

Pasta analisada: `arquivos das automações e coisas que fiz\Automação (Projetos de Robôs)\` (somente leitura; nada foi alterado lá).

Ignorados por serem artefatos de empacotamento ou ambiente: `build/`, `dist/`, `venv/`, `.exe`, `chromedriver.exe`, `.ico`, `.pyz`, `.toc`. Os `.spec` foram lidos só para descobrir o ponto de entrada de cada executável.

> Observação: todos os arquivos estão com data de modificação de 29/09/2026 (foram copiados hoje), então o critério "data de modificação" não serviu para desempatar. Valeram o `.spec` e o ano no nome da pasta.

## Categorias

- **A** — opera o WMS pelo navegador (Selenium) → entrou no simulador.
- **B** — ferramenta local de planilha/PDF → fica fora do simulador, mas rende vídeo.
- **C** — fora do escopo.

## Tabela

| Automação (pasta) | Arquivos de código | Versão escolhida | Motivo | Cat. |
|---|---|---|---|---|
| **Robô que cria pedidos** — `Projeto Robo que cria pedidos(versao_pos_erro_01.10.2025)` | `interface.py`, `criar_pedido.py`, `funcaos.py`, `funcaoLerPlanilha.py` | `interface.py` → `criar_pedido.py` | Ponto de entrada de `interface.spec` e `MeuApp.spec`. É a única versão deste robô (o `criar_pedido.py` da pasta AVANCADOR é outro fluxo). Lê o relatório por paciente e cria um **Pedido Normal** por paciente. | **A** |
| **Robô de reabastecimento ("desconto") 2026** — `PROJETO_DESCONTO_AUTOMACAO_2026` | `interface.py`, `criar_pedido.py`, `funcaos.py`, `funcaoLerPlanilha.py`, `LerPlanilhaDesconto.ipynb` | `interface.py` → `criar_pedido.py` | Ponto de entrada de `Automacao_Reabastecimento.spec` e `interface.spec`; pasta 2026. Cria um pedido de reabastecimento por TIPO da aba "SAÍDA PROGRAMADA", aprova, integra e depois ajusta o pedido de saída gerado. | **A** |
| **Avançador de pedidos 2026** — `AVANCADOR_DE_PEDIDOS_2026` | `interface.py`, `avancar_pedido.py`, `funcaos.py`, `criar_pedido.py`, `LerPlanilhaDesconto.ipynb` | `interface.py` → `avancar_pedido.py` | Ponto de entrada de `interface.spec`; confirmado pela documentação ("Automação Avançador de Pedidos 2026"). Pede o nº do pedido, solicita aprovação, cria a WSaída, inicia a separação e imprime a picking list. | **A** |
| ↳ `AVANCADOR_DE_PEDIDOS_2026/criar_pedido.py` | — | descartado | Cópia incompleta do robô de reabastecimento (usa variáveis que não existem, como `qt_itens_tratado` e `tipo`) e não é importada pela interface. | C |
| ↳ `LerPlanilhaDesconto.ipynb` (2 cópias idênticas) | — | descartado | Rascunho de leitura da planilha; a lógica final está em `funcaoLerPlanilha.py`. | C |
| **Montador da planilha de desconto** — `ROBO_DESCONTO_FINAL` | `interface.py`, `funcoes_robo_desconto.py` (+ `(1)`), `funcao_tratar_PL_Almox.py`, `concatenador_Almox.py`, `concatenador_saidas.py`, notebooks, `teste.py`, `exemplo_TKinter.py` | `interface.py` | Ponto de entrada de `excecutor_do_reabastecimento.spec`. Não usa navegador: junta 4 planilhas no modelo e gera a planilha que alimenta o robô de reabastecimento. `funcoes_robo_desconto(1).py` só difere num trecho comentado; `teste(1).ipynb` é idêntico a `teste.ipynb`. | **B** |
| **Separador de números** — `Numeros_na_planilha_python` | `separa_numeros_auxiliar_zin.py` | o próprio | Ponto de entrada do `.spec`. Lê "Total de Produtos" de cada grupo e escreve o total ao lado, preservando a formatação. | **B** |
| **Digitador de planilha** — `PROJETO_ROBO_DIGITADOR_DE_PLANILHA` | `roboPL1.py`, `copia.py`, `funcao.py`, `funcaoLerPlanilha.py`, `teste.ipynb` | `roboPL1.py` | Ponto de entrada de `roboPL1.spec`. Não opera o WMS: extrai produto/código/total de relatórios `.xls` e salva `_final.xlsx`. | **B** |
| **Alimentador do radar (protótipo)** — `alimentador_do_radar - protótipo tela` | `interface.py`, `criador_de_planilha.py` | `interface.py` | Ponto de entrada do `.spec`. Lê o `.txt` de log gerado pelo robô de pedidos (INICIANDO/FINALIZANDO) e monta uma planilha de resultados. Não usa navegador. | **B** |
| **Mesclador de PDFs** — `MESCLADOR DE PDFS NA PASTA LOCAL` | só `.exe` | — | Ferramenta local de PDF, sem código-fonte na pasta. | **B** |
| **Novo Radar 2026** — pasta `PROJETO_NOVO_RADAR_…_2026` | `schema.sql`, `seed.sql` | — | Esquema de banco (PostgreSQL); não opera o WMS. | **C** |
| **Documentação geral** — `_Documentação Geral` | 2 `.docx`, 1 `.xlsx` | — | Lida para contexto (manual do Avançador e e-mail de apresentação). | C |

## Como ficaram na pasta de saída

| Automação | Pasta adaptada |
|---|---|
| Robô que cria pedidos | `automacoes/robo_cria_pedidos/` |
| Robô de reabastecimento 2026 | `automacoes/robo_reabastecimento/` |
| Avançador de pedidos 2026 | `automacoes/avancador_de_pedidos/` |
