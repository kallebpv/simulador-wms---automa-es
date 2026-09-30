from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from funcaos import localizar_e_clicar_elemento, localizar_e_preencher, localizar_e_selecionar_por_visibilidade, preencher_campo, clicar_com_js, localizar_e_preencher_2, preencher_com_tabs, colar_texto_formatado, colar_via_javascript, preencher_com_tabs_seguro, obter_texto_por_id
from funcaos import iniciar_chrome_demo  # [SIMULADOR]
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from funcaoLerPlanilha import processar_planilha, limpar_valor
from selenium.webdriver.support.ui import WebDriverWait
import sys
import os
import psutil
import signal
import codecs

# [SIMULADOR] Endereço do simulador FluxoWMS (no lugar do endereço do sistema real).
URL_SIMULADOR = "http://localhost:8080/"

if hasattr(sys.stdout, "detach"):
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
if hasattr(sys.stderr, "detach"):
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


def main(controle=None, **kwargs):
    driver = None
     # Se a automação for interrompida antes de iniciar
    if controle and not controle.automacao_ativa:
        print("🚦 Automação interrompida pelo usuário antes de iniciar!")
        return
    # Validação básica dos parâmetros
    required_params = ['usuario', 'senha', 'pasta', 'data', 'observacao', 'nome_relatorio', 'nome_arquivo']
    for param in required_params:
        if controle and not controle.automacao_ativa:
                print("🚦 Automação interrompida pelo usuário!")
                break
    
    # Construção dos parâmetros
    params = {
        'usuario': kwargs['usuario'],
        'senha': kwargs['senha'],
        'pasta_caminho': kwargs['pasta'],
        'data da criacao': kwargs['data do dia criado'],
        'data de expedicao': kwargs['data do dia de expedir'],
        'nome_relatorio': kwargs['nome_relatorio'],
        'data_agendamento': kwargs['data_do_agendamento']
    }

    # Processamento principal
    caminho_relatorio = os.path.join(params['pasta_caminho'], params['nome_relatorio'])



    # Substitua por isto (para .exe e desenvolvimento):
    caminho_atual = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    chrome_driver_path = os.path.join(caminho_atual, "chromedriver.exe")

