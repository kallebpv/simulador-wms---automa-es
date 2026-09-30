# FluxoWMS · Simulador para gravar os robôs

Um "WMS de mentira" que roda no seu computador, sem internet, com as mesmas telas e botões que os seus robôs usam — e os próprios robôs, adaptados para rodar nele com dados 100% fictícios.

## Como rodar (8 passos)

1. **Ligue o simulador**: abra a pasta `simulador` e dê dois cliques em **`iniciar_simulador.bat`**. Vai abrir uma janela preta (é o servidor, deixe aberta) e o FluxoWMS no navegador. Para desligar, feche a janela preta.
2. (Opcional) Faça um teste manual no navegador: entre com qualquer usuário e senha e passeie pelo **Menu → WMS → Saida → Pedidos**.
3. **Robô que cria pedidos**: abra `automacoes\robo_cria_pedidos` e dê dois cliques em **`rodar.bat`**. Na primeira vez ele instala o que falta (pode demorar um pouco). A sua tela Tkinter abre já preenchida → clique em **Iniciar Automação**.
4. Assista: o Chrome abre maximizado, faz login e cria um pedido por paciente da planilha. O **painel no canto direito** e a **pílula no topo** mostram o contador, o cronômetro e o log subindo.
5. **Robô de reabastecimento**: `automacoes\robo_reabastecimento\rodar.bat` → **Iniciar Automação**. Ele cria um reabastecimento por tipo (5 no total), aprova, integra e ajusta o pedido de saída gerado.
6. **Avançador de pedidos**: `automacoes\avancador_de_pedidos\rodar.bat` → **Iniciar Automação**. Quando ele pedir o número, digite um pedido **"Em digitação"** (a tela inicial do WMS mostra a lista; ex.: `104519`, ou um que o robô de pedidos acabou de criar, como `104520`). Ele aprova, cria a WSaída, inicia a separação e baixa a picking list em PDF na sua pasta Downloads.
7. **Planilhas novas**: dentro de `automacoes`, rode `python gerar_dados_exemplo.py --pacientes 120` (de 1 a 200 pacientes). Ele gera planilhas novas e bagunçadas, iguais às reais, em `dados_exemplo`.
8. **Recomeçar do zero**: no painel da demonstração, clique em **Reiniciar demonstração** (duas vezes, para confirmar). Pedidos e contadores voltam ao início.

## Dicas para a gravação

- **Velocidade**: em cada `rodar.bat`, mude `VELOCIDADE_DEMO` (1 = ritmo original; 2 = duas vezes mais rápido; 0.5 = mais devagar) e `PAUSA_EXTRA_DEMO` (segundos a mais em cada passo).
- **Teclas no navegador**: **P** esconde/mostra o painel e **H** esconde/mostra a pílula do topo (para tomadas "limpas").
- **Vídeo vertical (9:16)**: títulos, diálogos, avisos e a pílula ficam no centro da tela.
- **Impressão**: o avançador só *simula* a impressão. Para imprimir de verdade, troque `IMPRIMIR_DE_VERDADE = False` por `True` no topo de `avancar_pedido.py`. Para o PDF abrir na tela, use `ABRIR_PDF_NA_DEMO = True`.
- Não rode dois robôs ao mesmo tempo (eles usam o mesmo perfil do Chrome, em `automacoes\_perfil_chrome_demo`).

## Se algo der errado

- **"O simulador FluxoWMS não está ligado"** → faça o passo 1 primeiro.
- **Erro do ChromeDriver** → na primeira execução o Selenium baixa o driver compatível sozinho (precisa de internet só dessa vez). Se preferir, coloque um `chromedriver.exe` da mesma versão do seu Chrome dentro da pasta do robô.
- **Porta 8080 ocupada** → feche o outro programa que usa a porta ou troque `8080` no `iniciar_simulador.bat` e em `URL_SIMULADOR` nos robôs.

## O que tem em cada arquivo

| Arquivo | Para que serve |
|---|---|
| `DECISOES.md` | Tudo o que foi decidido sem perguntar (e onde mudar) |
| `01_INVENTARIO.md` | Quais automações entraram e por quê |
| `02_MAPA_DE_ROTAS.md` | Fluxogramas e todos os botões/campos que os robôs usam |
| `03_TESTES.md` | Resultado dos testes de cada robô |
| `simulador/` | O FluxoWMS (HTML, CSS e JavaScript puros) |
| `automacoes/` | Os seus robôs adaptados (mudanças marcadas com `# [SIMULADOR]`) |
