/* =====================================================================
   FluxoWMS · painel_demo.js
   Painel de demonstração (canto inferior direito, recolhível) e a
   "pílula" no topo central com contador + cronômetro — ela fica dentro
   de um corte vertical 9:16 do vídeo.

   Atalhos de teclado (fora de campos de texto):
     P  mostra/esconde o painel inteiro   ·   H  mostra/esconde a pílula
   ===================================================================== */

const PainelDemo = (function () {
  let painel, hud, ultimoTopoLog = null, ultimoContador = null, armadoReset = false;

  function fmtTempo(ms) {
    if (ms == null || ms < 0) return "00:00";
    const s = Math.floor(ms / 1000);
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), ss = s % 60;
    const mm = String(m).padStart(2, "0") + ":" + String(ss).padStart(2, "0");
    return h ? h + ":" + mm : mm;
  }

  /* Cronômetro: corre desde o 1º pedido; congela 60 s depois da última atividade. */
  function tempoDecorrido(sessao) {
    if (!sessao.primeiroPedidoEm) return null;
    const ultimaAtividade = sessao.log.length ? sessao.log[0].t : sessao.primeiroPedidoEm;
    const ocioso = Date.now() - ultimaAtividade > 60000;
    return (ocioso ? ultimaAtividade : Date.now()) - sessao.primeiroPedidoEm;
  }

  /* Número em destaque: pedidos criados; se o robô só avança pedidos (WSaídas), mostra os avançados. */
  function principal(s) {
    if (!s.pedidos && s.wsaidas) return { n: s.wsaidas, rotulo: "pedidos avançados", curto: "avançados" };
    return { n: s.pedidos, rotulo: "pedidos criados", curto: "pedidos" };
  }

  function montar() {
    painel = document.createElement("aside");
    painel.id = "painelDemo";
    painel.innerHTML =
      '<section class="pd-caixa">' +
      '<header class="pd-cab"><span class="ao-vivo">AO VIVO</span><strong>Painel da demonstração</strong><span class="espaco"></span>' +
      '<button type="button" class="pd-recolher" title="Recolher / expandir">–</button></header>' +
      '<section class="pd-corpo">' +
      '<div class="pd-grande"><span class="num" data-v="pedidos">0</span><span class="rot"><span data-v="rotulo">pedidos criados</span><br><small class="dica">nesta execução</small></span></div>' +
      '<div class="pd-tempo"><div><small>Cronômetro</small><b data-v="tempo">00:00</b></div><div><small>Média / pedido</small><b data-v="media">—</b></div></div>' +
      '<div class="pd-mini">' +
      '<div><b data-v="itens">0</b><small>itens</small></div>' +
      '<div><b data-v="aprovacoes">0</b><small>aprov.</small></div>' +
      '<div><b data-v="wsaidas">0</b><small>WSaídas</small></div>' +
      '<div><b data-v="pickings">0</b><small>pickings</small></div>' +
      "</div>" +
      '<ul class="pd-log"></ul>' +
      "</section>" +
      '<footer class="pd-rodape"><button type="button" class="pd-reset">Reiniciar demonstração</button></footer>' +
      "</section>";
    document.body.appendChild(painel);

    hud = document.createElement("aside");
    hud.id = "hudDemo";
    hud.innerHTML = '<span class="ponto"></span><span><b data-h="pedidos">0</b> <span data-h="rotulo">pedidos</span></span><span class="sep">|</span><span data-h="tempo">00:00</span><span class="sep">|</span><span data-h="ultimo">—</span>';
    document.body.appendChild(hud);

    if (App.lerLocal("fluxowms.painelRecolhido", false)) painel.classList.add("recolhido");
    if (App.lerLocal("fluxowms.painelOculto", false)) painel.hidden = true;
    if (App.lerLocal("fluxowms.hudOculto", false)) hud.hidden = true;

    painel.querySelector(".pd-recolher").addEventListener("click", function () {
      painel.classList.toggle("recolhido");
      App.gravarLocal("fluxowms.painelRecolhido", painel.classList.contains("recolhido"));
    });

    const btnReset = painel.querySelector(".pd-reset");
    btnReset.addEventListener("click", function () {
      if (!armadoReset) {
        armadoReset = true;
        btnReset.classList.add("confirmar");
        btnReset.textContent = "Clique de novo para zerar tudo";
        setTimeout(function () { armadoReset = false; btnReset.classList.remove("confirmar"); btnReset.textContent = "Reiniciar demonstração"; }, 3500);
        return;
      }
      Estado.reiniciar();
      location.reload();
    });

    document.addEventListener("keydown", function (ev) {
      const alvo = ev.target;
      if (alvo && (alvo.tagName === "INPUT" || alvo.tagName === "TEXTAREA" || alvo.tagName === "SELECT" || alvo.isContentEditable)) return;
      if (ev.ctrlKey || ev.altKey || ev.metaKey) return;
      const k = ev.key.toLowerCase();
      if (k === "p") { painel.hidden = !painel.hidden; App.gravarLocal("fluxowms.painelOculto", painel.hidden); }
      if (k === "h") { hud.hidden = !hud.hidden; App.gravarLocal("fluxowms.hudOculto", hud.hidden); }
    });
  }

  function atualizar() {
    if (!painel) return;
    const d = Estado.dados, s = d.sessao;
    const tempo = tempoDecorrido(s);
    const valores = {
      pedidos: principal(s).n, rotulo: principal(s).rotulo, itens: s.itens.toLocaleString("pt-BR"), aprovacoes: s.aprovacoes, wsaidas: s.wsaidas, pickings: s.pickings,
      tempo: fmtTempo(tempo), media: principal(s).n && tempo ? Math.round(tempo / 1000 / principal(s).n) + " s" : "—"
    };
    Object.keys(valores).forEach(function (k) {
      const el = painel.querySelector('[data-v="' + k + '"]');
      if (el && el.textContent !== String(valores[k])) el.textContent = valores[k];
    });

    const ul = painel.querySelector(".pd-log");
    const topo = s.log.length ? s.log[0].t + s.log[0].texto : null;
    if (topo !== ultimoTopoLog) {
      const novo = ultimoTopoLog !== null;
      ultimoTopoLog = topo;
      if (!s.log.length) {
        ul.innerHTML = '<li class="vazio">Aguardando o robô…</li>';
      } else {
        ul.innerHTML = s.log.slice(0, 6).map(function (l, i) {
          return '<li class="' + l.tipo + (i === 0 && novo ? " novo" : "") + '"><i></i><span>' + App.esc(l.texto) + "</span><time>" + App.hora(l.t) + "</time></li>";
        }).join("");
      }
    }

    // pílula central
    hud.querySelector('[data-h="pedidos"]').textContent = principal(s).n;
    hud.querySelector('[data-h="rotulo"]').textContent = principal(s).curto;
    hud.querySelector('[data-h="tempo"]').textContent = fmtTempo(tempo);
    hud.querySelector('[data-h="ultimo"]').textContent = s.log.length ? s.log[0].texto : "aguardando";
    hud.classList.toggle("visivel", s.log.length > 0);
    if (ultimoContador !== null && principal(s).n > ultimoContador) {
      hud.classList.remove("pulou"); void hud.offsetWidth; hud.classList.add("pulou");
    }
    ultimoContador = principal(s).n;
  }

  function iniciar() {
    if (painel) return;
    montar();
    atualizar();
    document.addEventListener("estado-mudou", atualizar);
    setInterval(atualizar, 1000);
  }

  return { iniciar: iniciar, atualizar: atualizar };
})();