# Configuração do Selenium para usar esse ChromeDriver corretamente
    print(f"🛠️ Verificando ChromeDriver em: {chrome_driver_path}")

    if not os.path.exists(chrome_driver_path):
        print(f"🚨 Arquivo chromedriver.exe não encontrado em: {chrome_driver_path}")
        print("ℹ️ Usando o driver baixado automaticamente pelo Selenium.")  # [SIMULADOR]
        # raise FileNotFoundError("chromedriver.exe ausente")  # [SIMULADOR] o chromedriver.exe na pasta deixou de ser obrigatório

    try:
        driver = iniciar_chrome_demo(chrome_driver_path)  # [SIMULADOR] opções de gravação + driver automático
        print("✅ ChromeDriver iniciado com sucesso!")
    except Exception as e:
        print(f"🚨 Erro ao iniciar o ChromeDriver: {str(e)}")
        print("👉 Solução: Baixe a versão correta em https://chromedriver.chromium.org/")
        raise
    
    try:
         # Antes de cada ação, verificar se a automação foi parada
        if controle and controle.automacao_ativa:
            print("Automação rodando...")
            planilha_de_pacientes = processar_planilha(caminho_relatorio)
            ac = ActionChains(driver)
            wait = WebDriverWait(driver, 5)

            driver.get(URL_SIMULADOR)  # [SIMULADOR]
            print("Navegador aberto.")



            #CLICAR EM ENTRAR
            localizar_e_clicar_elemento(driver, "//a[contains(text(),'Entrar')]",\
                                        msg_sucesso='Entrou com sucesso.', msg_falha='Falhou no início tentar entrar.')

            #PRENCHEER USUARIO
            localizar_e_preencher(driver, "//input[@name='data[Usuario][login]']", params['usuario'],\
                                msg_sucesso="Usuário preenchido.", msg_falha="Erro ao preencher usuário.")
            
            #PREENCHER SENHA
            localizar_e_preencher(driver, "//input[@name='data[Usuario][senha]']", params["senha"],\
                                msg_sucesso='senha sucesso', msg_falha='senha falha')
            #CLICAR NO BOTÃO LOGIN
            localizar_e_clicar_elemento(driver, "//input[@type='submit' and @value='Login']",\
                                        msg_sucesso="Botão de login clicado.", msg_falha="Erro ao clicar no botão de login.")
            #CLICAR NO BOTÃO WMS
            localizar_e_clicar_elemento(driver, "//div[contains(@class, 'link-modulo') and contains(@link, '/Homes/index/wms')]",\
                                        msg_sucesso= 'Botão WMS clicado com sucesso', msg_falha='Falha ao clicar no botão WMS')
            #CLICAR NO BOTÃO DE ABA ESQUERDA.
            localizar_e_clicar_elemento(driver,"//span[contains(@class, 'menu-anchor-opendata')]",\
                                        msg_sucesso='aba esquerda clicada com sucesso', msg_falha='falaha ao clicar aba esquerda')
            #CLICAR NO BOTÃO DE WMS DA ABA ESQUERDA.
            localizar_e_clicar_elemento(driver,"//a[contains(@class, 'list-group-item') and contains(text(), 'WMS')]",\
                                        msg_sucesso='wms da aba esquerda encontrado', msg_falha='falha ao encontrar wms da aba esquerda')
            
            #CLICAR NO BOTÃO SAÍDA DA ABA ESQUERDA.
            localizar_e_clicar_elemento(driver,"//a[contains(@class, 'list-group-item') and contains(text(), 'Saida')]",\
                                             msg_sucesso='Saída clicada na aba esquerda com sucesso.')

            #CLICAR NO BOTÃO ARMAZÉM DA ABA ESQUERDA.
            localizar_e_clicar_elemento(driver,"//a[contains(@class, 'list-group-item') and contains(text(), 'Armazém')]",\
                                        msg_sucesso='Saída clicada na aba esquerda com sucesso.')
            #CLICAR NO BOTÃO PEDIDOS DE REABASTECIMENTO NA ABA ESQUERDA.
            localizar_e_clicar_elemento(driver,"//a[contains(@class, 'list-group-item') and contains(text(), 'Pedidos de reabastecimento')]",\
                                        msg_sucesso='Botão Pedidos da aba esquerda clicado com sucesso', msg_falha='Falha ao clicar no botão Pedidos da aba esquerda.')
            #CLICAR NO 'X' DE FECHAR A ABA ESQUERDA.
            localizar_e_clicar_elemento(driver,'//*[@id="closeMenuOpendata"]/span',\
                                        msg_sucesso='Aba esquerda fechada com sucesso.',msg_falha='Falha ao tentar Fechar aba esquerda')
            
            #CLICAR EM PESQUISA
            localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div/div/div/div/a',\
                                                msg_sucesso= 'Botão PESQUISA clicado com sucesso', msg_falha='Falha ao tentar clicar em botão PESQUISA')

            #CLICAR E PRENCHER DATA DE CRIAÇÃO(DE ACORDO COM A QUE O USUARIO PODERÁ ESCOLHER)
            localizar_e_preencher(driver,'/html/body/div[4]/div[2]/div[3]/div[3]/div/div/form/div[2]/div/div/fieldset/div[1]/div[3]/div/div/div[1]/input', params['data da criacao'],\
                                        msg_sucesso='Sucesso ao preencher data',msg_falha='Falha ao tentar preencher data')
            
            #CLICAR EM PESQUISAR
            localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div/div/form/div[2]/div/div/fieldset/div[2]/div/div/button[2]',\
                                                msg_sucesso= 'Botão PESQUISAR clicado com sucesso', msg_falha='Falha ao tentar clicar em botão PESQUISAR')

            for tipo, quantidade_itens in planilha_de_pacientes.items():
                 # Antes de cada ação, verificar se a automação foi parada
                if controle and controle.automacao_ativa:
                    print("Automação rodando...")
                    if not kwargs.get('automacao_ativa', True):  # Verifica estado
                        print("Automação interrompida pelo usuário")
                        break

                    qt_itens_tratado = "\n".join(
                        f"{limpar_valor(codigo)}\t{limpar_valor(pedido)}"
                        for codigo, pedido in zip(quantidade_itens["CÓD"], quantidade_itens["PEDIDO "])
                     )
                    #CLICAR EM NOVO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div/div/div/a[2]',\
                                                msg_sucesso= 'Botão NOVO clicado com sucesso', msg_falha='Falha ao tentar clicar em botão NOVO')
                    
                    
                    #CLICAR NA SELEÇÃO UNIDADE DE ORIGEM.
                    #USAR SETA PARA BAIXO, PARA PARAR EM FLUXO CD MATRIZ  [SIMULADOR] nome fictício
                    localizar_e_selecionar_por_visibilidade(driver, '/html/body/div[4]/div[2]/div[3]/div[4]/form/div[2]/div/div/div[2]/div/div[2]/div[1]/div/select', 'FLUXO CD MATRIZ',\
                                                            msg_sucesso='Sucesso ao selecionar FLUXO CD MATRIZ', msg_falha='Sucesso ao selecionar FLUXO CD MATRIZ')  # [SIMULADOR] nome fictício
                    
                    #CLICAR NA SELEÇÃO UNIDADE DE DESTINO.
                    #USAR SETA PARA BAIXO, PARA PARAR EM UNIDADE NORTE  [SIMULADOR] nome fictício
                    localizar_e_selecionar_por_visibilidade(driver, '/html/body/div[4]/div[2]/div[3]/div[4]/form/div[2]/div/div/div[2]/div/div[2]/div[2]/div/select','UNIDADE NORTE',\
                                                            msg_sucesso='Sucesso ao selecionar UNIDADE NORTE', msg_falha='Sucesso ao selecionar UNIDADE NORTE')  # [SIMULADOR] nome fictício
                    
                    #CLICAR NA SELEÇÃO PROJETO ORIGEM.
                    #USAR SETA PARA BAIXO, PARA PARAR EM PROJETO ESPECIAL  [SIMULADOR] nome fictício
                    localizar_e_selecionar_por_visibilidade(driver, '/html/body/div[4]/div[2]/div[3]/div[4]/form/div[2]/div/div/div[2]/div/div[3]/div[1]/div/select','PROJETO ESPECIAL',\
                                                            msg_sucesso='Sucesso ao selecionar PROJETO ESPECIAL', msg_falha='Sucesso ao selecionar PROJETO ESPECIAL')  # [SIMULADOR] nome fictício
                    
                    #CLICAR NA SELEÇÃO PROJETO DESTINO.
                    #USAR SETA PARA BAIXO, PARA PARAR EM PROJETO ESPECIAL  [SIMULADOR] nome fictício
                    localizar_e_selecionar_por_visibilidade(driver, '/html/body/div[4]/div[2]/div[3]/div[4]/form/div[2]/div/div/div[2]/div/div[3]/div[2]/div/select','PROJETO ESPECIAL',\
                                                            msg_sucesso='Sucesso ao selecionar DESTINO', msg_falha='Sucesso ao selecionar DESTINO')


                    #CLICAR EM IMPORTAR CSV
                    localizar_e_clicar_elemento(driver,'/html/body/div[4]/div[2]/div[3]/div[4]/form/div[5]/div/button',\
                                                msg_sucesso='Sucesso ao clicar em importar CSV',msg_falha='Falha ao clicar em importar CSV')
                    #CLICAR EM OK(O CLIENTE NÃO PODE SER MAIS MODIFICADO)
                    localizar_e_clicar_elemento(driver,'/html/body/div[15]/div[3]/div/button[2]/span',\
                                                msg_sucesso='Sucesso ao clicar OK depois de clicar em em importar CSV',msg_falha='Falha ao clicar OK depois de clicar em em importar CSV')
                    #CLICAR E PRENCHER A PARTE DE INSERÇÃO DE PRODUTOS DE QUANTIDADES.
                    preencher_com_tabs_seguro(driver,'/html/body/div[6]/div[2]/div/div/form/div[2]/div/div/div/div/textarea',qt_itens_tratado,\
                                                msg_sucesso='Sucesso ao inserir Produtos e Quantidades', msg_falha='Falha ao tentar inserir Produtos e Quantidades')
                    #CLICAR EM IMPORTAR PRODUTOS
                    localizar_e_clicar_elemento(driver,'/html/body/div[6]/div[3]/div/button[1]/span',\
                                                msg_sucesso='Sucesso ao importar produtos',msg_falha='Falha ao importar produtos')
                    # Localiza o elemento que contém "Pedido Normal"
                    elemento = driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div[1]/h2')
                    texto_pedido = elemento.text  # Exemplo: "Pedido # 202169808"

                    # Usa expressão regular para extrair somente os dígitos do número do pedido
                    match = re.search(r"Pedido #\s*(\d+)", texto_pedido)
                    if match:
                        numero_pedido = match.group(1)
                        print("Número do pedido:", numero_pedido)
                    else:
                        print("Não foi possível extrair o número do pedido.")

                    #CLICAR EM VOLTAR FINALIZANDO A CRIAÇÃO DE UM PEDIDO.
                    localizar_e_clicar_elemento(driver,"//a[contains(text(), 'Voltar')]",\
                                                msg_sucesso='Sucesso ao clicar no botão voltar finalizando o pedido', msg_falha='Falha ao tentar clicar no botão voltar finalizando o pedido')
                    
                    #CLICAR EM PESQUISA
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div/div/div/div/a',\
                                                msg_sucesso= 'Botão PESQUISA clicado com sucesso', msg_falha='Falha ao tentar clicar em botão PESQUISA')
            
                    #LOCALIZAR BARRA DE NUMERO DO PEDIDO E PREENCHER
                    localizar_e_preencher(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div/div/form/div[2]/div/div/fieldset/div[1]/div[2]/div/input', text=numero_pedido,\
                                          msg_sucesso='Sucesso ao clicar e prencher a barra de numero do pedido', msg_falha='Falha ao clicar e prencher a barra de numero do pedido')
                    
                    #CLICAR EM PESQUISAR
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div/div/form/div[2]/div/div/fieldset/div[2]/div/div/button[2]',\
                                                msg_sucesso= 'Botão PESQUISAR clicado com sucesso', msg_falha='Falha ao tentar clicar em botão PESQUISAR')
                    
                    #CLICAR NO MENU DO PEDIDO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[6]/div/table/tbody/tr/td[11]/div/span',\
                                                msg_sucesso= 'Botão MENU clicado com sucesso', msg_falha='Falha ao tentar clicar em botão MENU')
                    
                    #CLICAR EM SOLICITAR APROVACAO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[6]/div/table/tbody/tr/td[11]/div/ul/li[4]/a',\
                                                msg_sucesso= 'Botão SOLICITAR APROVACAO clicado com sucesso', msg_falha='Falha ao tentar clicar em botão SOLICITAR APROVACAO')
                    
                    #LOCALIZAR E COPIAR CODIGO DE APROVACAO DA SOLICITACAO DE APROVACAO
                    codigo_solicitar_aprovacao = obter_texto_por_id(driver, ID='lbl_random', msg_sucesso='sucesso ao copiar codigo de aprovacao de solicitar aprovacao', msg_falha='falha ao copiar codigo de aprovacao de solicitar aprovacao')

                    #LOCALIZAR E PREENCHER BARRA DO CODIGO DE APROVACAO DE SOLCITAR APROVACAO
                    localizar_e_preencher(driver, '/html/body/div[16]/div[2]/form/div/input', text=codigo_solicitar_aprovacao,\
                                          msg_sucesso='sucesso ao copiar codigo de aprovacao de solicitar aprovacao', msg_falha='falha ao copiar codigo de aprovacao de solicitar aprovacao')
                    
                    #CLICAR EM OK
                    localizar_e_clicar_elemento(driver, '/html/body/div[16]/div[3]/div/button[2]/span',\
                                                msg_sucesso= 'Botão OK clicado com sucesso', msg_falha='Falha ao tentar clicar em botão OK')
                    
                    #CLICAR NO MENU DO PEDIDO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[6]/div/table/tbody/tr/td[11]/div/span',\
                                                msg_sucesso= 'Botão MENU clicado com sucesso', msg_falha='Falha ao tentar clicar em botão MENU')
                    
                    #CLICAR EM NO BOTAO APROVAR PEDIDO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[6]/div/table/tbody/tr/td[11]/div/ul/li[4]/a',\
                                                msg_sucesso= 'Botão APROVAR PEDIDO clicado com sucesso', msg_falha='Falha ao tentar clicar em botão APROVAR PEDIDO')
                    
                    #LOCALIZAR E COPIAR CODIGO DE APROVACAO DA SOLICITACAO DE APROVAR PEDIDO
                    codigo_solicitar_aprovacao = obter_texto_por_id(driver, ID='lbl_random',\
                                                                     msg_sucesso='sucesso ao copiar codigo de aprovacao de APROVAR PEDIDO', msg_falha='falha ao copiar codigo de aprovacao de APROVAR PEDIDO')

                    #LOCALIZAR E PREENCHER BARRA DO CODIGO DE APROVACAO DE APROVAR PEDIDO
                    localizar_e_preencher(driver, '/html/body/div[16]/div[2]/form/div/input', text=codigo_solicitar_aprovacao,\
                                          msg_sucesso='sucesso ao copiar codigo de aprovacao de APROVAR PEDIDO', msg_falha='falha ao copiar codigo de aprovacao de APROVAR PEDIDO')
                    
                    #CLICAR EM OK
                    localizar_e_clicar_elemento(driver, '/html/body/div[16]/div[3]/div/button[2]/span',\
                                                msg_sucesso= 'Botão OK clicado com sucesso', msg_falha='Falha ao tentar clicar em botão OK')
                    
                    #CLICAR NO MENU DO PEDIDO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[6]/div/table/tbody/tr/td[11]/div/span',\
                                                msg_sucesso= 'Botão MENU clicado com sucesso', msg_falha='Falha ao tentar clicar em botão MENU')
                    
                    #CLICAR NO BOTAO SUBMETER INTEGRACAO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[6]/div/table/tbody/tr/td[11]/div/ul/li[5]/a',\
                                                msg_sucesso= 'Botão SUBMETER INTEGRACAO clicado com sucesso', msg_falha='Falha ao tentar clicar em botão SUBMETER INTEGRACAO')
                    
                    #LOCALIZAR E COPIAR CODIGO DE APROVACAO DA SOLICITACAO DE SUBMETER INTEGRACAO
                    codigo_solicitar_aprovacao = obter_texto_por_id(driver, ID='lbl_random',\
                                                                     msg_sucesso='sucesso ao copiar codigo de aprovacao de SUBMETER INTEGRACAO', msg_falha='falha ao copiar codigo de aprovacao de SUBMETER INTEGRACAO')

                    #LOCALIZAR E PREENCHER BARRA DO CODIGO DE APROVACAO DE SUBMETER INTEGRACAO
                    localizar_e_preencher(driver, '/html/body/div[16]/div[2]/form/div/input', text=codigo_solicitar_aprovacao,\
                                          msg_sucesso='sucesso ao copiar codigo de aprovacao de SUBMETER INTEGRACAO', msg_falha='falha ao copiar codigo de aprovacao de SUBMETER INTEGRACAO')
                    
                    #CLICAR EM OK
                    localizar_e_clicar_elemento(driver, '/html/body/div[16]/div[3]/div/button[2]/span',\
                                                msg_sucesso= 'Botão OK clicado com sucesso', msg_falha='Falha ao tentar clicar em botão OK')
                    # CONTINUAR DAQUI...
                     #CLICAR NO BOTÃO DE ABA ESQUERDA.
                    localizar_e_clicar_elemento(driver,"//span[contains(@class, 'menu-anchor-opendata')]",\
                                        msg_sucesso='aba esquerda clicada com sucesso', msg_falha='falaha ao clicar aba esquerda')
                     
                    #CLICAR NO BOTÃO PEDIDOS NA ABA ESQUERDA.
                    localizar_e_clicar_elemento(driver,"//a[contains(@class, 'list-group-item') and contains(text(), 'Pedidos')]",\
                                                msg_sucesso='Botão Pedidos da aba esquerda clicado com sucesso', msg_falha='Falha ao clicar no botão Pedidos da aba esquerda.')
                    #CLICAR NO 'X' DE FECHAR A ABA ESQUERDA.
                    localizar_e_clicar_elemento(driver,'//*[@id="closeMenuOpendata"]/span',\
                                                msg_sucesso='Aba esquerda fechada com sucesso.',msg_falha='Falha ao tentar Fechar aba esquerda')
                    
                    #CLICAR EM PESQUISAR
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div/div/h4/a',\
                                                msg_sucesso= 'Botão PESQUISAR clicado com sucesso', msg_falha='Falha ao tentar clicar em botão PESQUISAR')
                    
                    #LOCALIZAR A BARRA DE OBSERVACAO E PREENCHER COM O NUMERO DO PEDIDO DE REABASTECIMENTO
                    localizar_e_preencher(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div/form/div[2]/div/div[2]/fieldset[1]/div[9]/div/div/input', text='PEDIDO: '+ numero_pedido,\
                                          msg_sucesso='sucesso ao LOCALIZAR A BARRA DE OBSERVACAO E PREENCHER COM O NUMERO DO PEDIDO DE REABASTECIMENTO', msg_falha='falha ao LOCALIZAR A BARRA DE OBSERVACAO E PREENCHER COM O NUMERO DO PEDIDO DE REABASTECIMENTO')
                    #CLICAR EM FILTRAR
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div/form/div[2]/div/div[2]/fieldset[5]/div/div/div/button',\
                                                msg_sucesso= 'Botão FILTRAR clicado com sucesso', msg_falha='Falha ao tentar clicar em botão FILTRAR')
                    
                    #CLICAR NO MENU DO PEDIDO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/table/tbody/tr[4]/td[12]/div/span',\
                                                msg_sucesso= 'Botão MENU clicado com sucesso', msg_falha='Falha ao tentar clicar em botão MENU')
                    
                    #CLICAR NO BOTÃO DESAPROVAR PEDIDO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/table/tbody/tr[4]/td[12]/div/ul/li[7]/a',\
                                                msg_sucesso= 'Botão DESAPROVAR PEDIDO clicado com sucesso', msg_falha='Falha ao tentar clicar em botão DESAPROVAR PEDIDO')
                    
                    #LOCALIZAR A BARRA DE JUSTIFICATIVA DE DESAPROVAR PEDIDO E PREENCHER COM A JUSTIFICATIVA: AJUSTE DE PEDIDO
                    localizar_e_preencher(driver, '/html/body/div[19]/div[2]/form/input', text='AJUSTE DE PEDIDO',\
                                          msg_sucesso='sucesso ao LOCALIZAR A BARRA DE JUSTIFICATIVA DE DESAPROVAR PEDIDO E PREENCHER COM A JUSTIFICATIVA: AJUSTE DE PEDIDO', msg_falha='falha ao LOCALIZAR A BARRA DE JUSTIFICATIVA DE DESAPROVAR PEDIDO E PREENCHER COM A JUSTIFICATIVA: AJUSTE DE PEDIDO')
                    
                    #CLICAR NO BOTÃO OK
                    localizar_e_clicar_elemento(driver, '/html/body/div[19]/div[3]/div/button[2]',\
                                                msg_sucesso= 'Botão OK clicado com sucesso', msg_falha='Falha ao tentar clicar em botão OK')
                    
                    #CLICAR NO BOTÃO EDITAR PEDIDO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/table/tbody/tr[4]/td[9]/a',\
                                                msg_sucesso= 'Botão EDITAR PEDIDO clicado com sucesso', msg_falha='Falha ao tentar clicar em botão EDITAR PEDIDO')
                    
                    #CLICAR NA SELEÇÃO TIPO DE SAÍDA.
                    #USAR SETA PARA BAIXO, PARA PARAR EM SAÍDA PADRÃO
                    localizar_e_selecionar_por_visibilidade(driver, '//*[@id="id_tipo_movimento"]','SAÍDA PADRÃO',\
                                                            msg_sucesso='Sucesso ao selecionar SAÍDA PADRÃO', msg_falha='Sucesso ao selecionar SAÍDA PADRÃO')
                    
                    # Localiza o elemento que contém "Pedido Normal"
                    elemento_saida = driver.find_element(By.XPATH, "//h2[contains(text(), 'Pedido Normal')]")
                    texto_pedido_saida = elemento_saida.text
                    
                    # Usa expressão regular para extrair somente os dígitos do número do pedido
                    match = re.search(r"Pedido Normal #\s*(\d+)", texto_pedido_saida)
                    if match:
                        numero_pedido_saida = match.group(1)
                        print("Número do pedido:", numero_pedido_saida)
                    else:
                        print("Não foi possível extrair o número do pedido.")
                        numero_pedido_saida = 'NN'
                    
                    #SELECIONAR PRIORIDADE
                    localizar_e_selecionar_por_visibilidade(driver,'//*[@id="nprioridade_ped"]','0',\
                                                            msg_sucesso='Sucesso ao selecionar prioridade Zero',msg_falha='Falha ao selecionar prioridade Zero')
                    
                    #CLICAR NO BOTÃO CRÍTICO.
                    localizar_e_clicar_elemento(driver,'//*[@id="bcritico_ped"]',\
                                                msg_sucesso='Sucesso ao clicar no botão crítico', msg_falha='Falha ao clicar no botão crítico')
                    
                    #CLICAR E PREENCHER MOTIVO CRITICIDADE
                    # [SIMULADOR] nomes reais trocados por fictícios na linha abaixo
                    localizar_e_preencher(driver,'//*[@id="stexto_urgente_ped"]','Demanda Prioritária',\
                                        msg_sucesso='Sucesso ao preencher motivo Criticidade',msg_falha='Falha ao tentar preencher motivo Criticidade')

                    #CLICAR E PRENCHER DATA(DE ACORDO COM A QUE FUTURAMENTE O USUARIO PODERÁ ESCOLHER)
                    localizar_e_preencher(driver,'//*[@id="dtseparacao_ped"]', params['data de expedicao'],\
                                        msg_sucesso='Sucesso ao preencher data',msg_falha='Falha ao tentar preencher data')
                    
                    #CLICAR E PREENCHER OBSERVAÇÃO, OBSERVE, SERÁ PRENCHIDO COM A OBSERVAÇÃO DADA FUTURAMENTE PELO O USUÁRIO E O PACIENTE E PROCESSO QUE SÃO DADOS DA PLANILHA.
                    localizar_e_preencher(driver,'//*[@id="mobs_ped"]', 'PEDIDO DE REABASTECIMENTO: '+ numero_pedido + ' Obs do pedido de Reabastecimento: Pedido aprovado - ' + numero_pedido_saida + ' - ' + tipo + ' - ' + params['data_agendamento'],\
                                        msg_sucesso='Sucesso ao prencher observação.', msg_falha='Falha ao tentar preenhcer observação.')
                    
                    #CLICAR NO BOTÃO DE SALVAR PEDIDO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[4]/form/div[4]/div/div/div/div[3]/div[1]/div/button[3]',\
                                                msg_sucesso= 'Botão SALVAR clicado com sucesso', msg_falha='Falha ao tentar clicar em botão SALVAR')
                    
                    #CLICAR EM VOLTAR FINALIZANDO UM PEDIDO.
                    localizar_e_clicar_elemento(driver,"//a[contains(text(), 'Voltar')]",\
                                                msg_sucesso='Sucesso ao clicar no botão voltar finalizando edicao do pedido', msg_falha='Falha ao tentar clicar no botão voltar finalizando a edicao do pedido')
                    
                    #CLICAR NO BOTÃO DE ABA ESQUERDA.
                    localizar_e_clicar_elemento(driver,"//span[contains(@class, 'menu-anchor-opendata')]",\
                                        msg_sucesso='aba esquerda clicada com sucesso', msg_falha='falaha ao clicar aba esquerda')
                    
                    #CLICAR NO BOTÃO PEDIDOS DE REABASTECIMENTO NA ABA ESQUERDA.
                    localizar_e_clicar_elemento(driver,"//a[contains(@class, 'list-group-item') and contains(text(), 'Pedidos de reabastecimento')]",\
                                        msg_sucesso='Botão Pedidos da aba esquerda clicado com sucesso', msg_falha='Falha ao clicar no botão Pedidos da aba esquerda.')
                    #CLICAR NO 'X' DE FECHAR A ABA ESQUERDA.
                    localizar_e_clicar_elemento(driver,'//*[@id="closeMenuOpendata"]/span',\
                                        msg_sucesso='Aba esquerda fechada com sucesso.',msg_falha='Falha ao tentar Fechar aba esquerda')
                    
                    # AQUI A AUTOMACAO VOLTOU PARA O PEDIDO DE REABASTECIMENTO PARA INICIAR UM NOVO CICLO DE PEDIDO DE REBASTECIMENTO
                    




            

    except Exception as e:
        print(f"Erro na automação: {str(e)}")
        raise
    finally:
     if driver:
        try:
            print("🛑 Fechando Selenium corretamente...")
            driver.quit()
        except Exception as e:
            print(f"Erro ao fechar o navegador: {e}")

            # Aguarde um pouco antes de matar os processos (garante que Selenium teve tempo para encerrar)
            time.sleep(2)

            matar_processos_navegador()  # Agora, só mata processos se necessário

        if controle:
            controle.automacao_ativa = False

