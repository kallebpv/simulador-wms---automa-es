/* =====================================================================
   FluxoWMS · estado.js
   Todo o "banco" do simulador: um objeto em memória, salvo no
   localStorage para sobreviver à troca de páginas. Sem servidor.
   ===================================================================== */

const Estado = (function () {
  const CHAVE = "fluxowms.estado.v1";
  const CHAVE_SESSAO = "fluxowms.sessao";   // sessionStorage: 1 por aba/execução do robô

  let dados = null;

  /* ---------- utilitários ---------- */
  function agora() { return Date.now(); }
  function hojeBR(deslocDias) {
    const d = new Date(); d.setDate(d.getDate() + (deslocDias || 0));
    return String(d.getDate()).padStart(2, "0") + "/" + String(d.getMonth() + 1).padStart(2, "0") + "/" + d.getFullYear();
  }
  function aleatorio(n) { return Math.floor(Math.random() * n); }
  function escolher(lista) { return lista[aleatorio(lista.length)]; }
  function copia(o) { return JSON.parse(JSON.stringify(o)); }

  function itensAleatorios(qtd, categoria) {
    const base = DADOS_DEMO.produtos.filter(function (p) { return !categoria || p[2] === categoria; });
    const usados = {};
    const itens = [];
    while (itens.length < qtd && itens.length < base.length) {
      const p = escolher(base);
      if (usados[p[0]]) continue;
      usados[p[0]] = true;
      itens.push({ cod: p[0], desc: p[1], qtd: [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 30, 60][aleatorio(13)] });
    }
    return itens;
  }

  /* ---------- dados iniciais (pedidos já existentes no "sistema") ---------- */
  function semear() {
    const pedidos = [];
    const statusSemente = [
      "EXPEDIDO", "EXPEDIDO", "EXPEDIDO", "SEPARACAO", "SEPARACAO", "SEPARACAO",
      "WSAIDA", "APROVADO", "APROVADO", "APROVADO",
      "DIGITACAO", "DIGITACAO", "DIGITACAO", "DIGITACAO", "DIGITACAO", "DIGITACAO",
      "DIGITACAO", "DIGITACAO", "DIGITACAO", "DIGITACAO"
    ];
    let wsaida = DADOS_DEMO.primeiroNumeroWSaida - 40;
    statusSemente.forEach(function (st, i) {
      const numero = DADOS_DEMO.primeiroNumeroPedido - statusSemente.length + i;
      const dest = escolher(DADOS_DEMO.destinatarios);
      const p = {
        numero: numero,
        tipo: "Normal",
        tipoMov: "SAÍDA PADRÃO",
        projeto: escolher(["PROJETO ESPECIAL", "PROJETO ROTINA"]),
        destinatario: dest.nome,
        prioridade: String(aleatorio(3)),
        dataSeparacao: hojeBR(aleatorio(3)),
        critico: Math.random() < 0.3,
        motivoCritico: "",
        obs: escolher(["Entrega programada", "Reposição mensal", "Atendimento de rotina", "Retirada no balcão"]),
        itens: itensAleatorios(3 + aleatorio(9)),
        status: st,
        criadoEm: agora() - (statusSemente.length - i) * 3600 * 1000,
        semente: true
      };
      if (st === "WSAIDA" || st === "SEPARACAO" || st === "EXPEDIDO") {
        p.wsaida = { numero: wsaida++, criadaEm: p.criadoEm + 600000 };
      }
      pedidos.push(p);
    });

    const reabs = [];
    const statusReab = ["INTEGRADO", "INTEGRADO", "INTEGRADO", "APROVADO", "AGUARDANDO", "RASCUNHO"];
    statusReab.forEach(function (st, i) {
      const numero = DADOS_DEMO.primeiroNumeroPedido - 60 + i;
      reabs.push({
        numero: numero,
        origem: "FLUXO CD MATRIZ",
        destino: escolher(["UNIDADE NORTE", "UNIDADE SUL", "UNIDADE LESTE"]),
        projOrigem: "PROJETO ESPECIAL",
        projDestino: "PROJETO ESPECIAL",
        itens: itensAleatorios(6 + aleatorio(8)),
        status: st,
        dataCriacao: hojeBR(-1 - aleatorio(4)),
        criadoEm: agora() - (10 - i) * 86400000 / 3,
        semente: true
      });
    });

    return {
      versao: 1,
      usuario: "",
      proximoPedido: DADOS_DEMO.primeiroNumeroPedido,
      proximaWSaida: DADOS_DEMO.primeiroNumeroWSaida,
      pedidos: pedidos,
      reabs: reabs,
      totais: { pedidos: 0, itens: 0, aprovacoes: 0, wsaidas: 0, pickings: 0 },
      sessao: null
    };
  }

  /* ---------- sessão (contador e cronômetro do painel) ---------- */
  function idSessaoAtual() {
    let id = null;
    try { id = sessionStorage.getItem(CHAVE_SESSAO); } catch (e) { }
    if (!id) {
      id = "s" + agora().toString(36) + aleatorio(1000);
      try { sessionStorage.setItem(CHAVE_SESSAO, id); } catch (e) { }
    }
    return id;
  }
  function novaSessao(id) {
    return { id: id, inicio: agora(), primeiroPedidoEm: null, ultimoPedidoEm: null, pedidos: 0, itens: 0, aprovacoes: 0, wsaidas: 0, pickings: 0, log: [] };
  }

  /* ---------- carregar / salvar ---------- */
  function carregar() {
    if (dados) return dados;
    try {
      const bruto = localStorage.getItem(CHAVE);
      if (bruto) dados = JSON.parse(bruto);
    } catch (e) { dados = null; }
    if (!dados || dados.versao !== 1) dados = semear();
    const id = idSessaoAtual();
    if (!dados.sessao || dados.sessao.id !== id) dados.sessao = novaSessao(id);
    salvar();
    return dados;
  }

  function salvar() {
    try { localStorage.setItem(CHAVE, JSON.stringify(dados)); } catch (e) { }
    document.dispatchEvent(new CustomEvent("estado-mudou"));
  }

  function reiniciar() {
    try {
      Object.keys(localStorage).forEach(function (k) { if (k.indexOf("fluxowms.") === 0) localStorage.removeItem(k); });
      Object.keys(sessionStorage).forEach(function (k) { if (k.indexOf("fluxowms.") === 0) sessionStorage.removeItem(k); });
    } catch (e) { }
    dados = null;
    carregar();
  }

  /* ---------- log e contadores ---------- */
  function registrar(texto, tipo) {
    carregar();
    dados.sessao.log.unshift({ t: agora(), texto: texto, tipo: tipo || "info" });
    dados.sessao.log = dados.sessao.log.slice(0, 40);
    salvar();
  }

  function contar(campo, n) {
    carregar();
    dados.totais[campo] = (dados.totais[campo] || 0) + (n || 1);
    dados.sessao[campo] = (dados.sessao[campo] || 0) + (n || 1);
    if (campo === "pedidos" || campo === "wsaidas") {   // o cronômetro começa no 1º pedido criado OU avançado
      if (!dados.sessao.primeiroPedidoEm) dados.sessao.primeiroPedidoEm = agora();
      dados.sessao.ultimoPedidoEm = agora();
    }
  }

  /* ---------- numeração ---------- */
  function reservarNumeroPedido() {
    carregar();
    const n = dados.proximoPedido++;
    salvar();
    return n;
  }
  function reservarNumeroWSaida() {
    carregar();
    const n = dados.proximaWSaida++;
    salvar();
    return n;
  }

  /* ---------- pedidos de saída ---------- */
  function pedidos() { return carregar().pedidos; }
  function pedido(numero) {
    return pedidos().find(function (p) { return String(p.numero) === String(numero); }) || null;
  }
  function salvarPedido(p) {
    const lista = carregar().pedidos;
    const i = lista.findIndex(function (x) { return x.numero === p.numero; });
    if (i >= 0) lista[i] = p; else lista.push(p);
    salvar();
  }

  /* ---------- pedidos de reabastecimento ---------- */
  function reabs() { return carregar().reabs; }
  function reab(numero) {
    return reabs().find(function (r) { return String(r.numero) === String(numero); }) || null;
  }
  function salvarReab(r) {
    const lista = carregar().reabs;
    const i = lista.findIndex(function (x) { return x.numero === r.numero; });
    if (i >= 0) lista[i] = r; else lista.push(r);
    salvar();
  }

  /* ---------- conversão da colagem "código<TAB>quantidade" ---------- */
  function interpretarColagem(texto) {
    const itens = [];
    String(texto || "").split(/\r?\n/).forEach(function (linha) {
      linha = linha.trim();
      if (!linha) return;
      const partes = linha.split(/\t|;/).map(function (s) { return s.trim(); }).filter(Boolean);
      if (partes.length < 2) return;
      const cod = partes[0].replace(/\.0+$/, "");   // "20114.0" (número lido do Excel) vira "20114"
      const qtd = parseFloat(String(partes[1]).replace(",", "."));
      if (!cod || !isFinite(qtd) || qtd <= 0) return;
      const prod = DADOS_DEMO.produtoPorCodigo[cod.toUpperCase()];
      itens.push({ cod: cod, desc: prod ? prod.descricao : "Item " + cod, qtd: qtd });
    });
    return itens;
  }

  return {
    carregar: carregar, salvar: salvar, reiniciar: reiniciar,
    registrar: registrar, contar: contar,
    reservarNumeroPedido: reservarNumeroPedido, reservarNumeroWSaida: reservarNumeroWSaida,
    pedidos: pedidos, pedido: pedido, salvarPedido: salvarPedido,
    reabs: reabs, reab: reab, salvarReab: salvarReab,
    interpretarColagem: interpretarColagem,
    hojeBR: hojeBR, copia: copia, aleatorio: aleatorio,
    get dados() { return carregar(); }
  };
})();
