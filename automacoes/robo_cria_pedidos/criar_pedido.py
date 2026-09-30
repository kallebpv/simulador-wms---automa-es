from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from funcaos import localizar_e_clicar_elemento, localizar_e_preencher, localizar_e_selecionar_por_visibilidade, preencher_campo, clicar_com_js, localizar_e_preencher_2, preencher_com_tabs, colar_texto_formatado, colar_via_javascript, preencher_com_tabs_seguro
from funcaos import iniciar_chrome_demo  # [SIMULADOR]
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from funcaoLerPlanilha import processar_planilha
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
        'data': kwargs['data'],
        'observacao': kwargs['observacao'],
        'nome_relatorio': kwargs['nome_relatorio'],
        'nome_arquivo': kwargs['nome_arquivo'],
        'nome_paciente': kwargs.get('nome_paciente', '#ignorate#')
    }

    # Processamento principal
    caminho_relatorio = os.path.join(params['pasta_caminho'], params['nome_relatorio'])
    caminho_arquivo_txt = os.path.join(params['pasta_caminho'], params['nome_arquivo'])



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
            planilha_de_pacientes = processar_planilha(caminho_relatorio, params['nome_paciente'])
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
            #CLICAR NO BOTÃO PEDIDOS NA ABA ESQUERDA.
            localizar_e_clicar_elemento(driver,"//a[contains(@class, 'list-group-item') and contains(text(), 'Pedidos')]",\
                                        msg_sucesso='Botão Pedidos da aba esquerda clicado com sucesso', msg_falha='Falha ao clicar no botão Pedidos da aba esquerda.')
            #CLICAR NO 'X' DE FECHAR A ABA ESQUERDA.
            localizar_e_clicar_elemento(driver,'//*[@id="closeMenuOpendata"]/span',\
                                        msg_sucesso='Aba esquerda fechada com sucesso.',msg_falha='Falha ao tentar Fechar aba esquerda')
            for paciente in planilha_de_pacientes:
                 # Antes de cada ação, verificar se a automação foi parada
                if controle and controle.automacao_ativa:
                    print("Automação rodando...")
                    if not kwargs.get('automacao_ativa', True):  # Verifica estado
                        print("Automação interrompida pelo usuário")
                        break
                    with open(caminho_arquivo_txt, "a", encoding="utf-8", errors='ignore') as arquivo_txt:
                    # ALERTANDO QUE INICIOU UM PACIENTE
                        arquivo_txt.write(f"INICIANDO: {paciente['paciente']}\n")
                        arquivo_txt.write(f"{paciente['itens']}\n\n")
                    #CLICAR EM CRIAR PEDIDO
                    localizar_e_clicar_elemento(driver, '//*[@id="dropdownCadastrarPedido"]',\
                                                msg_sucesso= 'Botão criar pedido clicado com sucesso', msg_falha='Falha ao tentar clicar em botão criar pedido')
                    #CLICAR EM NORMAL
                    localizar_e_clicar_elemento(driver,'//*[@id="accordion"]/div/div[1]/ul/li[1]/a',\
                                                msg_sucesso='BOTÃO NORMAL CLICADO COM SUCESSO', msg_falha='Falha ao tentar clicar em botão normal')
                    
                    
                    #CLICAR NA SELEÇÃO TIPO DE SAÍDA.
                    #USAR SETA PARA BAIXO, PARA PARAR EM SAÍDA PADRÃO
                    localizar_e_selecionar_por_visibilidade(driver, '//*[@id="id_tipo_movimento"]','SAÍDA PADRÃO',\
                                                            msg_sucesso='Sucesso ao selecionar SAÍDA PADRÃO', msg_falha='Sucesso ao selecionar SAÍDA PADRÃO')


                    #CLICAR EM PROJETO
                    #USAR SETAR PARA BAIXO ATÉ PARAR EM PROJETO ESPECIAL.  [SIMULADOR] nome fictício
                    localizar_e_selecionar_por_visibilidade(driver,'//*[@id="cod_wcliproj"]','PROJETO ESPECIAL',\
                                                            msg_sucesso='Sucesso ao selecionar PROJETO ESPECIAL',msg_falha='Sucesso ao selecionar PROJETO ESPECIAL')  # [SIMULADOR] nome fictício
                    


                    #CLICAR EM LUPA DE DESTINATARIO
                    # PRENCHER DESTINATÁRIO, PREENCHER COM UNIDADE NORTE  [SIMULADOR] nome fictício
                    localizar_e_clicar_elemento(driver,'//*[@id="collapseOne"]/div/div[3]/div[1]/div/span/button',\
                                                msg_sucesso='Sucesso ao clicar em lupa de Destinarário',msg_falha='Sucesso ao clicar em lupa de Destinarário')
                    # PRENCHER DESTINATÁRIO, PREENCHER COM UNIDADE NORTE  [SIMULADOR] nome fictício
                    preencher_campo(driver,'//*[@id="ncod_snome"]','UNIDADE NORTE',  # [SIMULADOR] nome fictício
                                    msg_sucesso='Sucesso ao preencher campo destinatário com a palavra "UNIDADE NORTE"')  # [SIMULADOR] nome fictício
                    #CLICAR EM PESQUISAR, PARA PROCURAR DESTINATARIO
                    localizar_e_clicar_elemento(driver,'/html/body/div[6]/div[2]/div[1]/div/form/div[2]/div/div/div[2]/button',\
                                                msg_sucesso='Sucesso ao pesquisar destinatário',msg_falha='Falha ao tentar pesquisar destinatário')
                    #CLICAR NO DESTINATARIO UNIDADE NORTE  [SIMULADOR] nome fictício
                    localizar_e_clicar_elemento(driver,'//*[@id="lista_itens_encontrados"]/div/table/tbody/tr/td[4]/button',\
                                                msg_sucesso='Sucesso ao clicar no destanarito unidade norte',msg_falha='Falha ao clicar no destinatario Unidade Norte')  # [SIMULADOR] nome fictício
                    
                    
                    #SELECIONAR PRIORIDADE
                    localizar_e_selecionar_por_visibilidade(driver,'//*[@id="nprioridade_ped"]','0',\
                                                            msg_sucesso='Sucesso ao selecionar prioridade Zero',msg_falha='Falha ao selecionar prioridade Zero')


                    #CLICAR E PRENCHER DATA(DE ACORDO COM A QUE FUTURAMENTE O USUARIO PODERÁ ESCOLHER)
                    localizar_e_preencher(driver,'//*[@id="dtseparacao_ped"]', params['data'],\
                                        msg_sucesso='Sucesso ao preencher data',msg_falha='Falha ao tentar preencher data')
                    #CLICAR NO BOTÃO CRÍTICO.
                    localizar_e_clicar_elemento(driver,'//*[@id="bcritico_ped"]',\
                                                msg_sucesso='Sucesso ao clicar no botão crítico', msg_falha='Falha ao clicar no botão crítico')
                    #CLICAR E PREENCHER MOTIVO CRITICIDADE
                    # [SIMULADOR] nomes reais trocados por fictícios na linha abaixo
                    localizar_e_preencher(driver,'//*[@id="stexto_urgente_ped"]','Demanda Prioritária',\
                                        msg_sucesso='Sucesso ao preencher motivo Criticidade',msg_falha='Falha ao tentar preencher motivo Criticidade')
                    #CLICAR E PREENCHER OBSERVAÇÃO, OBSERVE, SERÁ PRENCHIDO COM A OBSERVAÇÃO DADA FUTURAMENTE PELO O USUÁRIO E O PACIENTE E PROCESSO QUE SÃO DADOS DA PLANILHA.
                    localizar_e_preencher(driver,'//*[@id="mobs_ped"]', params['observacao'] + paciente["paciente"],\
                                        msg_sucesso='Sucesso ao prencher observação.', msg_falha='Falha ao tentar preenhcer observação.')
                    #CLICAR EM IMPORTAR CSV
                    localizar_e_clicar_elemento(driver,'//*[@id="importarProdutosCSV"]',\
                                                msg_sucesso='Sucesso ao clicar em importar CSV',msg_falha='Falha ao clicar em importar CSV')
                    #CLICAR EM OK(O CLIENTE NÃO PODE SER MAIS MODIFICADO)
                    localizar_e_clicar_elemento(driver,'/html/body/div[16]/div[3]/div/button[2]/span',\
                                                msg_sucesso='Sucesso ao clicar OK depois de clicar em em importar CSV',msg_falha='Falha ao clicar OK depois de clicar em em importar CSV')
                    #CLICAR E PRENCHER A PARTE DE INSERÇÃO DE PRODUTOS DE QUANTIDADES.
                    preencher_com_tabs_seguro(driver,'//*[@id="produtos"]',paciente["numeracao_dos_itens_e_quantidade"],\
                                                msg_sucesso='Sucesso ao inserir Produtos e Quantidades', msg_falha='Falha ao tentar inserir Produtos e Quantidades')
                    #CLICAR EM IMPORTAR PRODUTOS
                    localizar_e_clicar_elemento(driver,'/html/body/div[24]/div[3]/div/button[2]/span',\
                                                msg_sucesso='Sucesso ao importar produtos',msg_falha='Falha ao importar produtos')
                    # Localiza o elemento que contém "Pedido Normal"
                    elemento = driver.find_element(By.XPATH, "//h2[contains(text(), 'Pedido Normal')]")
                    texto_pedido = elemento.text  # Exemplo: "Pedido Normal # 202169808"

                    # Usa expressão regular para extrair somente os dígitos do número do pedido
                    match = re.search(r"Pedido Normal #\s*(\d+)", texto_pedido)
                    if match:
                        numero_pedido = match.group(1)
                        print("Número do pedido:", numero_pedido)
                    else:
                        print("Não foi possível extrair o número do pedido.")
                        numero_pedido = '000'
                    
                    # ALERTANDO QUE FINALIZOU UM PACIENTE
                    with open(caminho_arquivo_txt, "a", encoding="utf-8", errors='ignore') as arquivo_txt:
                        arquivo_txt.write(f"\nFINALIZANDO: {paciente['paciente']}\n")
                        arquivo_txt.write(f"NUMERO DO PEDIDO: {numero_pedido}\n\n")

                    #CLICAR EM VOLTAR FINALIZANDO UM PEDIDO.
                    localizar_e_clicar_elemento(driver,"//a[contains(text(), 'Voltar')]",\
                                                msg_sucesso='Sucesso ao clicar no botão voltar finalizando o pedido de ' + paciente['paciente'], msg_falha='Falha ao tentar clicar no botão voltar finalizando o pedido de ' + paciente['paciente'])

            

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