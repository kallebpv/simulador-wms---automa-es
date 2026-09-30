/* =====================================================================
   FluxoWMS · pagina_pedidos.js  (tela WMS › Saida › Pedidos)

   Regras de comportamento que mantêm os robôs funcionando:
   - Toda mudança de status esconde a linha da tabela NA HORA do clique
     e redesenha depois do "processamento" (300–1200 ms). Assim o robô,
     que espera o elemento ficar clicável, sempre enxerga o estado novo.
   - O modo "Gerenciar WSaída" é desenhado na mesma hora do OK, porque o
     robô lê o percentual e o número da WSaída sem esperar.
   - O filtro continua aplicado ao voltar da WSaída (o robô clica direto
     na linha 4 da tabela depois do "Voltar").
   ===================================================================== */

(function () {
  const $ = App.$, $$ = App.$$;
  App.iniciar({ atual: "pedidos", trilha: "WMS › Saida › <b>Pedidos</b>" });

  const corpo = $("#corpoTabela");
  let filtro = {};
  let pedidoWS = null;         // pedido aberto no modo WSaída
  let acaoConfirmar = null;    // callback do diálogo div[16]
  let pedidoDesaprovar = null;
  let pedidoRelatorio = null;
  let codigoEsperado = null;

  /* ---------- combos do filtro ---------- */
  DADOS_DEMO.projetos.forEach(function (p) {
    const o = document.createElement("option"); o.textContent = p; $("#filtro_projeto").appendChild(o);
  });

  /* ---------- painel de filtros: o link só ABRE (o × recolhe) ---------- */
  function abrirFiltro() {
    $("#corpoFiltro").hidden = false;
    $("#painelFiltro").classList.add("aberto");
    $("#btnFecharFiltro").hidden = false;
  }
  function recolherFiltro() {
    $("#corpoFiltro").hidden = true;
    $("#painelFiltro").classList.remove("aberto");
    $("#btnFecharFiltro").hidden = true;
  }
  $("#lnkPesquisar").addEventListener("click", function (ev) { ev.preventDefault(); abrirFiltro(); });
  $("#btnFecharFiltro").addEventListener("click", recolherFiltro);

  function lerFiltro() {
    return {
      numero: $("#filtro_nnumero_ped").value.trim(),
      tipo: $("#filtro_tipo").value,
      status: $("#filtro_status").value,
      destinatario: $("#filtro_destinatario").value.trim(),
      projeto: $("#filtro_projeto").value,
      dataIni: $("#filtro_data_ini").value.trim(),
      dataFim: $("#filtro_data_fim").value.trim(),
      prioridade: $("#filtro_prioridade").value,
      obs: $("#filtro_mobs_ped").value.trim()
    };
  }
  function dataNum(br) {
    const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(br || "");
    return m ? Number(m[3] + m[2] + m[1]) : null;
  }
  function passa(p, f) {
    if (f.numero && String(p.numero) !== f.numero.replace(/\D/g, "")) return false;
    if (f.tipo && p.tipo !== f.tipo) return false;
    if (f.status && p.status !== f.status) return false;
    if (f.destinatario && (p.destinatario || "").toLowerCase().indexOf(f.destinatario.toLowerCase()) < 0) return false;
    if (f.projeto && p.projeto !== f.projeto) return false;
    if (f.prioridade !== "" && f.prioridade != null && String(p.prioridade) !== f.prioridade) return false;
    if (f.obs && (p.obs || "").toLowerCase().indexOf(f.obs.toLowerCase()) < 0) return false;
    const d = dataNum(p.dataSeparacao);
    if (f.dataIni && dataNum(f.dataIni) && d && d < dataNum(f.dataIni)) return false;
    if (f.dataFim && dataNum(f.dataFim) && d && d > dataNum(f.dataFim)) return false;
    return true;
  }
  function descreverFiltro(f) {
    const partes = [];
    if (f.numero) partes.push("nº " + f.numero);
    if (f.obs) partes.push("obs. contém “" + f.obs + "”");
    if (f.status) partes.push(App.STATUS_PEDIDO[f.status][0]);
    if (f.destinatario) partes.push(f.destinatario);
    if (f.tipo) partes.push(f.tipo);
    if (f.projeto) partes.push(f.projeto);
    if (f.prioridade) partes.push("prioridade " + f.prioridade);
    return partes.join(" · ");
  }

  /* ---------- menus de ação por status (posições fixas: 8 itens) ---------- */
  function itensMenu(p) {
    const comuns = [["ver", "Visualizar pedido"], ["editar", "Editar pedido"], ["historico", "Histórico"], ["duplicar", "Duplicar pedido"], ["espelho", "Imprimir espelho"]];
    let extra;
    switch (p.status) {
      case "DIGITACAO": extra = [["solicitar", "Solicitar aprovação", "destaque"], ["cancelar", "Cancelar pedido"], ["x-criarws", "Criar WSaída", "inativo"]]; break;
      case "APROVADO": extra = [["reenviar", "Reenviar aviso de aprovação"], ["desaprovar", "Desaprovar pedido"], ["criarws", "Criar WSaída", "destaque"]]; break;
      case "WSAIDA": extra = [["separar", "Iniciar separação", "destaque"], ["x-desaprovar", "Desaprovar pedido", "inativo"], ["verws", "Ver WSaída"]]; break;
      case "SEPARACAO": extra = [["x-finalizar", "Finalizar separação", "inativo"], ["x-desaprovar", "Desaprovar pedido", "inativo"], ["verws", "Ver WSaída"]]; break;
      case "EXPEDIDO": extra = [["x-rastrear", "Rastrear entrega", "inativo"], ["x-desaprovar", "Desaprovar pedido", "inativo"], ["verws", "Ver WSaída"]]; break;
      default: extra = [["x-1", "Solicitar aprovação", "inativo"], ["x-2", "Cancelar pedido", "inativo"], ["x-3", "Criar WSaída", "inativo"]];
    }
    return comuns.concat(extra).map(function (it) {
      return '<li><a data-acao="' + it[0] + '" data-numero="' + p.numero + '"' + (it[2] ? ' class="' + it[2] + '"' : "") + ">" + it[1] + "</a></li>";
    }).join("");
  }
  function itensImpressao(p) {
    return [["x-espelho", "Espelho do pedido"], ["x-etiquetas", "Etiquetas de volume"], ["x-endereco", "Picking list por endereço"], ["picking", "Picking list total", "destaque"], ["x-romaneio", "Romaneio de entrega"]]
      .map(function (it) { return '<li><a data-acao="' + it[0] + '" data-numero="' + p.numero + '"' + (it[2] ? ' class="' + it[2] + '"' : "") + ">" + it[1] + "</a></li>"; }).join("");
  }

  /* ---------- tabela ---------- */
  function linhaHTML(p, destacar) {
    const total = p.itens.reduce(function (s, it) { return s + Number(it.qtd || 0); }, 0);
    return '<tr class="linha' + (destacar ? " novo" : "") + '" data-numero="' + p.numero + '">' +
      '<td class="n">' + p.numero + (p.critico ? '<span class="critico">CRÍTICO</span>' : "") + "</td>" +
      "<td>" + App.esc(p.tipo) + "</td>" +
      "<td>" + App.esc(p.dataSeparacao || "—") + "</td>" +
      "<td>" + App.esc(p.destinatario || "—") + "</td>" +
      '<td class="col-proj">' + App.esc(p.projeto || "—") + "</td>" +
      '<td class="dir">' + p.itens.length + "</td>" +
      '<td class="dir col-qtd">' + App.qtd(total) + "</td>" +
      "<td>" + App.esc(p.prioridade) + "</td>" +
      '<td><a class="btn" data-editar="' + p.numero + '">Editar</a></td>' +
      "<td>" + App.etiqueta(App.STATUS_PEDIDO, p.status) + (p.wsaida ? '<br><small class="dica">WS ' + p.wsaida.numero + "</small>" : "") + "</td>" +
      '<td class="obs col-obs" title="' + App.esc(p.obs) + '">' + App.esc(p.obs || "—") + "</td>" +
      '<td><div class="acoes"><span title="Ações">•••</span><ul>' + itensMenu(p) + "</ul></div></td>" +
      '<td><div class="acoes impressao"><span title="Impressão"></span><ul>' + itensImpressao(p) + "</ul></div></td>" +
      "</tr>";
  }

  function limparLinhas() { $$("tr.linha, tr.esqueleto", corpo).forEach(function (tr) { tr.remove(); }); }

  function mostrarAtualizando() {
    App.fecharMenusDeAcao();
    limparLinhas();
    $("#linhaVazia").hidden = true;
    $("#linhaAtualizando").hidden = false;
    for (let i = 0; i < 4; i++) {
      const tr = document.createElement("tr"); tr.className = "esqueleto"; tr.innerHTML = '<td colspan="13"></td>';
      corpo.appendChild(tr);
    }
  }

  function desenharTabela(destacarNumero) {
    limparLinhas();
    $("#linhaAtualizando").hidden = true;
    const todos = Estado.pedidos().slice().sort(function (a, b) { return b.numero - a.numero; });
    const lista = todos.filter(function (p) { return passa(p, filtro); });
    const desc = descreverFiltro(filtro);
    $("#resumoTabela").innerHTML = "Mostrando <b>" + Math.min(lista.length, 40) + "</b> de " + lista.length + " pedido(s)" + (desc ? " · filtro: <b>" + App.esc(desc) + "</b>" : "");
    $("#linhaVazia").hidden = lista.length > 0;
    corpo.insertAdjacentHTML("beforeend", lista.slice(0, 40).map(function (p) { return linhaHTML(p, String(p.numero) === String(destacarNumero)); }).join(""));
    $("#resumoFiltro").textContent = desc ? "Filtro ativo: " + desc : "";
    const prontos = todos.filter(function (p) { return p.status === "DIGITACAO"; }).length;
    $("#dicaTopo").textContent = todos.length + " pedidos no sistema · " + prontos + " em digitação";
  }

  function aplicarFiltro() {
    filtro = lerFiltro();
    mostrarAtualizando();
    App.processar("Filtrando pedidos…", function () { desenharTabela(); }, 350, 900);
  }
  $("#btnFiltrar").addEventListener("click", aplicarFiltro);
  $("#formFiltro").addEventListener("submit", function (ev) { ev.preventDefault(); aplicarFiltro(); });
  $("#btnLimpar").addEventListener("click", function () { $("#formFiltro").reset(); aplicarFiltro(); });

  /* ---------- "Criar pedido" ---------- */
  $("#dropdownCadastrarPedido").addEventListener("click", function (ev) {
    ev.stopPropagation();
    $("#accordion").classList.toggle("aberto");
  });
  document.addEventListener("click", function (ev) {
    if (!ev.target.closest(".criar-caixa")) $("#accordion").classList.remove("aberto");
  });
  $$("#accordion a[data-tipo]").forEach(function (a) {
    a.addEventListener("click", function (ev) {
      ev.preventDefault();
      $("#accordion").classList.remove("aberto");
      if (a.dataset.tipo === "normal") App.navegar("pedido.html?novo=normal", "Abrindo novo pedido…");
      else App.toast("Somente o pedido <b>Normal</b> faz parte do roteiro da demonstração.", "aviso");
    });
  });

  /* ---------- diálogos ---------- */
  $$("[data-fechar]").forEach(function (b) {
    b.addEventListener("click", function () { App.fecharDialogo(b.closest(".ui-dialog")); });
  });

  function confirmar(titulo, mensagem, acao) {
    $("#tituloConfirmar").textContent = titulo;
    $("#msgConfirmar").innerHTML = mensagem;
    acaoConfirmar = acao;
    App.abrirDialogo($("#dlgConfirmar"));
  }
  $("#okConfirmar").addEventListener("click", function () {
    const acao = acaoConfirmar; acaoConfirmar = null;
    App.fecharDialogo($("#dlgConfirmar"));
    if (acao) acao();
  });

  /* Mudança de status: esconde a linha já, grava e redesenha depois. */
  function mudarStatus(p, texto, fn) {
    mostrarAtualizando();
    App.processar(texto, function () {
      fn(p);
      Estado.salvarPedido(p);
      desenharTabela(p.numero);
    });
  }

  /* ---------- ações dos menus ---------- */
  document.addEventListener("click", function (ev) {
    const a = ev.target.closest("a[data-acao]");
    if (!a) return;
    ev.preventDefault();
    App.fecharMenusDeAcao();
    const p = Estado.pedido(a.dataset.numero);
    if (!p) return;
    const acao = a.dataset.acao;
    const rot = App.rotuloPedido(p.numero);

    if (acao === "solicitar") {
      confirmar("Solicitar aprovação", "Enviar o pedido <b>" + rot + "</b> para aprovação?<br><small class='dica'>Pedidos dentro da alçada são aprovados automaticamente.</small>", function () {
        mudarStatus(p, "Enviando para aprovação…", function (x) {
          x.status = "APROVADO";
          Estado.contar("aprovacoes");
          Estado.registrar(rot + " aprovado", "ok");
          App.toast("Pedido <b>" + rot + "</b> aprovado.", "ok");
        });
      });
    } else if (acao === "cancelar") {
      confirmar("Cancelar pedido", "Cancelar o pedido <b>" + rot + "</b>?", function () {
        mudarStatus(p, "Cancelando…", function (x) { x.status = "CANCELADO"; Estado.registrar(rot + " cancelado", "aviso"); });
      });
    } else if (acao === "desaprovar") {
      pedidoDesaprovar = p;
      $("#msgDesaprovar").innerHTML = "Informe a justificativa para desaprovar o pedido <b>" + rot + "</b>.";
      $("#txtJustificativa").value = "";
      App.abrirDialogo($("#dlgDesaprovar"));
    } else if (acao === "criarws") {
      confirmar("Criar WSaída", "Gerar a WSaída do pedido <b>" + rot + "</b>?<br><small class='dica'>O estoque dos itens será verificado e reservado.</small>", function () {
        abrirWSaida(p);
      });
    } else if (acao === "verws") {
      abrirWSaida(p);
    } else if (acao === "separar") {
      confirmar("Iniciar separação", "Iniciar a separação do pedido <b>" + rot + "</b> (WSaída " + (p.wsaida ? p.wsaida.numero : "") + ")?", function () {
        mudarStatus(p, "Liberando para separação…", function (x) {
          x.status = "SEPARACAO";
          Estado.registrar("Separação iniciada · " + rot, "info");
          App.toast("Separação do <b>" + rot + "</b> iniciada.", "ok");
        });
      });
    } else if (acao === "picking") {
      if (!p.wsaida) { App.toast("Este pedido ainda não tem WSaída.", "erro"); return; }
      pedidoRelatorio = p;
      $("#msgRelatorio").innerHTML = "Picking list total da WSaída <b>" + p.wsaida.numero + "</b> · pedido " + rot + ".<br>Escolha o formato:";
      App.abrirDialogo($("#dlgRelatorio"));
    } else if (acao === "reenviar") {
      App.toast("Aviso de aprovação reenviado.", "info");
    } else if (acao === "editar") {
      irParaEdicao(p);
    } else {
      App.toast("Opção fora do roteiro da demonstração.", "aviso", 2200);
    }
  });

  function irParaEdicao(p) {
    if (p.status !== "DIGITACAO") {
      App.toast("Só é possível editar pedidos <b>em digitação</b>. Desaprove o pedido antes.", "aviso");
      return;
    }
    App.navegar("pedido.html?numero=" + p.numero, "Abrindo " + App.rotuloPedido(p.numero) + "…");
  }
  corpo.addEventListener("click", function (ev) {
    const a = ev.target.closest("a[data-editar]");
    if (!a) return;
    ev.preventDefault();
    const p = Estado.pedido(a.dataset.editar);
    if (p) irParaEdicao(p);
  });

  /* desaprovar (div[19]) */
  $("#okDesaprovar").addEventListener("click", function () {
    const just = $("#txtJustificativa").value.trim();
    if (!just) { App.tremer($("#dlgDesaprovar")); App.toast("Informe a justificativa.", "erro"); return; }
    const p = pedidoDesaprovar; pedidoDesaprovar = null;
    App.fecharDialogo($("#dlgDesaprovar"));
    if (!p) return;
    mudarStatus(p, "Desaprovando…", function (x) {
      x.status = "DIGITACAO";
      x.historico = (x.historico || []).concat([{ t: Date.now(), texto: "Desaprovado: " + just }]);
      Estado.registrar(App.rotuloPedido(x.numero) + " desaprovado · " + just, "aviso");
      App.toast("Pedido <b>" + App.rotuloPedido(x.numero) + "</b> voltou para digitação.", "aviso");
    });
  });

  /* picking list (div[17] → #PDF) */
  $("#PDF").addEventListener("click", function () {
    const p = pedidoRelatorio;
    App.fecharDialogo($("#dlgRelatorio"));
    if (!p) return;
    App.processar("Gerando picking list em PDF…", function () {
      const nome = "Picking-list_TOTAL_wSaida_" + p.wsaida.numero + "_fmt.pdf";
      App.baixarArquivo(nome, App.gerarPdfPicking(p), "application/pdf");
      p.picking = true;
      Estado.contar("pickings");
      Estado.salvarPedido(p);
      Estado.registrar("Picking list impresso · WSaída " + p.wsaida.numero, "roxo");
      folhaVoando(p);
      App.toast("Picking list da WSaída <b>" + p.wsaida.numero + "</b> enviado para impressão.", "roxo", 3600);
    }, 600, 1000);
  });
  $("#XLS").addEventListener("click", function () { App.toast("Na demonstração, use o formato PDF.", "aviso"); });
  $("#HTML").addEventListener("click", function () { App.toast("Na demonstração, use o formato PDF.", "aviso"); });

  function folhaVoando(p) {
    const f = document.createElement("section");
    f.className = "impressao-voando";
    f.innerHTML = "<h5>Picking list · WS " + p.wsaida.numero + "</h5><i></i><i></i><i></i><i></i><i></i><div class='imp'>⎙ Imprimindo…</div>";
    document.body.appendChild(f);
    setTimeout(function () { f.remove(); }, 2700);
  }

  /* ---------- modo Gerenciar WSaída (mesma página) ---------- */
  function abrirWSaida(p) {
    pedidoWS = p;
    App.fecharMenusDeAcao();
    $("#painelFiltro").hidden = true;
    $("#barraVoltar").hidden = false;
    $("#table_results").hidden = true;
    $("#barraCriar").hidden = true;
    $("#areaWSaida").hidden = false;
    $("#tituloPagina").textContent = "Gerenciar WSaída";
    $("#subtituloPagina").textContent = "Pedido " + App.rotuloPedido(p.numero) + " · " + (p.destinatario || "");

    const n = p.itens.length;
    $("#wsNumero").textContent = p.wsaida ? String(p.wsaida.numero) : "";
    $("#wsPedido").textContent = App.rotuloPedido(p.numero);
    $("#wsDestino").textContent = p.destinatario || "—";
    $("#wsItens").textContent = String(n);
    $("#wsInfo").innerHTML = "Tipo <b>" + App.esc(p.tipoMov || "SAÍDA PADRÃO") + "</b> · separação em <b>" + App.esc(p.dataSeparacao || Estado.hojeBR()) + "</b> · prioridade <b>" + App.esc(p.prioridade) + "</b>" + (p.critico ? ' <span class="critico">CRÍTICO</span>' : "");
    $("#wsCorpo").innerHTML = p.itens.map(function (it, i) {
      return '<tr class="entra" style="animation-delay:' + (i * 40) + 'ms"><td class="n">' + DADOS_DEMO.enderecoDe(it.cod) + "</td><td>" + App.esc(it.cod) + "</td><td>" + App.esc(it.desc) +
        '</td><td class="dir">' + App.qtd(it.qtd) + '</td><td class="dir">' + App.qtd(it.qtd) + '</td><td><span class="st st-verde">Reservado</span></td></tr>';
    }).join("");
    $("#wsEnderecos").textContent = "· " + n + " endereços";
    // O texto com o percentual já nasce pronto (o robô lê sem esperar).
    $("#wsAtendimento").textContent = "Atendimento: " + n + " de " + n + " itens (100%)";
    const barra = $("#wsBarra"); barra.style.width = "0"; setTimeout(function () { barra.style.width = "100%"; }, 30);

    const btn = $("#criar_wsaida");
    btn.disabled = true;
    btn.textContent = p.wsaida ? "WSaída já criada" : "Verificando estoque…";
    if (!p.wsaida) {
      App.carregando(true, "Verificando estoque…");
      setTimeout(function () {
        App.carregando(false);
        if (pedidoWS === p && !p.wsaida) { btn.disabled = false; btn.textContent = "Criar WSaída"; }
      }, App.atraso(500, 1000));
    }
  }

  function fecharWSaida() {
    pedidoWS = null;
    $("#areaWSaida").hidden = true;
    $("#barraVoltar").hidden = true;
    $("#painelFiltro").hidden = false;
    recolherFiltro();
    $("#barraCriar").hidden = false;
    $("#table_results").hidden = false;
    $("#tituloPagina").textContent = "Pedidos de saída";
    $("#subtituloPagina").textContent = "Crie, aprove, gere a WSaída e imprima a picking list.";
  }
  $("#btnVoltarWS").addEventListener("click", function (ev) {
    ev.preventDefault();
    const p = pedidoWS;
    fecharWSaida();
    mostrarAtualizando();
    App.processar("Voltando para a lista…", function () { desenharTabela(p ? p.numero : null); }, 300, 700);
  });

  $("#criar_wsaida").addEventListener("click", function () {
    if (!pedidoWS || pedidoWS.wsaida) return;
    codigoEsperado = App.codigoAleatorio();
    $("#lbl_random").textContent = codigoEsperado;
    $("#txt_random").value = "";
    App.abrirDialogo($("#dlgCodigoWS"));
  });

  $("#okCodigoWS").addEventListener("click", function () {
    const digitado = $("#txt_random").value.trim();
    if (!codigoEsperado || digitado !== codigoEsperado) {
      App.tremer($("#dlgCodigoWS"));
      App.toast("Código de confirmação incorreto.", "erro");
      return;
    }
    codigoEsperado = null;
    App.fecharDialogo($("#dlgCodigoWS"));
    const p = pedidoWS;
    if (!p) return;
    // Criação síncrona: o robô lê o número da WSaída logo após o OK.
    p.wsaida = { numero: Estado.reservarNumeroWSaida(), criadaEm: Date.now() };
    p.status = "WSAIDA";
    Estado.contar("wsaidas");
    Estado.salvarPedido(p);
    Estado.registrar("WSaída " + p.wsaida.numero + " criada · " + App.rotuloPedido(p.numero), "roxo");
    $("#wsNumero").textContent = String(p.wsaida.numero);
    const btn = $("#criar_wsaida"); btn.disabled = true; btn.textContent = "WSaída criada ✓";
    App.selo("WSaída " + p.wsaida.numero + " criada", App.rotuloPedido(p.numero) + " · " + p.itens.length + " itens reservados");
  });

  /* ---------- início ---------- */
  desenharTabela();
})();
