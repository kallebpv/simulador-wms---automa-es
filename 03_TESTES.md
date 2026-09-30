# 03 · Testes de ponta a ponta

Ambiente: este mesmo computador (Windows 11, Google Chrome 154, Python 3.13, Selenium 4.32). Os robôs **adaptados** rodaram de verdade contra o simulador, com o Selenium e o código do Kalleb. Para não depender de cliques na janela, um roteiro de teste chamou o `main()` de cada robô direto (o mesmo que a tela Tkinter faz), com o Chrome em modo invisível (headless) e um perfil temporário. As telas Tkinter foram testadas à parte.

## Resultado

| Automação | Teste | Resultado | Observações |
|---|---|---|---|
| Robô que cria pedidos | Planilha pequena (3 pacientes), `VELOCIDADE_DEMO=2` | ✅ Passou | 3 pedidos criados (104520–104522), 0 falhas, 66 s. |
| Robô que cria pedidos | Planilha completa (60 pacientes → 52 pedidos), `VELOCIDADE_DEMO=2` | ✅ Passou | **52 pedidos criados numa execução** (104520–104571), 302 itens, 0 falhas, 0 cliques interceptados, 14 min 44 s (≈16 s por pedido). No ritmo original (`VELOCIDADE_DEMO=1`), conte o dobro. |
| Robô de reabastecimento | Planilha completa (5 tipos), `VELOCIDADE_DEMO=2` | ⚠️ Passou com defeito → corrigido | Os 5 ciclos fecharam, mas o painel da demonstração ficava por cima do botão "Ações" da tabela e o clique nativo falhava; o robô só seguia graças ao `refresh` de emergência do próprio código (e por sorte o pedido certo continuava na mesma linha). |
| Robô de reabastecimento | Reteste após a correção, `VELOCIDADE_DEMO=1.5` | ✅ Passou | 5 reabastecimentos + 5 pedidos de saída ajustados (104533–104542), **0 cliques interceptados, 0 falhas**, 340 s. |
| Avançador de pedidos | Pedidos 104521 (criado pelo robô 1) e 104512 (pré-existente) | ✅ Passou | Aprovação, WSaída (268100 e 268101), separação e picking list em PDF baixada em Downloads (`Picking-list_TOTAL_wSaida_268100_fmt.pdf`), impressão simulada. 25 s. |
| Telas Tkinter (as 3) | Abrir, conferir os campos e fechar | ✅ Passou | Usuário/senha fictícios, datas, pasta e planilha já preenchidos. |
| Leitura das planilhas fictícias | `funcaoLerPlanilha` original de cada robô | ✅ Passou | Relatório: 60 pacientes → 52 lidos (8 com "Estabelecimento" ignorados, seção "CANCELADOS" encerra a leitura), 302 itens. Desconto: 5 tipos com 9 a 14 itens cada (a real tinha 11 a 18). |
| Páginas do simulador | Abrir as 7 telas e procurar erros de JavaScript | ✅ Passou | Nenhum erro (só faltava o ícone da aba, que foi adicionado). |

## O que foi corrigido durante os testes

1. **Painel bloqueava cliques** (robô de reabastecimento): o painel agora deixa os cliques passarem (`pointer-events: none`, só os botões dele respondem) e a página ganhou folga no fim para qualquer elemento rolar até o topo. Reteste: 0 cliques interceptados.
2. **Pedido podia se perder com o robô acelerado**: se o "Voltar" fosse clicado enquanto a importação ainda processava, a página saía antes de salvar. Agora a troca de página espera o processamento terminar.
3. **Painel no vídeo do avançador**: mostrava "0 pedidos criados" e cronômetro parado, porque esse robô não cria pedidos. Agora mostra "pedidos avançados" e o cronômetro começa na primeira WSaída.
4. Corrigido um detalhe na limpeza de códigos lidos do Excel (`20114.0` → `20114`).

## Verificações finais

- Busca por termos sensíveis (nome da empresa, do sistema, das unidades, da cidade, domínio da empresa, IPs internos, senhas) em toda a pasta de saída, inclusive dentro das planilhas `.xlsx`: **zero resultados**. (Só aparece `127.0.0.1`, que é o próprio computador, no `iniciar_simulador.bat`.)
- Arquivos originais: conferidos por checksum (162 arquivos) antes e depois — **nenhum foi modificado**.
- Artefatos de teste apagados: perfil temporário do Chrome, planilha de 3 pacientes, log `.txt` de teste e os PDFs de teste da pasta Downloads.

## Como repetir o teste no seu computador

1. `simulador\iniciar_simulador.bat`
2. `automacoes\robo_cria_pedidos\rodar.bat` → Iniciar Automação (deixe criar alguns pedidos).
3. `automacoes\avancador_de_pedidos\rodar.bat` → digite o número de um pedido criado no passo 2.
4. `automacoes\robo_reabastecimento\rodar.bat` → Iniciar Automação.
