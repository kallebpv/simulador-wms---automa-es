# FluxoWMS · Robôs de logística em Python rodando num WMS simulado

Três automações (RPA) que desenvolvi para uma operação real de logística de saúde, recriadas para portfólio dentro de um WMS de demonstração que roda no navegador, com dados 100% fictícios.

![Robô criando pedidos no FluxoWMS: login, preenchimento do pedido, busca do destinatário e o painel contando os pedidos criados](docs/demo.gif)

*O robô de pedidos rodando no simulador (vídeo acelerado 3,5×).*

## A história

Criei essas automações em Python e Selenium para o dia a dia de uma operação de logística de saúde. Elas rodam em produção e operam o sistema de gestão de armazém (WMS) da empresa, substituindo trabalho manual repetitivo.

Escrevi as versões originais praticamente à mão, antes de usar IA no desenvolvimento. Como não posso mostrar o sistema real nem os dados da operação, reconstruí o cenário com a ajuda de IA: um WMS de demonstração com as mesmas telas e o mesmo fluxo que os robôs percorrem, e as automações adaptadas para rodar nele.

A lógica dos robôs é a mesma da produção. As poucas mudanças feitas para o simulador estão marcadas no código com `# [SIMULADOR]`.

## Resultados na operação real

| Automação | Antes | Com o robô |
|---|---|---|
| Criação de pedidos a partir de planilha | 2 pessoas, cerca de 4 horas por dia | cerca de 200 pedidos por dia criados automaticamente |
| Pedidos de reabastecimento | cerca de 25 minutos no fim do expediente | cerca de 13 minutos |
| Avanço de pedidos | cada etapa feita manualmente no sistema | aprovação, WSaída, separação e picking list em um único fluxo |

## Os robôs

**Robô que cria pedidos** (`automacoes/robo_cria_pedidos`)
Lê um relatório de entregas desorganizado (sem cabeçalho, com um bloco por paciente), extrai produtos e quantidades e cria um pedido por paciente no WMS: preenche destinatário, prioridade, datas e observação e importa os itens em lote.

**Robô de reabastecimento** (`automacoes/robo_reabastecimento`)
Lê a planilha de saída programada, agrupa os itens por tipo e cria os pedidos de reabastecimento. Em seguida passa cada pedido por aprovação e integração e ajusta o pedido de saída gerado.

**Avançador de pedidos** (`automacoes/avancador_de_pedidos`)
A partir do número de um pedido, solicita aprovação, cria a WSaída, inicia a separação e baixa a picking list em PDF.

Os três têm interface desktop em Tkinter, para quem opera não precisar abrir código.

## O simulador

- HTML, CSS e JavaScript puros, sem framework e sem banco de dados. O estado fica em memória.
- Reproduz a estrutura de páginas do sistema original a ponto de os localizadores dos robôs, inclusive XPaths absolutos, funcionarem sem alteração. Os detalhes estão em [`docs/COMO_FUNCIONA.md`](docs/COMO_FUNCIONA.md).
- Tempos de processamento e telas de carregamento simulados, para o fluxo se comportar como um sistema real.
- Painel de demonstração com contador de pedidos, cronômetro e log das ações em tempo real.

## Tecnologias

Python · Selenium · pandas · openpyxl · Tkinter · HTML · CSS · JavaScript

## Como rodar

Requisitos: Windows, Python 3 e Google Chrome.

1. Abra `simulador/iniciar_simulador.bat`. O FluxoWMS abre em `http://localhost:8080` (qualquer usuário e senha entram).
2. Abra o `rodar.bat` da automação desejada, dentro de `automacoes/`. Na primeira execução ele instala as dependências.
3. Na janela do robô, clique em **Iniciar Automação** e acompanhe pelo navegador.

Para gerar novas planilhas de exemplo:

```bash
python automacoes/gerar_dados_exemplo.py --pacientes 120
```

A velocidade dos robôs é ajustada pela variável `VELOCIDADE_DEMO` em cada `rodar.bat`.

## Estrutura

```
├── simulador/                  WMS de demonstração (HTML, CSS, JS)
├── automacoes/
│   ├── robo_cria_pedidos/
│   ├── robo_reabastecimento/
│   ├── avancador_de_pedidos/
│   ├── gerar_dados_exemplo.py  gerador de planilhas fictícias
│   └── requirements.txt
└── docs/
    └── COMO_FUNCIONA.md        fluxos dos robôs e decisões técnicas
```

## Sobre os dados

Todos os nomes, produtos, pacientes, unidades e números deste repositório são fictícios. Nenhum dado, credencial ou endereço do sistema real foi incluído.

## Autor

**Kalleb Vieira**: automação de processos com Python e IA para logística e saúde.

[LinkedIn](https://www.linkedin.com/in/kallebvieira) · [Instagram @kallebcode](https://www.instagram.com/kallebcode)
