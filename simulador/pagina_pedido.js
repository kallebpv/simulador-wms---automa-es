/* =====================================================================
   FluxoWMS · pagina_pedido.js  (Pedido Normal: novo ou edição)
   - pedido.html?novo=normal  → número reservado na abertura (o robô lê
     o "Pedido Normal # N" do título logo depois de importar).
   - pedido.html?numero=N     → edição de um pedido em digitação.
   A importação dos produtos é o que cria o pedido (como no original).
   ===================================================================== */

(function () {
  const $ = App.$, $$ = App.$$;
  App.iniciar({ atual: "pedidos", trilha: "WMS › Saida › Pedidos › <b>Pedido Normal</b>" });

  const CHAVE_RASCUNHO = "fluxowms.rascunhoPedido";
  const numeroEdicao = App.parametro("numero");
  let pedido = null;          // existe no estado (criado ou em edição)
  let numero = null;
  let itensTela = [];
  let acaoConfirmar = null;

  /* ---------- combos ---------- */
  function preencherSelect(sel, opcoes, placeholder) {
    sel.innerHTML = (placeholder ? '<option value="">' + placeholder + "</option>" : "") +
      opcoes.map(function (o) { return "<option>" + App.esc(o) + "</option>"; }).join("");
  }
  preencherSelect($("#id_tipo_movimento"), DADOS_DEMO.tiposMovimento, "Selecione…");
  preencherSelect($("#cod_wcliproj"), DADOS_DEMO.projetos, "Selecione…");

  /* ---------- título ---------- */
  function desenharTitulo() {
    const st = pedido ? App.etiqueta(App.STATUS_PEDIDO, pedido.status) : '<span class="st st-cinza">Novo</span>';
    $("#tituloPedido").innerHTML = 'Pedido Normal # <span class="num" id="badgePedido">' + numero + "</span> " + st;
    $("#subtituloPedido").textContent = pedido
      ? App.rotuloPedido(numero) + " · " + (pedido.destinatario || "") + " · " + pedido.itens.length + " itens"
      : "Preencha os dados e importe os produtos.";
    $("#dicaModo").textContent = numeroEdicao ? "Editando pedido existente" : "Novo pedido de saída";
  }

  /* ---------- itens ---------- */
  function desenharItens(animar) {
    const area = $("#areaItens");
    $("#contagemItens").textContent = itensTela.length ? "· " + itensTela.length + " itens" : "";
    if (!itensTela.length) {
      area.innerHTML = '<div class="itens-vazio"><b>Nenhum produto ainda</b>Clique em “Importar produtos (CSV)” e cole código + quantidade.</div>';
      return;
    }
    const total = itensTela.reduce(function (s, it) { return s + Number(it.qtd || 0); }, 0);
    area.innerHTML = '<table class="tabela"><thead><tr><th>#</th><th>Código</th><th>Descrição</th><th class="dir">Quantidade</th><th>Endereço</th></tr></thead><tbody>' +
      itensTela.map(function (it, i) {
        return '<tr class="' + (animar ? "entra" : "") + '" style="animation-delay:' + (i * 45) + 'ms"><td>' + (i + 1) + '</td><td class="n">' + App.esc(it.cod) + "</td><td>" + App.esc(it.desc) +
          '</td><td class="dir n">' + App.qtd(it.qtd) + "</td><td>" + DADOS_DEMO.enderecoDe(it.cod) + "</td></tr>";
      }).join("") + '</tbody></table><div class="totais-itens"><span>Itens: <b>' + itensTela.length + "</b></span><span>Unidades: <b>" + App.qtd(total) + "</b></span></div>";
  }

  /* ---------- carregar pedido ---------- */
  function preencherFormulario(p) {
    $("#id_tipo_movimento").value = p.tipoMov || "";
    $("#cod_wcliproj").value = p.projeto || "";
    $("#destinatarioNome").value = p.destinatario || "";
    const d = DADOS_DEMO.destinatarios.find(function (x) { return x.nome === p.destinatario; });
    $("#destinatarioCodigo").value = d ? d.codigo + " · " + d.cidade : "";
    $("#nprioridade_ped").value = String(p.prioridade || "3");
    $("#dtseparacao_ped").value = p.dataSeparacao || "";
    definirCritico(!!p.critico);
    $("#stexto_urgente_ped").value = p.motivoCritico || "";
    $("#mobs_ped").value = p.obs || "";
    itensTela = (p.itens || []).slice();
  }

  if (numeroEdicao) {
    pedido = Estado.pedido(numeroEdicao);
    if (!pedido) {
      App.toast("Pedido " + App.esc(numeroEdicao) + " não encontrado.", "erro");
      numero = numeroEdicao;
    } else {
      numero = pedido.numero;
      preencherFormulario(pedido);
    }
  } else {
    let rascunho = null;
    try { rascunho = sessionStorage.getItem(CHAVE_RASCUNHO); } catch (e) { }
    if (rascunho && !Estado.pedido(rascunho)) numero = Number(rascunho);
    else {
      numero = Estado.reservarNumeroPedido();
      try { sessionStorage.setItem(CHAVE_RASCUNHO, String(numero)); } catch (e) { }
    }
  }
  $("#numeroPedido").value = numero;
  desenharTitulo();
  desenharItens(false);

  /* ---------- crítico ---------- */
  function definirCritico(ligado) {
    $("#bcritico_ped").classList.toggle("ligado", ligado);
    $("#bcritico_ped").textContent = ligado ? "Pedido crítico · SIM" : "Pedido crítico";
    $("#campoUrgente").hidden = !ligado;
  }
  $("#bcritico_ped").addEventListener("click", function () {
    definirCritico(!$("#bcritico_ped").classList.contains("ligado"));
  });

  /* ---------- diálogos ---------- */
  $$("[data-fechar]").forEach(function (b) { b.addEventListener("click", function () { App.fecharDialogo(b.closest(".ui-dialog")); }); });
  function confirmar(titulo, msg, acao) {
    $("#tituloConfirmar").textContent = titulo;
    $("#msgConfirmar").innerHTML = msg;
    acaoConfirmar = acao;
    App.abrirDialogo($("#dlgConfirmar"));
  }
  $("#okConfirmar").addEventListener("click", function () {
    const a = acaoConfirmar; acaoConfirmar = null;
    App.fecharDialogo($("#dlgConfirmar"));
    if (a) a();
  });

  /* ---------- destinatário (div[6]) ---------- */
  function destinatarioTravado() { return !!(pedido && pedido.itens && pedido.itens.length); }
  $("#btnLupa").addEventListener("click", function () {
    if (destinatarioTravado()) { App.toast("Produtos já importados: o destinatário não pode mais ser alterado.", "aviso"); return; }
    $("#resultadosDest").innerHTML = "";
    App.abrirDialogo($("#dlgDestinatario"));
  });
  function buscarDestinatario() {
    const termo = $("#ncod_snome").value.trim().toLowerCase();
    $("#resultadosDest").innerHTML = '<tr class="resumo"><td colspan="4">Pesquisando…</td></tr>';
    App.processar("Pesquisando destinatários…", function () {
      const achados = DADOS_DEMO.destinatarios.filter(function (d) { return !termo || d.nome.toLowerCase().indexOf(termo) >= 0; });
      $("#resultadosDest").innerHTML = achados.length ? achados.map(function (d) {
        return '<tr class="linha"><td class="n">' + d.codigo + "</td><td><b>" + App.esc(d.nome) + "</b></td><td>" + App.esc(d.cidade) +
          '</td><td><button type="button" class="btn btn-pri" data-dest="' + d.codigo + '">Selecionar</button></td></tr>';
      }).join("") : '<tr class="vazio"><td colspan="4">Nenhum destinatário encontrado.</td></tr>';
    }, 350, 800);
  }
  $("#btnBuscarDest").addEventListener("click", buscarDestinatario);
  $("#formBuscaDest").addEventListener("submit", function (ev) { ev.preventDefault(); buscarDestinatario(); });
  $("#resultadosDest").addEventListener("click", function (ev) {
    const b = ev.target.closest("button[data-dest]");
    if (!b) return;
    const d = DADOS_DEMO.destinatarios.find(function (x) { return x.codigo === b.dataset.dest; });
    $("#destinatarioNome").value = d.nome;
    $("#destinatarioCodigo").value = d.codigo + " · " + d.cidade;
    App.fecharDialogo($("#dlgDestinatario"));
    App.toast("Destinatário <b>" + App.esc(d.nome) + "</b> selecionado.", "ok", 2000);
  });

  /* ---------- dados do formulário ---------- */
  function lerFormulario() {
    return {
      tipoMov: $("#id_tipo_movimento").value,
      projeto: $("#cod_wcliproj").value,
      destinatario: $("#destinatarioNome").value,
      prioridade: $("#nprioridade_ped").value,
      dataSeparacao: $("#dtseparacao_ped").value.trim(),
      critico: $("#bcritico_ped").classList.contains("ligado"),
      motivoCritico: $("#stexto_urgente_ped").value.trim(),
      obs: $("#mobs_ped").value
    };
  }

  /* ---------- importar produtos (div[16] → div[24]) ---------- */
  $("#importarProdutosCSV").addEventListener("click", function () {
    confirmar("Importar produtos", "Depois de importar os produtos, <b>o destinatário não poderá mais ser modificado</b>. Deseja continuar?", function () {
      App.carregando(true, "Abrindo importação…");
      setTimeout(function () {
        App.carregando(false);
        // Não limpar o textarea aqui: o robô pode ter colado o conteúdo antes do diálogo aparecer.
        App.abrirDialogo($("#dlgImportar"));
      }, App.atraso(300, 600));
    });
  });
  setInterval(function () {
    const n = Estado.interpretarColagem($("#produtos").value).length;
    $("#previaImport").textContent = n ? n + " linha(s) reconhecida(s)." : "";
  }, 400);

  $("#okImportar").addEventListener("click", function () {
    const novos = Estado.interpretarColagem($("#produtos").value);
    const f = lerFormulario();
    if (!novos.length) { App.tremer($("#dlgImportar")); App.toast("Nenhuma linha válida (código + quantidade).", "erro"); return; }
    if (!f.destinatario) { App.fecharDialogo($("#dlgImportar")); App.toast("Selecione o destinatário antes de importar.", "erro"); return; }
    App.fecharDialogo($("#dlgImportar"));
    App.processar("Importando " + novos.length + " produtos…", function () {
      $("#produtos").value = "";
      const criando = !pedido;
      if (criando) {
        pedido = Object.assign({ numero: numero, tipo: "Normal", itens: [], status: "DIGITACAO", criadoEm: Date.now() }, f);
        try { sessionStorage.removeItem(CHAVE_RASCUNHO); } catch (e) { }
      } else {
        Object.assign(pedido, f);
      }
      pedido.itens = pedido.itens.concat(novos);
      itensTela = pedido.itens.slice();
      Estado.contar("itens", novos.length);
      if (criando) {
        Estado.contar("pedidos");
        Estado.registrar("Pedido " + App.rotuloPedido(numero) + " criado · " + novos.length + " itens", "ok");
      } else {
        Estado.registrar(novos.length + " itens adicionados ao " + App.rotuloPedido(numero), "info");
      }
      Estado.salvarPedido(pedido);
      desenharTitulo();
      desenharItens(true);
      $("#infoSalvo").textContent = "Salvo às " + new Date().toLocaleTimeString("pt-BR");
      if (criando) App.selo("Pedido " + App.rotuloPedido(numero) + " criado", novos.length + " itens importados");
      else App.toast(novos.length + " itens importados.", "ok");
    }, 600, 1200);
  });

  /* ---------- salvar ---------- */
  $("#btnSalvar").addEventListener("click", function () {
    if (!pedido) { App.toast("Importe os produtos para criar o pedido.", "aviso"); return; }
    const f = lerFormulario();
    if (f.dataSeparacao && !/^\d{2}\/\d{2}\/\d{4}$/.test(f.dataSeparacao)) { App.toast("Data de separação inválida (DD/MM/AAAA).", "erro"); return; }
    App.processar("Salvando pedido…", function () {
      Object.assign(pedido, f);
      Estado.salvarPedido(pedido);
      Estado.registrar(App.rotuloPedido(pedido.numero) + " salvo · prioridade " + f.prioridade + (f.critico ? " · crítico" : ""), "ok");
      desenharTitulo();
      $("#infoSalvo").textContent = "Salvo às " + new Date().toLocaleTimeString("pt-BR");
      App.toast("Pedido <b>" + App.rotuloPedido(pedido.numero) + "</b> salvo com sucesso.", "ok");
    }, 500, 1000);
  });

  $("#btnCancelar").addEventListener("click", function () { if (pedido) preencherFormulario(pedido); desenharItens(false); App.toast("Alterações descartadas.", "info", 1800); });
  $("#btnImprimir").addEventListener("click", function () { App.toast("Espelho do pedido fora do roteiro da demonstração.", "aviso", 2200); });
  $("#formPedido").addEventListener("submit", function (ev) { ev.preventDefault(); });

  $("#btnVoltar").addEventListener("click", function (ev) {
    ev.preventDefault();
    App.navegar("pedidos.html", "Voltando para os pedidos…");
  });
})();