def matar_processos_navegador():
    processos = ["chromedriver.exe", "geckodriver"]
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        if proc.info["name"] in processos:
            try:
                os.kill(proc.info["pid"], signal.SIGTERM)
                # Use stderr para garantir que a saída não dependa de sys.stdout
                sys.stderr.write(f"✅ Processo {proc.info['name']} encerrado.\n")
            except Exception as e:
                sys.stderr.write(f"⚠️ Erro ao encerrar {proc.info['name']}: {e}\n")

# Mantém compatibilidade com execução direta
# Mantenha a execução direta apenas quando chamado explicitamente
# if __name__ == "__main__":
#     try:
#         if len(sys.argv) < 8:
#             print("Uso correto:")
#             print("python criar_pedido.py <usuario> <senha> <pasta> <data> <observacao> <relatorio> <arquivo> [paciente]")
#             sys.exit(1)
            
#         main(
#             usuario=sys.argv[1],
#             senha=sys.argv[2],
#             pasta=sys.argv[3],
#             data=sys.argv[4],
#             observacao=sys.argv[5],
#             nome_relatorio=sys.argv[6],
#             nome_arquivo=sys.argv[7],
#             nome_paciente=sys.argv[8] if len(sys.argv) > 8 else "#ignorate#"
#         )
#     except Exception as e:
#         print(f"Erro fatal: {str(e)}")
#         sys.exit(1)