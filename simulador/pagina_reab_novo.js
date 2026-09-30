/* =====================================================================
   FluxoWMS · pagina_reab_novo.js  (novo pedido de reabastecimento)
   O número é reservado na abertura; a importação dos itens cria o pedido.
   ===================================================================== */

(function () {
  const $ = App.$, $$ = App.$$;
  App.iniciar({ atual: "reabastecimento", trilha: "WMS › Armazém › Reabastecimento › <b>Novo</b>" });

  const CHAVE = "fluxowms.rascunhoReab";
  let numero = null, reab = null;

  let rascunho = null;
  try { rascunho = sessionStorage.getItem(CHAVE); } catch (e) { }
  if (rascunho && !Estado.reab(rascunho)) numero = Number(rascunho);
  else { numero = Estado.reservarNumeroPedido(); try { sessionStorage.setItem(CHAVE, String(numero)); } catch (e) { } }
  $("#numeroReab").value = numero;

  function opcoes(sel, lista) {
    sel.innerHTML = '<option value="">Selecione…</option>' + lista.map(function (o) { return "<option>" + App.esc(o) + "</option>"; }).join("");
  }
  opcoes($("#reab_origem"), DADOS_DEMO.unidades);
  opcoes($("#reab_destino"), DADOS_DEMO.unidades);
  opcoes($("#reab_proj_origem"), DADOS_DEMO.projetos);
  opcoes($("#reab_proj_destino"), DADOS_DEMO.projetos);

  function titulo() {
    $("#tituloReab").innerHTML = 'Reabastecimento · Pedido # <span class="num">' + numero + "</span> " +
      (reab ? App.etiqueta(App.STATUS_REAB, reab.status) : '<span class="st st-cinza">Novo</span>');
    if (reab) $("#subtituloReab").textContent = reab.origem + " → " + reab.destino + " · " + reab.itens.length + " itens";
  }
  function desenharItens(animar) {
    const itens = reab ? reab.itens : [];
    $("#contagemItens").textContent = itens.length ? "· " + itens.length + " itens" : "";
    if (!itens.length) {
      $("#areaItens").innerHTML = '<div class="itens-vazio"><b>Nenhum item importado</b>Use “Importar CSV” e cole código + quantidade.</div>';
      return;
    }
    const total = itens.reduce(function (s, it) { return s + Number(it.qtd || 0); }, 0);
    $("#areaItens").innerHTML = '<table class="tabela"><thead><tr><th>#</th><th>Código</th><th>Descrição</th><th class="dir">Quantidade</th></tr></thead><tbody>' +
      itens.map(function (it, i) {
        return '<tr class="' + (animar ? "entra" : "") + '" style="animation-delay:' + (i * 45) + 'ms"><td>' + (i + 1) + '</td><td class="n">' + App.esc(it.cod) + "</td><td>" + App.esc(it.desc) + '</td><td class="dir n">' + App.qtd(it.qtd) + "</td></tr>";
      }).join("") + '</tbody></table><div class="totais-itens"><span>Itens: <b>' + itens.length + "</b></span><span>Unidades: <b>" + App.qtd(total) + "</b></span></div>";
  }
  titulo();
  desenharItens(false);

  $$("[data-fechar]").forEach(function (b) { b.addEventListener("click", function () { App.fecharDialogo(b.closest(".ui-dialog")); }); });

  $("#btnImportarCSV").addEventListener("click", function () { App.abrirDialogo($("#dlgConfirmar")); });
  $("#okConfirmar").addEventListener("click", function () {
    App.fecharDialogo($("#dlgConfirmar"));
    App.carregando(true, "Abrindo importação…");
    setTimeout(function () {
      App.carregando(false);
      // Não limpar o textarea: o robô pode colar antes de o diálogo aparecer.
      App.abrirDialogo($("#dlgImportar"));
    }, App.atraso(300, 600));
  });
  setInterval(function () {
    const n = Estado.interpretarColagem($("#itensReab").value).length;
    $("#previaImport").textContent = n ? n + " linha(s) reconhecida(s)." : "";
  }, 400);

  $("#okImportar").addEventListener("click", function () {
    const novos = Estado.interpretarColagem($("#itensReab").value);
    const campos = { origem: $("#reab_origem").value, destino: $("#reab_destino").value, projOrigem: $("#reab_proj_origem").value, projDestino: $("#reab_proj_destino").value };
    if (!novos.length) { App.tremer($("#dlgImportar")); App.toast("Nenhuma linha válida (código + quantidade).", "erro"); return; }
    if (!campos.origem || !campos.destino || !campos.projOrigem || !campos.projDestino) {
      App.fecharDialogo($("#dlgImportar")); App.toast("Preencha unidades e projetos antes de importar.", "erro"); return;
    }
    App.fecharDialogo($("#dlgImportar"));
    App.processar("Importando " + novos.length + " itens…", function () {
      $("#itensReab").value = "";
      const criando = !reab;
      if (criando) {
        const cats = {};
        novos.forEach(function (it) { const p = DADOS_DEMO.produtoPorCodigo[String(it.cod).toUpperCase()]; if (p) cats[p.categoria] = true; });
        reab = Object.assign({ numero: numero, itens: [], status: "RASCUNHO", dataCriacao: Estado.hojeBR(), criadoEm: Date.now(), categoria: Object.keys(cats).join(", "), obs: $("#reab_obs").value }, campos);
        try { sessionStorage.removeItem(CHAVE); } catch (e) { }
      }
      reab.itens = reab.itens.concat(novos);
      Estado.contar("itens", novos.length);
      if (criando) {
        Estado.contar("pedidos");
        Estado.registrar("Reabastecimento " + App.rotuloPedido(numero) + " criado · " + novos.length + " itens", "ok");
      }
      Estado.salvarReab(reab);
      ["#reab_origem", "#reab_destino", "#reab_proj_origem", "#reab_proj_destino"].forEach(function (s) { $(s).disabled = true; });
      titulo();
      desenharItens(true);
      App.selo("Reabastecimento " + App.rotuloPedido(numero) + " criado", novos.length + " itens importados");
    }, 600, 1200);
  });

  $("#formReab").addEventListener("submit", function (ev) { ev.preventDefault(); });
  $("#btnVoltar").addEventListener("click", function (ev) { ev.preventDefault(); App.navegar("reabastecimento.html", "Voltando…"); });
})();
