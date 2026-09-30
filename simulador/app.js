/* =====================================================================
   FluxoWMS · app.js
   Peças compartilhadas pelas telas: barra do topo, menu lateral,
   diálogos, carregamento, avisos (toasts), menus de ação e PDF.

   IMPORTANTE (compatibilidade com os robôs): elementos criados aqui e
   pendurados direto no <body> usam <section>, <aside> e <footer>, nunca
   <div>. Assim a contagem /html/body/div[N] usada nos XPaths absolutos
   dos robôs continua igual à do sistema original.
   ===================================================================== */

const App = (function () {
  let idSvg = 0;

  /* ---------------- utilidades ---------------- */
  function $(sel, raiz) { return (raiz || document).querySelector(sel); }
  function $$(sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function atraso(min, max) { return Math.round(min + Math.random() * ((max || min) - min)); }
  function lerLocal(chave, padrao) {
    try { const v = localStorage.getItem(chave); return v ? JSON.parse(v) : padrao; } catch (e) { return padrao; }
  }
  function gravarLocal(chave, valor) { try { localStorage.setItem(chave, JSON.stringify(valor)); } catch (e) { } }
  function lerSessao(chave) { try { return sessionStorage.getItem(chave); } catch (e) { return null; } }
  function gravarSessao(chave, valor) { try { sessionStorage.setItem(chave, valor); } catch (e) { } }
  function parametro(nome) { return new URLSearchParams(location.search).get(nome); }
  function rotuloPedido(n) { return "PED-" + n; }
  function qtd(n) { return Number(n).toLocaleString("pt-BR", { maximumFractionDigits: 2 }); }
  function hora(t) { return new Date(t).toLocaleTimeString("pt-BR"); }
  function codigoAleatorio() { return String(100000 + Math.floor(Math.random() * 900000)); }

  function logo(tamanho) {
    idSvg++;
    const id = "lg" + idSvg;
    return '<svg viewBox="0 0 40 40" width="' + (tamanho || 40) + '" height="' + (tamanho || 40) + '" aria-hidden="true">' +
      '<defs><linearGradient id="' + id + '" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2dd4bf"/><stop offset="1" stop-color="#6d5dfc"/></linearGradient></defs>' +
      '<rect width="40" height="40" rx="11" fill="url(#' + id + ')"/>' +
      '<path d="M10 11h14.5l4.5 4.5-4.5 4.5H10z" fill="#fff"/>' +
      '<path d="M10 22h9.5l4.5 4.5-4.5 4.5H10z" fill="#fff" opacity=".72"/>' +
      '<circle cx="31" cy="26.5" r="2.4" fill="#fff" opacity=".9"/></svg>';
  }

  /* ---------------- status ---------------- */
  const STATUS_PEDIDO = {
    DIGITACAO: ["Em digitação", "st-azul"],
    APROVADO: ["Aprovado", "st-verde"],
    WSAIDA: ["WSaída criada", "st-roxo"],
    SEPARACAO: ["Em separação", "st-ambar"],
    EXPEDIDO: ["Expedido", "st-teal"],
    CANCELADO: ["Cancelado", "st-vermelho"]
  };
  const STATUS_REAB = {
    RASCUNHO: ["Rascunho", "st-cinza"],
    AGUARDANDO: ["Aguardando aprovação", "st-ambar"],
    APROVADO: ["Aprovado", "st-verde"],
    INTEGRADO: ["Integrado", "st-teal"]
  };
  function etiqueta(mapa, st) {
    const s = mapa[st] || [st, "st-cinza"];
    return '<span class="st ' + s[1] + '">' + esc(s[0]) + "</span>";
  }

  /* ---------------- sobreposições (nunca <div> no body!) ---------------- */
  function criarSobreposicoes() {
    if (!$("#veu")) {
      const veu = document.createElement("section"); veu.id = "veu"; document.body.appendChild(veu);
    }
    if (!$("#barraProgresso")) {
      const b = document.createElement("section"); b.id = "barraProgresso"; document.body.appendChild(b);
    }
    if (!$("#cartaoCarregando")) {
      const c = document.createElement("section"); c.id = "cartaoCarregando";
      c.innerHTML = '<i></i><span>Carregando…</span>'; document.body.appendChild(c);
    }
    if (!$("#toasts")) {
      const t = document.createElement("section"); t.id = "toasts"; document.body.appendChild(t);
    }
    if (!$("footer.faixa-demo")) {
      const f = document.createElement("footer"); f.className = "faixa-demo";
      f.textContent = "Ambiente de demonstração · dados fictícios"; document.body.appendChild(f);
    }
  }

  let contCarregando = 0;
  function carregando(ativo, texto) {
    const barra = $("#barraProgresso"), cartao = $("#cartaoCarregando");
    if (!barra) return;
    if (ativo) {
      contCarregando++;
      cartao.querySelector("span").textContent = texto || "Carregando…";
      barra.classList.remove("ativa"); void barra.offsetWidth; barra.classList.add("ativa");
      cartao.classList.add("ativo");
    } else {
      contCarregando = Math.max(0, contCarregando - 1);
      if (contCarregando === 0) { barra.classList.remove("ativa"); cartao.classList.remove("ativo"); }
    }
  }

  /* Mostra "processando", espera 300–1200 ms e executa fn. */
  function processar(texto, fn, min, max) {
    carregando(true, texto);
    setTimeout(function () {
      carregando(false);
      try { fn(); } catch (e) { console.error(e); toast("Erro inesperado: " + e.message, "erro"); }
    }, atraso(min || 300, max || 1200));
  }

  /* Troca de página. Se ainda houver algo "processando" (ex.: importação de
     produtos), espera terminar antes de sair — assim nada se perde mesmo com
     o robô acelerado. */
  function navegar(url, texto) {
    function ir() {
      if (contCarregando > 0) { setTimeout(ir, 120); return; }
      carregando(true, texto || "Carregando…");
      setTimeout(function () { location.href = url; }, atraso(300, 650));
    }
    ir();
  }

  function toast(html, tipo, ms) {
    const caixa = $("#toasts"); if (!caixa) return;
    const icones = { ok: "✓", erro: "!", aviso: "!", roxo: "★", info: "i" };
    const t = document.createElement("section");
    t.className = "toast " + (tipo || "ok");
    t.innerHTML = '<span class="ico">' + (icones[tipo || "ok"] || "✓") + "</span><span>" + html + "</span>";
    caixa.appendChild(t);
    setTimeout(function () { t.classList.add("sai"); setTimeout(function () { t.remove(); }, 320); }, ms || 3200);
  }

  function selo(titulo, sub) {
    const s = document.createElement("section");
    s.className = "selo-sucesso";
    s.innerHTML = '<span class="circ">✓</span><strong>' + titulo + "</strong><span>" + (sub || "") + "</span>";
    document.body.appendChild(s);
    setTimeout(function () { s.remove(); }, 2000);
  }

  /* ---------------- diálogos ---------------- */
  function abrirDialogo(el) {
    $("#veu").classList.add("aberto");
    el.classList.remove("tremer");
    el.classList.add("aberto");
    const foco = el.querySelector("input:not([type=hidden]), textarea");
    if (foco) setTimeout(function () { try { foco.focus(); } catch (e) { } }, 60);
  }
  function fecharDialogo(el) {
    el.classList.remove("aberto");
    if (!$$(".ui-dialog.aberto").length) $("#veu").classList.remove("aberto");
  }
  function tremer(el) { el.classList.remove("tremer"); void el.offsetWidth; el.classList.add("tremer"); }

  /* ---------------- menus de ação nas tabelas (td > div.acoes > span + ul) ---------------- */
  function ligarMenusDeAcao() {
    document.addEventListener("click", function (ev) {
      const gatilho = ev.target.closest(".acoes > span");
      if (gatilho) {
        const caixa = gatilho.parentElement;
        const abrir = !caixa.classList.contains("aberta");
        fecharMenusDeAcao();
        if (abrir) caixa.classList.add("aberta");
        return;
      }
      if (!ev.target.closest(".acoes")) fecharMenusDeAcao();
    });
  }
  function fecharMenusDeAcao() { $$(".acoes.aberta").forEach(function (m) { m.classList.remove("aberta"); }); }

  /* ---------------- barra do topo (body/div[1]) ---------------- */
  function montarTopo() {
    const topo = $(".topbar"); if (!topo) return;
    const usuario = (Estado.dados.usuario || "usuario_demo");
    topo.innerHTML =
      '<div class="topbar-in">' +
      '<a class="marca" href="wms.html">' + logo(40) +
      '<span><span class="marca-nome">Fluxo<b>WMS</b></span><br><span class="marca-sub">' + esc(DADOS_DEMO.subtitulo) + "</span></span></a>" +
      '<span class="espaco"></span>' +
      '<span class="chip-demo">Demonstração</span>' +
      '<span class="relogio"></span>' +
      '<span class="chip-usuario"><i>' + esc(usuario.charAt(0).toUpperCase()) + "</i>" + esc(usuario) + "</span>" +
      "</div>";
    const relogio = topo.querySelector(".relogio");
    function tic() { relogio.textContent = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }); }
    tic(); setInterval(tic, 15000);
  }

  /* ---------------- menu lateral (body/div[2]) ----------------
     Textos e classes iguais aos que os robôs procuram:
     a.list-group-item com "WMS", "Saida", "Armazém", "Pedidos",
     "Pedidos de reabastecimento"; span.menu-anchor-opendata;
     #closeMenuOpendata > span.
     A ordem importa: "Pedidos" precisa vir antes de
     "Pedidos de reabastecimento" (o XPath usa contains()).        */
  function montarMenu(atual) {
    const menu = $("#menuOpendata"); if (!menu) return;
    menu.innerHTML =
      '<div class="menu-cab"><a class="marca" href="wms.html">' + logo(32) + '<span class="marca-nome">Fluxo<b>WMS</b></span></a>' +
      '<div id="closeMenuOpendata" title="Fechar menu"><span>×</span></div></div>' +
      '<nav class="list-group">' +
      '<a class="list-group-item" data-ir="wms.html" data-pagina="inicio">Início</a>' +
      '<a class="list-group-item grupo" data-grupo="wms">WMS</a>' +
      '<div class="sub" data-sub="wms">' +
      '  <a class="list-group-item grupo" data-grupo="entrada">Entrada</a>' +
      '  <div class="sub" data-sub="entrada">' +
      '    <a class="list-group-item em-breve">Recebimento</a>' +
      '    <a class="list-group-item em-breve">Conferência cega</a>' +
      "  </div>" +
      '  <a class="list-group-item grupo" data-grupo="saida">Saida</a>' +
      '  <div class="sub" data-sub="saida">' +
      '    <a class="list-group-item" data-ir="pedidos.html" data-pagina="pedidos">Pedidos</a>' +
      '    <a class="list-group-item em-breve">WSaídas</a>' +
      '    <a class="list-group-item grupo" data-grupo="armazem">Armazém</a>' +
      '    <div class="sub" data-sub="armazem">' +
      '      <a class="list-group-item" data-ir="reabastecimento.html" data-pagina="reabastecimento">Pedidos de reabastecimento</a>' +
      '      <a class="list-group-item em-breve">Endereçamento</a>' +
      "    </div>" +
      '    <a class="list-group-item em-breve">Expedição</a>' +
      "  </div>" +
      '  <a class="list-group-item grupo" data-grupo="estoque">Estoque</a>' +
      '  <div class="sub" data-sub="estoque">' +
      '    <a class="list-group-item em-breve">Posição de estoque</a>' +
      '    <a class="list-group-item em-breve">Inventário</a>' +
      "  </div>" +
      "</div>" +
      '<a class="list-group-item em-breve">Relatórios</a>' +
      "</nav>" +
      '<div class="menu-rodape">FluxoWMS · ambiente de demonstração</div>';

    const expandidos = lerLocal("fluxowms.menu", {});
    function expandir(grupo, salvar) {
      const a = menu.querySelector('a.grupo[data-grupo="' + grupo + '"]');
      const sub = menu.querySelector('.sub[data-sub="' + grupo + '"]');
      if (!a || !sub) return;
      a.classList.add("expandido"); sub.classList.add("expandido");
      if (salvar) { expandidos[grupo] = true; gravarLocal("fluxowms.menu", expandidos); }
    }
    function recolher(grupo) {
      menu.querySelector('a.grupo[data-grupo="' + grupo + '"]').classList.remove("expandido");
      menu.querySelector('.sub[data-sub="' + grupo + '"]').classList.remove("expandido");
      delete expandidos[grupo]; gravarLocal("fluxowms.menu", expandidos);
    }
    Object.keys(expandidos).forEach(function (g) { expandir(g, false); });

    // Grupos: clicar sempre EXPANDE (idempotente). Só recolhe se clicar na setinha (canto direito).
    $$("a.grupo", menu).forEach(function (a) {
      a.addEventListener("click", function (ev) {
        ev.preventDefault();
        const g = a.dataset.grupo;
        const naSeta = ev.offsetX > a.clientWidth - 36 && ev.isTrusted;
        if (a.classList.contains("expandido") && naSeta) recolher(g); else expandir(g, true);
      });
    });
    $$("a[data-ir]", menu).forEach(function (a) {
      if (a.dataset.pagina === atual) a.classList.add("atual");
      a.addEventListener("click", function (ev) {
        ev.preventDefault();
        gravarSessao("fluxowms.menuAberto", "1");   // a próxima tela abre com o menu aberto (como no original)
        navegar(a.dataset.ir, "Abrindo " + a.textContent.trim() + "…");
      });
    });
    $$("a.em-breve", menu).forEach(function (a) {
      a.addEventListener("click", function (ev) { ev.preventDefault(); toast("Tela fora do roteiro da demonstração.", "aviso", 2200); });
    });

    $("#closeMenuOpendata").addEventListener("click", fecharMenu);
    const fundo = $(".menu-fundo"); if (fundo) fundo.addEventListener("click", fecharMenu);

    if (lerSessao("fluxowms.menuAberto") === "1") abrirMenu();
  }
  function abrirMenu() {
    $("#menuOpendata").classList.add("aberto");
    const f = $(".menu-fundo"); if (f) f.classList.add("aberto");
    gravarSessao("fluxowms.menuAberto", "1");
  }
  function fecharMenu() {
    $("#menuOpendata").classList.remove("aberto");
    const f = $(".menu-fundo"); if (f) f.classList.remove("aberto");
    gravarSessao("fluxowms.menuAberto", "0");
  }

  /* ---------------- barra de navegação (body/div[4]/div[1]) ---------------- */
  function montarSubbar(trilha) {
    const sb = $(".subbar"); if (!sb) return;
    sb.innerHTML = '<span class="menu-anchor-opendata">Menu</span><span class="trilha">' + (trilha || "") + "</span>";
    sb.querySelector(".menu-anchor-opendata").addEventListener("click", abrirMenu);
  }

  /* ---------------- início de cada tela interna ---------------- */
  function iniciar(opcoes) {
    opcoes = opcoes || {};
    Estado.carregar();
    criarSobreposicoes();
    montarTopo();
    montarMenu(opcoes.atual);
    montarSubbar(opcoes.trilha);
    ligarMenusDeAcao();
    if (typeof PainelDemo !== "undefined") PainelDemo.iniciar();
  }

  /* ---------------- PDF da picking list (gerado aqui mesmo, sem biblioteca) ---------------- */
  function pdfTexto(s) {
    let out = "";
    String(s).split("").forEach(function (ch) {
      const c = ch.charCodeAt(0);
      if (ch === "\\" || ch === "(" || ch === ")") out += "\\" + ch;
      else if (c >= 32 && c < 127) out += ch;
      else if (c >= 160 && c <= 255) out += "\\" + c.toString(8).padStart(3, "0");
      else if (ch === "—" || ch === "–") out += "\\227";
      else if (ch === "•") out += "\\225";
      else out += "?";
    });
    return out;
  }

  function gerarPdfPicking(pedido) {
    const cmds = [];
    function cor(hex) { const n = parseInt(hex.slice(1), 16); return [(n >> 16) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255].map(function (v) { return v.toFixed(3); }).join(" "); }
    function ret(x, y, w, h, c) { cmds.push(cor(c) + " rg " + x + " " + y + " " + w + " " + h + " re f"); }
    function txt(x, y, tam, negrito, s, c) { cmds.push("BT /" + (negrito ? "F2" : "F1") + " " + tam + " Tf " + cor(c || "#0b1b2b") + " rg " + x + " " + y + " Td (" + pdfTexto(s) + ") Tj ET"); }
    function lin(x1, y1, x2, y2, c) { cmds.push(cor(c || "#d8e1ea") + " RG 0.8 w " + x1 + " " + y1 + " m " + x2 + " " + y2 + " l S"); }

    const ws = pedido.wsaida ? pedido.wsaida.numero : "";
    ret(0, 772, 595, 70, "#0d7a66");
    ret(0, 768, 595, 4, "#6d5dfc");
    txt(40, 810, 20, true, "FluxoWMS", "#ffffff");
    txt(40, 790, 10, false, "Gestão de Armazém · Ambiente de Demonstração", "#d9f5ee");
    txt(360, 808, 15, true, "PICKING LIST TOTAL", "#ffffff");
    txt(360, 790, 10, false, "WSaída nº " + ws, "#d9f5ee");

    const y0 = 735;
    const info = [
      ["Pedido", rotuloPedido(pedido.numero)], ["WSaída", String(ws)],
      ["Destinatário", pedido.destinatario || "-"], ["Separação", pedido.dataSeparacao || Estado.hojeBR()],
      ["Tipo", pedido.tipoMov || "SAÍDA PADRÃO"], ["Prioridade", String(pedido.prioridade || "0") + (pedido.critico ? " · CRÍTICO" : "")]
    ];
    info.forEach(function (par, i) {
      const x = 40 + (i % 2) * 270, y = y0 - Math.floor(i / 2) * 34;
      txt(x, y + 12, 8, true, par[0].toUpperCase(), "#5a6b7e");
      txt(x, y - 2, 12, true, par[1]);
    });

    let y = 620;
    ret(40, y - 6, 515, 24, "#eef3f8");
    txt(48, y + 2, 9, true, "ENDEREÇO"); txt(128, y + 2, 9, true, "CÓDIGO"); txt(190, y + 2, 9, true, "DESCRIÇÃO");
    txt(470, y + 2, 9, true, "QTD"); txt(515, y + 2, 9, true, "CONF.");
    y -= 26;
    const itens = (pedido.itens || []).slice().sort(function (a, b) { return DADOS_DEMO.enderecoDe(a.cod) < DADOS_DEMO.enderecoDe(b.cod) ? -1 : 1; });
    const limite = 30;
    itens.slice(0, limite).forEach(function (it, i) {
      if (i % 2 === 1) ret(40, y - 6, 515, 20, "#f8fbfe");
      txt(48, y, 10, true, DADOS_DEMO.enderecoDe(it.cod));
      txt(128, y, 10, false, it.cod);
      txt(190, y, 10, false, String(it.desc).slice(0, 52));
      txt(470, y, 10, true, qtd(it.qtd));
      cmds.push("0.35 0.42 0.49 RG 0.8 w 520 " + (y - 2) + " 10 10 re S");
      y -= 20;
    });
    if (itens.length > limite) { txt(48, y, 10, false, "(+ " + (itens.length - limite) + " itens na próxima folha)", "#5a6b7e"); y -= 20; }
    lin(40, y + 6, 555, y + 6);
    const totalQtd = itens.reduce(function (s, it) { return s + Number(it.qtd || 0); }, 0);
    txt(48, y - 12, 11, true, itens.length + " itens · " + qtd(totalQtd) + " unidades");

    lin(40, 110, 250, 110, "#5a6b7e"); txt(40, 96, 9, false, "Separador", "#5a6b7e");
    lin(320, 110, 555, 110, "#5a6b7e"); txt(320, 96, 9, false, "Conferente", "#5a6b7e");
    ret(0, 0, 595, 40, "#eef3f8");
    txt(40, 16, 9, true, "Ambiente de demonstração · dados fictícios", "#5a6b7e");
    txt(420, 16, 9, false, "Emitido em " + new Date().toLocaleString("pt-BR"), "#5a6b7e");

    const conteudo = cmds.join("\n");
    const objs = [
      null,
      "<< /Type /Catalog /Pages 2 0 R >>",
      "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
      "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>",
      "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
      "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
      "<< /Length " + conteudo.length + " >>\nstream\n" + conteudo + "\nendstream"
    ];
    let pdf = "%PDF-1.4\n";
    const pos = [];
    for (let i = 1; i < objs.length; i++) { pos[i] = pdf.length; pdf += i + " 0 obj\n" + objs[i] + "\nendobj\n"; }
    const xref = pdf.length;
    pdf += "xref\n0 " + objs.length + "\n0000000000 65535 f \n";
    for (let i = 1; i < objs.length; i++) pdf += String(pos[i]).padStart(10, "0") + " 00000 n \n";
    pdf += "trailer\n<< /Size " + objs.length + " /Root 1 0 R >>\nstartxref\n" + xref + "\n%%EOF";
    return pdf;
  }

  function baixarArquivo(nome, conteudo, tipo) {
    const blob = new Blob([conteudo], { type: tipo || "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = nome; a.style.display = "none";
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 4000);
  }

  return {
    $: $, $$: $$, esc: esc, atraso: atraso, parametro: parametro, rotuloPedido: rotuloPedido, qtd: qtd, hora: hora,
    codigoAleatorio: codigoAleatorio, logo: logo, lerLocal: lerLocal, gravarLocal: gravarLocal,
    STATUS_PEDIDO: STATUS_PEDIDO, STATUS_REAB: STATUS_REAB, etiqueta: etiqueta,
    criarSobreposicoes: criarSobreposicoes, carregando: carregando, processar: processar, navegar: navegar,
    toast: toast, selo: selo, abrirDialogo: abrirDialogo, fecharDialogo: fecharDialogo, tremer: tremer,
    fecharMenusDeAcao: fecharMenusDeAcao, abrirMenu: abrirMenu, fecharMenu: fecharMenu,
    iniciar: iniciar, gerarPdfPicking: gerarPdfPicking, baixarArquivo: baixarArquivo
  };
})();
