# Decisões tomadas sem perguntar

Tudo o que foi decidido durante a construção, com o motivo. Se quiser mudar algo, cada item diz onde mexer.

## Escopo e versões

1. **Três automações entraram no simulador** (categoria A): robô que cria pedidos, robô de reabastecimento 2026 e avançador de pedidos 2026. Critério principal: ponto de entrada do `.spec` (o que virou executável). Detalhes em `01_INVENTARIO.md`.
2. **`AVANCADOR_DE_PEDIDOS_2026/criar_pedido.py` ficou de fora**: é uma cópia incompleta do robô de reabastecimento (usa variáveis que não existem) e a interface não usa esse arquivo.
3. **Ferramentas de planilha/PDF ficaram fora do simulador** (montador da planilha de desconto, separador de números, digitador, alimentador do radar, mesclador de PDF). Não operam o navegador. Estão citadas no relatório como material para vídeo.

## Sigilo

4. **Nomes reais trocados por fictícios** (no código adaptado, no simulador e nas planilhas):

   | Original (tipo) | Fictício |
   |---|---|
   | Unidade de origem da empresa | `FLUXO CD MATRIZ` |
   | Unidade de destino / destinatário | `UNIDADE NORTE` |
   | Projeto usado nos pedidos | `PROJETO ESPECIAL` |
   | Motivo de criticidade | `Demanda Prioritária` |
   | Nome do sistema | FluxoWMS |
   | Coluna/aba da planilha com o nome do sistema e da unidade | `ESTOQ. WMS UNIDADE`, `WMS_REL.SINTETICO.PROD` |
   | Aba com nome de cidade | `ESTOQUE CD CENTRAL` |

   O nome do projeto e o motivo de criticidade originais não são nomes próprios, mas também foram trocados por cautela (juntos, descreveriam demais a operação real). Cada linha alterada tem o comentário `# [SIMULADOR]`.
5. **Credenciais**: nenhum `.py` original tinha senha gravada (o login vem da tela Tkinter). O que havia era **a URL interna do sistema** em 4 arquivos (lista no relatório final). No código adaptado a URL virou a constante `URL_SIMULADOR = "http://localhost:8080/"` e as telas já vêm com `usuario_demo` / `demo123`.
6. **Planilhas reais**: foram abertas só para ler nomes de colunas, tipos e contagens (nenhuma linha foi copiada ou exibida). O **relatório por paciente** do robô de pedidos não estava na pasta; a estrutura foi deduzida da função `processar_planilha` e do formato do `.txt` de log (só o formato, com letras e números mascarados).
7. **Git**: criei um repositório em `simulador-wms` para registrar as etapas. O primeiro commit tinha as cópias originais (ainda com a URL interna), então **apaguei o repositório e recriei** só depois de sanitizar — o histórico não tem nada sensível. A pasta `_perfil_chrome_demo` e os logs `.txt` gerados pelos robôs ficam fora do git (`.gitignore`).

## Simulador

8. **Nenhum XPath do Kalleb foi trocado.** Em vez de mudar os localizadores absolutos (`/html/body/div[4]/...`), o simulador reproduz a mesma estrutura de `<div>`. Os "truques" estão no fim do `02_MAPA_DE_ROTAS.md`.
9. **"Gerenciar WSaída" é um modo da própria tela de pedidos**, e não outra página: o avançador lê o percentual e o número da WSaída **sem esperar** logo depois do OK. Numa página nova ele poderia ler antes de carregar.
10. **"Pesquisar" e os grupos do menu só abrem** (clicar de novo não fecha; há um "×" / a setinha para recolher). No sistema real a página recarregava e o painel voltava fechado; aqui isso garante que o robô sempre encontra o filtro aberto.
11. **Solicitar aprovação de um pedido de saída já aprova** ("dentro da alçada"): o avançador pede a aprovação e, em seguida, já vai em "Criar WSaída".
12. **Atendimento sempre 100%**: o avançador só continua quando o estoque atende 100%. Na demo não há falta de estoque.
13. **Números**: pedidos começam em **104520** (o título mostra só os dígitos, porque o robô usa o regex `Pedido Normal #\s*(\d+)`; no painel e nos avisos aparece `PED-104520`). WSaídas começam em **268100**. Pedidos 104500–104519 já existem (10 deles "Em digitação", prontos para o avançador).
14. **O pedido nasce na importação dos produtos** (como no original, não há "salvar" depois de importar). É aí que o contador do painel sobe. O pedido de saída gerado pela integração do reabastecimento aparece no log, mas não entra no contador de "pedidos criados".
15. **Painel de demonstração**: canto inferior direito, recolhível, com contador, cronômetro (corre desde o 1º pedido e congela após 60 s sem atividade), média por pedido, mini contadores e log. Há também uma **pílula no topo central** (contador + cronômetro + última ação) que cabe no corte 9:16. Teclas: **P** esconde/mostra o painel, **H** a pílula.
16. **Contadores "nesta execução"**: cada vez que um robô abre o Chrome começa uma sessão nova (contador e cronômetro zerados), mas os pedidos continuam no sistema. Assim o avançador enxerga os pedidos criados pelo robô de pedidos.
17. **Painel e avisos não bloqueiam cliques** (`pointer-events: none`) e a página tem folga embaixo. Motivo: no 1º teste o painel ficou por cima do botão "Ações" e o clique nativo dos robôs mais antigos falhou (ver `03_TESTES.md`).
18. **Trocar de página espera o "processando" terminar**: se o robô clicar em "Voltar" enquanto a importação ainda está rodando, o simulador conclui a importação antes de sair. Sem isso, um pedido podia se perder com `VELOCIDADE_DEMO` alta.
19. **Visual**: marca FluxoWMS com logo próprio (setas de fluxo em degradê verde-água → roxo), tema claro, fonte do sistema (Segoe UI) a partir de 17 px, títulos e diálogos centralizados. Nada de internet: sem fontes ou bibliotecas externas.
20. **PDF da picking list gerado no próprio navegador** (sem biblioteca), com o nome exato que o robô procura: `Picking-list_TOTAL_wSaida_<nº>_fmt.pdf`.
21. Arquivos a mais além dos pedidos no guia: `app.js` (peças compartilhadas), `pagina_*.js` (lógica de cada tela) e `favicon.svg`.

