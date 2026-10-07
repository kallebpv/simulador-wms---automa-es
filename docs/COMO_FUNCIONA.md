# Como funciona

Este documento explica o caminho que cada robô percorre no WMS e as decisões técnicas que permitiram rodar as automações de produção num sistema simulado, com o mínimo de mudanças no código.

## Esperas e robustez

Todas as ações dos robôs passam pelas funções de `funcaos.py`, que esperam o elemento ficar **clicável** (`element_to_be_clickable`) ou **presente** (`presence_of_element_located`). Se o elemento não aparece, a função tenta de novo com tempos maiores (5 s, depois 30 s) e, por último, recarrega a página e espera mais 40 s. Os pontos em que o robô lê a tela imediatamente, sem esperar, estão marcados com ⚡ nos fluxos abaixo.

## Fluxo de cada robô

### Robô que cria pedidos (`robo_cria_pedidos`)

```mermaid
flowchart TD
  A[Planilha: relatório por paciente<br/>funcaoLerPlanilha.processar_planilha] --> B
  B[driver.get URL] --> C[Entrar → usuário/senha → Login]
  C --> D[Módulo WMS]
  D --> E[Menu: WMS → Saida → Pedidos → fechar menu]
  E --> F{Para cada paciente}
  F --> G[Criar pedido → Normal]
  G --> H[Tipo de saída = SAÍDA PADRÃO<br/>Projeto = PROJETO ESPECIAL]
  H --> I[Lupa destinatário → digita UNIDADE NORTE → Pesquisar → Selecionar]
  I --> J[Prioridade 0 · data · Crítico + motivo · Observação + dados do paciente]
  J --> K[Importar CSV → OK no aviso → cola código⭾qtd → Importar]
  K --> L["⚡ lê h2 'Pedido Normal # N'"]
  L --> M[grava INICIANDO/FINALIZANDO no .txt]
  M --> N[Voltar] --> F
```

### Robô de reabastecimento (`robo_reabastecimento`)

```mermaid
flowchart TD
  A[Planilha SAÍDA PROGRAMADA<br/>agrupa CÓD + PEDIDO por TIPO] --> B[Login → WMS]
  B --> C[Menu: WMS → Saida → Armazém → Pedidos de reabastecimento]
  C --> D[Pesquisa → data de criação → Pesquisar]
  D --> E{Para cada TIPO}
  E --> F[Novo → unidade origem/destino → projeto origem/destino]
  F --> G[Importar CSV → OK → cola itens → Importar]
  G --> H["⚡ lê h2 'Pedido # N'"]
  H --> I[Voltar → Pesquisa → nº do pedido → Pesquisar]
  I --> J[Menu da linha → Solicitar aprovação → lê código lbl_random → digita → OK]
  J --> K[Menu → Aprovar pedido → código → OK]
  K --> L[Menu → Submeter integração → código → OK]
  L --> M[Menu lateral → Pedidos de saída]
  M --> N["Pesquisar → Observação = 'PEDIDO: N' → Filtrar"]
  N --> O[Menu da linha 4 → Desaprovar → justificativa AJUSTE DE PEDIDO → OK]
  O --> P[Editar → SAÍDA PADRÃO → ⚡ lê 'Pedido Normal # N2']
  P --> Q[Prioridade 0 · Crítico + motivo · data de expedição · observação → Salvar]
  Q --> R[Voltar → menu → Pedidos de reabastecimento] --> E
```

### Avançador de pedidos (`avancador_de_pedidos`)

```mermaid
flowchart TD
  A[Tkinter: usuário, senha, impressora] --> B[Login → WMS → Saida → Pedidos]
  B --> C{Diálogo: número do pedido}
  C --> D[Pesquisar → nº do pedido → Filtrar]
  D --> E[Menu da linha 4 → Solicitar aprovação → OK]
  E --> F[Menu → Criar WSaída → OK]
  F --> G["⚡ lê '(100%)' do atendimento"]
  G -->|100%| H[Criar WSaída → lê código → digita → OK]
  H --> I["⚡ lê número da WSaída"]
  I --> J[Voltar → menu → Iniciar separação → OK]
  J --> K[Impressora → Picking list total → PDF]
  K --> L[espera o PDF em Downloads → imprime*]
  L --> M{Processar outro?}
  M -->|sim| C
  G -->|< 100%| M
```
\* Na demonstração a impressão é simulada (`IMPRIMIR_DE_VERDADE = False`).

## Como as planilhas viram dados no sistema

| Robô | Planilha | Colunas/linhas lidas | Vira |
|---|---|---|---|
| Cria pedidos | Relatório por paciente (sem cabeçalho; tudo na coluna C) | Linha com o identificador do paciente (no simulador: `Registro de paciente: 1234567_12345678`) + linha `Paciente:` (até a linha com `Agendado`) | Texto somado à **Observação** (`#mobs_ped`) e ao `.txt` de log |
| | | Blocos com `Estabelecimento` nas 2 linhas seguintes ao identificador | Ignorados |
| | | Após a linha com `Produto`: 1º valor não vazio da coluna D em diante = código; próximo número = quantidade | Linhas `código⭾qtd` no **#produtos** |
| | | Linha com `cancelado` | Encerra a leitura |
| Reabastecimento | Aba `SAÍDA PROGRAMADA` | `TIPO`, `CÓD`, `PEDIDO ` (com espaço), só `PEDIDO` ≠ vazio/0 | Um pedido de reabastecimento por TIPO; `CÓD⭾PEDIDO` na importação; o TIPO vai na observação do pedido de saída |
| Avançador | — | Número digitado no diálogo | Filtro `#filtro_nnumero_ped` |

## Como o simulador mantém os localizadores originais funcionando

1. **Contagem de `<div>` no `<body>`**: cada tela tem exatamente os mesmos `div` filhos do `body` que o original. Os diálogos ficam nas posições que os robôs esperam (ex.: `div[15]`, `div[16]`, `div[19]`, `div[24]`) com `<div class="slot">` invisíveis preenchendo as posições intermediárias.
2. **Tudo que o simulador adiciona dinamicamente ao `body`** (painel da demonstração, avisos, carregamento, faixa do rodapé) usa `<aside>`, `<section>` e `<footer>`, nunca `<div>`, para não mudar a contagem.
3. **Linhas auxiliares na tabela de pedidos**: as 3 primeiras linhas do `tbody` (resumo, "atualizando", "nenhum resultado") fazem o 1º pedido cair em `tr[4]`, como no original.
4. **Menus por status com posições fixas**: o menu de ações sempre tem 8 itens; o que muda é o texto (ex.: `li[6]` é "Solicitar aprovação" em digitação e "Iniciar separação" com WSaída criada).
5. **Mudança de status esconde a linha na hora do clique** e só redesenha depois do "processamento": o robô, que espera o elemento ficar clicável, nunca clica num menu desatualizado.
6. **Painel e avisos não bloqueiam cliques** (`pointer-events: none`), e a página tem folga no fim para qualquer elemento poder rolar até o topo: os robôs mais antigos usam clique nativo, que falha se algo estiver por cima.
