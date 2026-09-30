/* =====================================================================
   FluxoWMS · pagina_reabastecimento.js  (WMS › Armazém › Pedidos de reabastecimento)
   Fluxo: Rascunho → (solicitar) Aguardando → (aprovar) Aprovado →
          (submeter integração) Integrado + gera um pedido de saída
          "Aprovado" com a observação "PEDIDO: <nº do reabastecimento>".
   ===================================================================== */

(function () {
  const $ = App.$, $$ = App.$$;
  App.iniciar({ atual: "reabastecimento", trilha: "WMS › Saida › Armazém › <b>Pedidos de reabastecimento</b>" });

  const corpo = $("#corpoReab");
  let filtro = {};
  let pendente = null;          // { acao, reab, codigo }

  /* ---------- busca: o botão "Pesquisa" só abre ---------- */
  $("#lnkPesquisa").addEventListener("click", function (ev) {
    ev.preventDefault();
    $("#corpoBusca").hidden = false;
    $("#painelBusca").classList.add("aberto");
  });

  function dataNum(br) {
    const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(br || "");
    return m ? Number(m[3] + m[2] + m[1]) : null;
  }
  function passa(r, f) {
    if (f.numero && String(r.numero) !== f.numero.replace(/\D/g, "")) return false;
    if (f.status && r.status !== f.status) return false;
    const d = dataNum(r.dataCriacao);
    if (f.de && dataNum(f.de) && d && d < dataNum(f.de)) return false;
    if (f.ate && dataNum(f.ate) && d && d > dataNum(f.ate)) return false;
    return true;
  }

  function itensMenu(r) {
    let acao4, acao5;
    if (r.status === "RASCUNHO") acao4 = ["solicitar", "Solicitar aprovação", "destaque"];
    else if (r.status === "AGUARDANDO") acao4 = ["aprovar", "Aprovar pedido", "destaque"];
    else acao4 = ["x-aprovado", "Pedido aprovado ✓", "inativo"];
    if (r.status === "APROVADO") acao5 = ["submeter", "Submeter integração", "destaque"];
    else if (r.status === "INTEGRADO") acao5 = ["x-integrado", "Integração enviada ✓", "inativo"];
    else acao5 = ["x-submeter", "Submeter integração", "inativo"];
    return [["x-ver", "Visualizar"], ["x-editar", "Editar"], ["x-historico", "Histórico"], acao4, acao5, ["x-cancelar", "Cancelar pedido"]]
      .map(function (it) { return '<li><a data-acao="' + it[0] + '" data-numero="' + r.numero + '"' + (it[2] ? ' class="' + it[2] + '"' : "") + ">" + it[1] + "</a></li>"; }).join("");
  }

  function desenhar(destacar) {
    $$("tr.linha, tr.esqueleto, tr.vazio", corpo).forEach(function (tr) { tr.remove(); });
    const lista = Estado.reabs().slice().sort(function (a, b) { return b.numero - a.numero; }).filter(function (r) { return passa(r, filtro); });
    $("#resumoReab").innerHTML = "<b>" + lista.length + "</b> pedido(s) de reabastecimento" + (filtro.numero ? " · nº <b>" + App.esc(filtro.numero) + "</b>" : "") + (filtro.de ? " · desde <b>" + App.esc(filtro.de) + "</b>" : "");
    if (!lista.length) corpo.insertAdjacentHTML("beforeend", '<tr class="vazio"><td colspan="11">Nenhum pedido encontrado.</td></tr>');
    corpo.insertAdjacentHTML("beforeend", lista.slice(0, 40).map(function (r) {
      const total = r.itens.reduce(function (s, it) { return s + Number(it.qtd || 0); }, 0);
      return '<tr class="linha' + (String(r.numero) === String(destacar) ? " novo" : "") + '">' +
        '<td class="n">' + r.numero + "</td><td>" + App.esc(r.dataCriacao) + "</td><td>" + App.esc(r.origem) + "</td><td>" + App.esc(r.destino) + "</td>" +
        "<td>" + App.esc(r.projDestino) + '</td><td class="dir">' + r.itens.length + '</td><td class="dir">' + App.qtd(total) + "</td>" +
        "<td>" + App.etiqueta(App.STATUS_REAB, r.status) + "</td>" +
        "<td>" + (r.pedidoGerado ? '<span class="n">' + r.pedidoGerado + "</span>" : '<span class="dica">—</span>') + "</td>" +
        '<td class="obs">' + App.esc(r.categoria || "") + "</td>" +
        '<td><div class="acoes"><span title="Ações">•••</span><ul>' + itensMenu(r) + "</ul></div></td></tr>";
    }).join(""));
    const hoje = Estado.reabs().filter(function (r) { return r.dataCriacao === Estado.hojeBR(); }).length;
    $("#dicaTopo").textContent = Estado.reabs().length + " pedidos cadastrados · " + hoje + " criados hoje";
  }

  function mostrarAtualizando() {
    App.fecharMenusDeAcao();
    $$("tr.linha, tr.vazio", corpo).forEach(function (tr) { tr.remove(); });
    for (let i = 0; i < 3; i++) corpo.insertAdjacentHTML("beforeend", '<tr class="esqueleto"><td colspan="11"></td></tr>');
  }

  function pesquisar() {
    filtro = { numero: $("#busca_numero").value.trim(), status: $("#busca_status").value, de: $("#busca_data_de").value.trim(), ate: $("#busca_data_ate").value.trim() };
    mostrarAtualizando();
    App.processar("Pesquisando…", function () { desenhar(); }, 350, 900);
  }
  $("#btnPesquisar").addEventListener("click", pesquisar);
  $("#formBusca").addEventListener("submit", function (ev) { ev.preventDefault(); pesquisar(); });
  $("#btnLimparBusca").addEventListener("click", function () { $("#formBusca").reset(); pesquisar(); });

  $("#btnNovo").addEventListener("click", function (ev) { ev.preventDefault(); App.navegar("reabastecimento_novo.html", "Abrindo novo reabastecimento…"); });
  $("#btnExportar").addEventListener("click", function (ev) { ev.preventDefault(); App.toast("Exportação fora do roteiro da demonstração.", "aviso", 2200); });

  /* ---------- ações com código de segurança (div[16]) ---------- */
  const TEXTOS = {
    solicitar: ["Solicitar aprovação", "Enviar o reabastecimento <b>{p}</b> para aprovação."],
    aprovar: ["Aprovar pedido", "Aprovar o reabastecimento <b>{p}</b>."],
    submeter: ["Submeter integração", "Integrar o reabastecimento <b>{p}</b> com a saída. Um pedido de saída será gerado."]
  };
  corpo.addEventListener("click", function (ev) {
    const a = ev.target.closest("a[data-acao]");
    if (!a) return;
    ev.preventDefault();
    App.fecharMenusDeAcao();
    const r = Estado.reab(a.dataset.numero);
    if (!r) return;
    const acao = a.dataset.acao;
    if (!TEXTOS[acao]) { App.toast(a.classList.contains("inativo") ? "Ação indisponível para o status atual." : "Opção fora do roteiro da demonstração.", "aviso", 2200); return; }
    pendente = { acao: acao, reab: r, codigo: App.codigoAleatorio() };
    $("#tituloCodigo").textContent = TEXTOS[acao][0];
    $("#msgCodigo").innerHTML = TEXTOS[acao][1].replace("{p}", App.rotuloPedido(r.numero)) + "<br>Digite o código abaixo para confirmar:";
    $("#lbl_random").textContent = pendente.codigo;
    $("#txtCodigo").value = "";
    App.abrirDialogo($("#dlgCodigo"));
  });
  $$("[data-fechar]").forEach(function (b) { b.addEventListener("click", function () { pendente = null; App.fecharDialogo(b.closest(".ui-dialog")); }); });

  $("#okCodigo").addEventListener("click", function () {
    if (!pendente) return;
    if ($("#txtCodigo").value.trim() !== pendente.codigo) {
      App.tremer($("#dlgCodigo")); App.toast("Código de confirmação incorreto.", "erro"); return;
    }
    const p = pendente; pendente = null;
    App.fecharDialogo($("#dlgCodigo"));
    mostrarAtualizando();
    const r = p.reab, rot = App.rotuloPedido(r.numero);
    App.processar(TEXTOS[p.acao][0] + "…", function () {
      if (p.acao === "solicitar") {
        r.status = "AGUARDANDO";
        Estado.registrar("Aprovação solicitada · " + rot, "info");
        App.toast("Aprovação do <b>" + rot + "</b> solicitada.", "ok");
      } else if (p.acao === "aprovar") {
        r.status = "APROVADO";
        Estado.contar("aprovacoes");
        Estado.registrar(rot + " aprovado", "ok");
        App.toast("Reabastecimento <b>" + rot + "</b> aprovado.", "ok");
      } else if (p.acao === "submeter") {
        r.status = "INTEGRADO";
        const n = Estado.reservarNumeroPedido();
        r.pedidoGerado = n;
        Estado.salvarPedido({
          numero: n, tipo: "Normal", tipoMov: "SAÍDA PADRÃO", projeto: r.projDestino, destinatario: r.destino,
          prioridade: "3", dataSeparacao: Estado.hojeBR(), critico: false, motivoCritico: "",
          obs: "PEDIDO: " + r.numero + " · gerado pela integração do reabastecimento",
          itens: Estado.copia(r.itens), status: "APROVADO", criadoEm: Date.now(), origemReab: r.numero
        });
        Estado.registrar("Integração enviada · " + rot + " gerou " + App.rotuloPedido(n), "roxo");
        App.selo("Integração enviada", rot + " gerou o pedido de saída " + App.rotuloPedido(n));
      }
      Estado.salvarReab(r);
      desenhar(r.numero);
    });
  });

  desenhar();
})();