## Automações adaptadas

22. **`chromedriver.exe` não foi copiado.** Se existir um na pasta do robô, ele é usado; senão o Selenium baixa sozinho o driver compatível com o Chrome instalado (precisa de internet só na primeira vez). O `raise` do original foi comentado com `# [SIMULADOR]`.
23. **Chrome preparado para gravação** (`opcoes_chrome_demo()` em `funcaos.py`): janela maximizada, sem a faixa "controlado por software automatizado", sem pop-up de senha, downloads direto na pasta Downloads e um perfil próprio em `automacoes/_perfil_chrome_demo` (compartilhado pelos 3 robôs; não rode dois ao mesmo tempo).
24. **Impressão simulada no avançador**: `IMPRIMIR_DE_VERDADE = False` no topo de `avancar_pedido.py` (evita gastar papel). `ABRIR_PDF_NA_DEMO = True` abre o PDF na tela depois de baixar (deixei `False` para a janela do PDF não cobrir a pergunta "Deseja processar outro pedido?").
25. **`VELOCIDADE_DEMO` e `PAUSA_EXTRA_DEMO`** (em `funcaos.py`, controlados pelo `rodar.bat`): multiplicam as pausas que já existiam. O avançador vem com `PAUSA_EXTRA_DEMO=0.6`, porque o original não tem pausa nenhuma e ficaria rápido demais para o vídeo. Faixa recomendada de `VELOCIDADE_DEMO`: 0,5 a 2.
26. **Telas Tkinter mantidas**, só com os campos pré-preenchidos (usuário/senha fictícios, datas, pasta `dados_exemplo`, planilha mais recente). Dá para apagar e digitar na hora, se quiser mostrar isso no vídeo.
27. **Chamada duplicada removida** em `robo_cria_pedidos/interface.py`: o botão "Iniciar" chamava a automação duas vezes (uma na thread, outra direto e sem `controle`). A segunda abria e fechava um Chrome extra e travava a janela. Comentei com `# [SIMULADOR]`.
28. **Planilhas de exemplo em `.xlsx`** (as reais eram `.xls`/`.xlsx`); o `pandas` lê as duas. O gerador lê o catálogo de produtos direto do `simulador/dados_demo.js`, então os códigos nunca ficam dessincronizados.
29. Na máquina foram instalados `openpyxl`, `pyperclip` e `xlrd` (necessários para ler planilhas e rodar os robôs). `selenium`, `pandas`, `psutil` e `pywin32` já estavam instalados.
30. **"Registro de paciente" como identificador** (pedido do Kalleb): o rótulo e a numeração originais ficavam realistas demais na Observação do pedido. Agora a planilha fictícia traz `Registro de paciente: 1234567_12345678`, e o `funcaoLerPlanilha.py` do robô de pedidos procura esse rótulo (3 linhas marcadas com `# [SIMULADOR]`).
31. **Nada que remeta ao sistema público de saúde** (pedido do Kalleb): siglas e termos ligados ao sistema do governo foram trocados nas planilhas fictícias. A aba principal do reabastecimento se chama "SAÍDA PROGRAMADA" (com a coluna "SAÍDAS DO DIA" e a aba "BASE SAÍDAS DO DIA"), e o relatório do robô de pedidos virou "Relatório de Entregas Programadas" (`RELATORIO_ENTREGAS_<data>.xlsx`). O `funcaoLerPlanilha.py` do robô de reabastecimento lê a aba nova (linha marcada com `# [SIMULADOR]`).

## Tempo de cada etapa (para a série "Refiz com IA")

Horários desta sessão (29/09/2026), com o relógio do computador:

| Etapa | Início | Duração aproximada |
|---|---|---|
| 1 · Inventário e triagem (leitura de ~35 arquivos, varredura de credenciais) | 00:31 | ~10 min |
| 2 · Engenharia reversa das rotas | 00:41 | ~10 min (feita junto com o desenho do simulador) |
| 3 · Construção do simulador (7 telas, painel, PDF) | 00:50 | ~20 min |
| 4 · Adaptação das automações + gerador de planilhas | 01:05 | ~10 min |
| 5 · Testes de ponta a ponta com os robôs de verdade + correções + documentação | 01:08 | ~35 min |
| **Total** | | **cerca de 1 h 20 min** |
