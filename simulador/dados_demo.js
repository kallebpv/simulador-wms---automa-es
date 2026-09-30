/* =====================================================================
   FluxoWMS · dados_demo.js
   Catálogo 100% fictício usado pelo simulador (produtos, unidades,
   destinatários, projetos). Os mesmos códigos de produto são usados por
   automacoes/gerar_dados_exemplo.py — se mudar aqui, mude lá também.
   ===================================================================== */

const DADOS_DEMO = {
  empresa: "FluxoWMS",
  subtitulo: "Gestão de Armazém · Ambiente de Demonstração",

  // Numeração inicial (pedidos e WSaídas)
  primeiroNumeroPedido: 104520,
  primeiroNumeroWSaida: 268100,

  unidades: ["FLUXO CD MATRIZ", "FLUXO CD FILIAL 02", "FLUXO CD FILIAL 03", "UNIDADE NORTE", "UNIDADE SUL", "UNIDADE LESTE", "POLO OESTE"],
  projetos: ["PROJETO ESPECIAL", "PROJETO ROTINA", "PROJETO CAMPANHA", "PROJETO CONTINGÊNCIA"],
  tiposMovimento: ["SAÍDA PADRÃO", "SAÍDA POR TRANSFERÊNCIA", "SAÍDA PARA DESCARTE", "DEVOLUÇÃO AO FORNECEDOR"],

  destinatarios: [
    { codigo: "D-0101", nome: "UNIDADE NORTE", cidade: "Vila Aurora" },
    { codigo: "D-0102", nome: "UNIDADE NORTE II - ANEXO", cidade: "Vila Aurora" },
    { codigo: "D-0201", nome: "UNIDADE SUL", cidade: "Porto Sereno" },
    { codigo: "D-0301", nome: "UNIDADE LESTE", cidade: "Lagoa Clara" },
    { codigo: "D-0401", nome: "POLO OESTE", cidade: "Monte Alegre do Vale" },
    { codigo: "D-0501", nome: "FARMÁCIA CENTRAL DEMO", cidade: "Vila Aurora" }
  ],

  // [codigo, descrição, categoria]
  produtos: [
    // DIETAS
    ["20114", "Dieta enteral polimérica 1,5 kcal/ml 1000 ml", "DIETAS"],
    ["20127", "Dieta enteral hiperproteica 1,2 kcal/ml 1000 ml", "DIETAS"],
    ["20131", "Dieta oral hipercalórica 200 ml baunilha", "DIETAS"],
    ["20146", "Dieta oral hipercalórica 200 ml chocolate", "DIETAS"],
    ["20158", "Suplemento hiperproteico em pó 400 g", "DIETAS"],
    ["20163", "Fórmula infantil de partida lata 800 g", "DIETAS"],
    ["20175", "Fórmula infantil de seguimento lata 800 g", "DIETAS"],
    ["20182", "Fórmula infantil sem lactose lata 400 g", "DIETAS"],
    ["20199", "Espessante alimentar instantâneo 125 g", "DIETAS"],
    ["20203", "Módulo de proteína isolada 250 g", "DIETAS"],
    ["20217", "Módulo de fibras solúveis 260 g", "DIETAS"],
    ["20224", "Dieta enteral para diabéticos 1000 ml", "DIETAS"],
    ["20236", "Fórmula de aminoácidos livres lata 400 g", "DIETAS"],
    ["20241", "Dieta semielementar 1,0 kcal/ml 500 ml", "DIETAS"],
    ["20258", "Suplemento para cicatrização 200 ml", "DIETAS"],
    ["20262", "Gelatina hiperproteica pote 120 g", "DIETAS"],
    ["20279", "Dieta enteral pediátrica 500 ml", "DIETAS"],
    ["20285", "Triglicerídeos de cadeia média 250 ml", "DIETAS"],
    // MEDICAMENTOS
    ["21304", "Omeprazol 20 mg cápsula", "MEDICAMENTOS"],
    ["21311", "Losartana potássica 50 mg comprimido", "MEDICAMENTOS"],
    ["21329", "Metformina 850 mg comprimido", "MEDICAMENTOS"],
    ["21336", "Insulina humana NPH 100 UI/ml frasco 10 ml", "MEDICAMENTOS"],
    ["21342", "Insulina humana regular 100 UI/ml frasco 10 ml", "MEDICAMENTOS"],
    ["21350J", "Enoxaparina sódica 40 mg seringa", "MEDICAMENTOS"],
    ["21367", "Levotiroxina 50 mcg comprimido", "MEDICAMENTOS"],
    ["21373", "Sinvastatina 20 mg comprimido", "MEDICAMENTOS"],
    ["21388", "Dipirona 500 mg/ml gotas 20 ml", "MEDICAMENTOS"],
    ["21395", "Paracetamol 750 mg comprimido", "MEDICAMENTOS"],
    ["21401", "Amoxicilina 500 mg cápsula", "MEDICAMENTOS"],
    ["21418", "Salbutamol aerossol 100 mcg", "MEDICAMENTOS"],
    ["21422", "Prednisolona 3 mg/ml solução oral 60 ml", "MEDICAMENTOS"],
    ["21439", "Carbamazepina 200 mg comprimido", "MEDICAMENTOS"],
    ["21444", "Ácido fólico 5 mg comprimido", "MEDICAMENTOS"],
    ["21457", "Sulfato ferroso 40 mg comprimido", "MEDICAMENTOS"],
    ["21463", "Vitamina D 7.000 UI cápsula", "MEDICAMENTOS"],
    ["21476", "Budesonida 32 mcg spray nasal", "MEDICAMENTOS"],
    // MATERIAL MÉDICO
    ["22108", "Seringa descartável 10 ml sem agulha", "MATERIAL MÉDICO"],
    ["22113", "Seringa para insulina 1 ml com agulha", "MATERIAL MÉDICO"],
    ["22125", "Agulha hipodérmica 25x7", "MATERIAL MÉDICO"],
    ["22137", "Luva de procedimento M caixa com 100", "MATERIAL MÉDICO"],
    ["22149", "Sonda nasoenteral 12 Fr", "MATERIAL MÉDICO"],
    ["22151", "Equipo para dieta enteral gravitacional", "MATERIAL MÉDICO"],
    ["22166", "Tiras reagentes de glicemia caixa com 50", "MATERIAL MÉDICO"],
    ["22172", "Lancetas descartáveis caixa com 100", "MATERIAL MÉDICO"],
    ["22184", "Cateter intravenoso 22G", "MATERIAL MÉDICO"],
    ["22197", "Máscara cirúrgica tripla caixa com 50", "MATERIAL MÉDICO"],
    ["22203", "Coletor de urina sistema fechado 2 L", "MATERIAL MÉDICO"],
    ["22218", "Sonda uretral 10 Fr", "MATERIAL MÉDICO"],
    ["22226", "Frasco para dieta enteral 500 ml", "MATERIAL MÉDICO"],
    ["22231", "Extensor para equipo 20 cm", "MATERIAL MÉDICO"],
    ["22245", "Sensor de glicose descartável 14 dias", "MATERIAL MÉDICO"],
    ["22259", "Bolsa de colostomia 45 mm", "MATERIAL MÉDICO"],
    ["22262", "Cânula de traqueostomia nº 8", "MATERIAL MÉDICO"],
    ["22270", "Filtro HME para traqueostomia", "MATERIAL MÉDICO"],
    // FRALDAS E HIGIENE
    ["23102", "Fralda geriátrica G pacote com 8", "FRALDAS E HIGIENE"],
    ["23119", "Fralda geriátrica M pacote com 9", "FRALDAS E HIGIENE"],
    ["23125", "Fralda geriátrica EG pacote com 7", "FRALDAS E HIGIENE"],
    ["23131", "Fralda infantil XG pacote com 24", "FRALDAS E HIGIENE"],
    ["23148", "Absorvente geriátrico pacote com 20", "FRALDAS E HIGIENE"],
    ["23154", "Lenço umedecido pacote com 50", "FRALDAS E HIGIENE"],
    ["23167", "Creme barreira 60 g", "FRALDAS E HIGIENE"],
    ["23173", "Lençol descartável rolo 50 m", "FRALDAS E HIGIENE"],
    ["23186", "Roupa íntima descartável G pacote com 8", "FRALDAS E HIGIENE"],
    ["23192", "Sabonete líquido neutro 1 L", "FRALDAS E HIGIENE"],
    ["23205", "Óleo de girassol com AGE 200 ml", "FRALDAS E HIGIENE"],
    ["23211", "Luva de banho descartável pacote com 10", "FRALDAS E HIGIENE"],
    ["23228", "Protetor de colchão descartável", "FRALDAS E HIGIENE"],
    ["23234", "Hidratante ureia 10% 120 g", "FRALDAS E HIGIENE"],
    // CURATIVOS
    ["24103", "Curativo de hidrocoloide 10x10 cm", "CURATIVOS"],
    ["24116", "Gaze estéril 7,5x7,5 cm pacote com 10", "CURATIVOS"],
    ["24122", "Atadura de crepom 15 cm", "CURATIVOS"],
    ["24139", "Esparadrapo 10 cm x 4,5 m", "CURATIVOS"],
    ["24145", "Curativo de espuma com prata 10x10 cm", "CURATIVOS"],
    ["24158", "Soro fisiológico 0,9% 250 ml", "CURATIVOS"],
    ["24164", "Filme transparente 10x12 cm", "CURATIVOS"],
    ["24171", "Alginato de cálcio 10x10 cm", "CURATIVOS"],
    ["24187", "Hidrogel com alginato 25 g", "CURATIVOS"],
    ["24193", "Fita microporosa 25 mm x 10 m", "CURATIVOS"],
    ["24206", "Compressa não tecida 10x10 cm pacote com 5", "CURATIVOS"],
    ["24212", "Carvão ativado com prata 10x10 cm", "CURATIVOS"],
    ["24229", "Placa de silicone para cicatriz 12x15 cm", "CURATIVOS"],
    ["24235", "Bota de Unna 10,2 cm x 9,14 m", "CURATIVOS"]
  ]
};

/* Mapa rápido código -> produto */
DADOS_DEMO.produtoPorCodigo = {};
DADOS_DEMO.produtos.forEach(function (p) {
  DADOS_DEMO.produtoPorCodigo[p[0].toUpperCase()] = { codigo: p[0], descricao: p[1], categoria: p[2] };
});

/* Endereço de armazém fictício, estável por código (para a picking list) */
DADOS_DEMO.enderecoDe = function (codigo) {
  let h = 0;
  String(codigo).split("").forEach(function (c) { h = (h * 31 + c.charCodeAt(0)) % 99991; });
  const rua = String.fromCharCode(65 + (h % 8));
  const modulo = String(1 + (h % 24)).padStart(2, "0");
  const nivel = String(1 + (Math.floor(h / 7) % 5)).padStart(2, "0");
  const pos = 1 + (Math.floor(h / 13) % 4);
  return rua + "-" + modulo + "-" + nivel + "-" + pos;
};
