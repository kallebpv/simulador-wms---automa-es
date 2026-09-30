from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from funcaos import (
    localizar_e_clicar_elemento,
    localizar_e_preencher,
    localizar_e_selecionar_por_visibilidade,
    preencher_campo,
    clicar_com_js,
    localizar_e_preencher_2,
    preencher_com_tabs,
    colar_texto_formatado,
    colar_via_javascript,
    preencher_com_tabs_seguro,
    obter_texto_por_id,
    imprimir_pdf_win32,
    imprimir_pdf_com_sumatra,
    localizar_pdf_por_numero
)
from funcaos import iniciar_chrome_demo  # [SIMULADOR]
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from selenium.webdriver.support.ui import WebDriverWait
import sys
import os
import psutil
import signal
import codecs
import glob
import subprocess
import win32api
import win32print

# [SIMULADOR] Endereço do simulador FluxoWMS (no lugar do endereço do sistema real).
URL_SIMULADOR = "http://localhost:8080/"
# [SIMULADOR] Na demonstração a impressão é só simulada (não gasta papel). Troque para True
# para mandar a picking list para a impressora de verdade, como no robô original.
IMPRIMIR_DE_VERDADE = False
# [SIMULADOR] True abre o PDF baixado na tela (bom para mostrar a picking list no vídeo).
ABRIR_PDF_NA_DEMO = False

if hasattr(sys.stdout, "detach"):
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
if hasattr(sys.stderr, "detach"):
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


def main(usuario, senha, controle=None):
    """
    Executa a automação de avanço de pedido.

    Parâmetros:
        usuario (str): login do sistema.
        senha (str): senha do sistema.
        controle (objeto opcional): deve ter os métodos:
            - obter_numero_pedido() -> str ou None (None interrompe)
            - perguntar_continuar() -> bool (True continua, False interrompe)
            - parar_solicitada() -> bool (True se o usuário pediu para parar)
    """
    driver = None
    caminho_atual = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    chrome_driver_path = os.path.join(caminho_atual, "chromedriver.exe")

    if not os.path.exists(chrome_driver_path):
        print("ℹ️ chromedriver.exe ausente; usando o driver baixado automaticamente pelo Selenium.")  # [SIMULADOR]
        # raise FileNotFoundError("chromedriver.exe ausente em " + chrome_driver_path)  # [SIMULADOR] deixou de ser obrigatório

    try:
        driver = iniciar_chrome_demo(chrome_driver_path)  # [SIMULADOR] opções de gravação + driver automático
        print("✅ ChromeDriver iniciado com sucesso!")
    except Exception as e:
        print(f"🚨 Erro ao iniciar o ChromeDriver: {str(e)}")
        raise

    try:
        ac = ActionChains(driver)
        wait = WebDriverWait(driver, 5)

        # ---------- LOGIN E NAVEGAÇÃO INICIAL ----------
        driver.get(URL_SIMULADOR)  # [SIMULADOR]
        print("Navegador aberto.")

        localizar_e_clicar_elemento(driver, "//a[contains(text(),'Entrar')]",
                                    msg_sucesso='Entrou com sucesso.', msg_falha='Falhou no início tentar entrar.')

        localizar_e_preencher(driver, "//input[@name='data[Usuario][login]']", usuario,
                              msg_sucesso="Usuário preenchido.", msg_falha="Erro ao preencher usuário.")

        localizar_e_preencher(driver, "//input[@name='data[Usuario][senha]']", senha,
                              msg_sucesso='senha sucesso', msg_falha='senha falha')

        localizar_e_clicar_elemento(driver, "//input[@type='submit' and @value='Login']",
                                    msg_sucesso="Botão de login clicado.", msg_falha="Erro ao clicar no botão de login.")

        localizar_e_clicar_elemento(driver, "//div[contains(@class, 'link-modulo') and contains(@link, '/Homes/index/wms')]",
                                    msg_sucesso='Botão WMS clicado com sucesso', msg_falha='Falha ao clicar no botão WMS')

        localizar_e_clicar_elemento(driver, "//span[contains(@class, 'menu-anchor-opendata')]",
                                    msg_sucesso='aba esquerda clicada com sucesso', msg_falha='falha ao clicar aba esquerda')

        localizar_e_clicar_elemento(driver, "//a[contains(@class, 'list-group-item') and contains(text(), 'WMS')]",
                                    msg_sucesso='wms da aba esquerda encontrado', msg_falha='falha ao encontrar wms da aba esquerda')

        localizar_e_clicar_elemento(driver, "//a[contains(@class, 'list-group-item') and contains(text(), 'Saida')]",
                                    msg_sucesso='Saída clicada na aba esquerda com sucesso.')

        localizar_e_clicar_elemento(driver, "//a[contains(@class, 'list-group-item') and contains(text(), 'Pedidos')]",
                                    msg_sucesso='Botão Pedidos da aba esquerda clicado com sucesso', msg_falha='Falha ao clicar no botão Pedidos da aba esquerda.')

        localizar_e_clicar_elemento(driver, '//*[@id="closeMenuOpendata"]/span',
                                    msg_sucesso='Aba esquerda fechada com sucesso.', msg_falha='Falha ao tentar Fechar aba esquerda')

        # ---------- LOOP PRINCIPAL PERSISTENTE ----------
        # Enquanto a automação estiver ativa, o navegador NÃO FECHA
        while controle and controle.automacao_ativa:
            try:
                # Verifica se o usuário pediu para parar
                if hasattr(controle, 'parar_solicitada') and controle.parar_solicitada():
                    print("🛑 Parada solicitada pelo usuário.")
                    break

                # 1) Obter número do pedido (bloqueante - aguarda entrada do usuário)
                if controle and hasattr(controle, 'obter_numero_pedido'):
                    numero_pedido = controle.obter_numero_pedido()
                else:
                    # fallback para linha de comando
                    numero_pedido = input("Digite o número do pedido (ou 'sair' para encerrar): ").strip()
                    if numero_pedido.lower() == 'sair':
                        break

                # Se o usuário cancelou ou fechou o pop-up
                if numero_pedido is None or numero_pedido.strip() == '':
                    print("Número vazio ou cancelado. Aguardando próximo pedido...")
                    time.sleep(0.5)  # Pequena pausa para não sobrecarregar
                    continue  # Volta para o início do while

                # Verifica novamente se a automação ainda está ativa
                if not controle.automacao_ativa:
                    break

                # 2) Executar ações para este pedido
                print(f"📦 Processando pedido: {numero_pedido}")

            # 2) Executar ações para este pedido
            
                # CLICAR EM PESQUISAR (expande o filtro)
                localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div/div/h4/a',
                                            tempo_inicial=0,
                                            msg_sucesso='Botão PESQUISAR clicado com sucesso',
                                            msg_falha='Falha ao tentar clicar em botão PESQUISAR')

                # Preencher número do pedido
                localizar_e_preencher(driver, '//*[@id="filtro_nnumero_ped"]', text=numero_pedido,
                                      tempo_inicial=0,
                                      msg_sucesso='Número do pedido preenchido com sucesso',
                                      msg_falha='Falha ao preencher número do pedido')

                # Filtrar
                localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div/form/div[2]/div/div[2]/fieldset[5]/div/div/div/button',
                                            tempo_inicial=0,
                                            msg_sucesso='Botão FILTRAR clicado com sucesso',
                                            msg_falha='Falha ao tentar clicar em botão FILTRAR')

                # CLICAR NO MENU DO PEDIDO
                localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/table/tbody/tr[4]/td[12]/div/span',
                                            tempo_inicial=0,
                                            msg_sucesso='Botão MENU clicado com sucesso',
                                            msg_falha='Falha ao tentar clicar em botão MENU')

                # SOLICITAR APROVAÇÃO
                localizar_e_clicar_elemento(driver, '//*[@id="table_results"]/tbody/tr[4]/td[12]/div/ul/li[6]/a',
                                            tempo_inicial=0,
                                            msg_sucesso='Botão SOLICITAR APROVACAO clicado com sucesso',
                                            msg_falha='Falha ao tentar clicar em botão SOLICITAR APROVACAO')

                # OK da solicitação
                localizar_e_clicar_elemento(driver, '/html/body/div[16]/div[3]/div/button[2]/span',
                                            tempo_inicial=0,
                                            msg_sucesso='Botão OK DE SOLICITAR APROVACAO clicado com sucesso',
                                            msg_falha='Falha ao tentar clicar em botão OK DE SOLICITAR APROVACAO')

                # MENU novamente
                localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/table/tbody/tr[4]/td[12]/div/span',
                                            tempo_inicial=0,
                                            msg_sucesso='Botão MENU clicado com sucesso',
                                            msg_falha='Falha ao tentar clicar em botão MENU')

                # CRIAR WSAIDA
                localizar_e_clicar_elemento(driver, '//*[@id="table_results"]/tbody/tr[4]/td[12]/div/ul/li[8]/a',
                                            tempo_inicial=0,
                                            msg_sucesso='Botão CRIAR WSAIDA clicado com sucesso',
                                            msg_falha='Falha ao tentar clicar em botão CRIAR WSAIDA')

                # OK criar wsaida
                localizar_e_clicar_elemento(driver, '/html/body/div[16]/div[3]/div/button[2]/span',
                                            tempo_inicial=0,
                                            msg_sucesso='Botão OK DE CRIAR WSAIDA clicado com sucesso',
                                            msg_falha='Falha ao tentar clicar em botão OK DE CRIAR WSAIDA')

                # Verificar percentual de atendimento
                elemento = driver.find_element(By.XPATH, '//*[@id="conteudo_gerenciarwsaida"]/div[5]/div/div[1]')
                texto_status = elemento.text
                match = re.search(r"\((\d+)%\)", texto_status)
                percentual = 0
                if match:
                    percentual = int(match.group(1))
                    print(f"Percentual de atendimento: {percentual}%")
                else:
                    print("Não foi possível extrair o percentual.")

                # Se atendimento incompleto, não executa ações adicionais
                if int(percentual) == 100:
                    print("Atendimento completo – executando as demais ações.")

                    # Botão para criar WSAIDA
                    localizar_e_clicar_elemento(driver, '//*[@id="criar_wsaida"]',
                                                tempo_inicial=0,
                                                msg_sucesso='Botão PARA CRIAR WSAIDA clicado com sucesso',
                                                msg_falha='Falha ao tentar clicar em botão PARA CRIAR WSAIDA')

                    # Copiar código
                    codigo = obter_texto_por_id(driver, ID='lbl_random',
                                                msg_sucesso='sucesso ao copiar codigo de aprovacao de CRIAR A WSAIDA',
                                                msg_falha='falha ao copiar codigo de aprovacao de CRIAR A WSAIDA')

                    # Preencher campo com o código
                    localizar_e_preencher(driver, '//input[@id="txt_random"]', text=codigo,
                                          tempo_inicial=0,
                                          msg_sucesso='sucesso ao preencher código de CRIAR A WSAIDA',
                                          msg_falha='falha ao preencher código de CRIAR A WSAIDA')

                    # OK
                    localizar_e_clicar_elemento(driver, '/html/body/div[15]/div[3]/div/button[2]/span',
                                                tempo_inicial=0,
                                                msg_sucesso='Botão OK PARA CRIAR A WSAIDA clicado com sucesso',
                                                msg_falha='Falha ao tentar clicar em botão OK PARA CRIAR A WSAIDA')
 
                    # O elemento contém APENAS o número (ex: "268109")
                    elemento_numero = driver.find_element(By.XPATH, '//*[@id="collapseHeader"]/div/div[1]/div[2]/div')
                    numero_wsaida = elemento_numero.text.strip()
    
                    if numero_wsaida and numero_wsaida.isdigit():
                        print(f"📄 WSaída número: {numero_wsaida}")
                    else:
                        print(f"⚠️ Número da WSaída não é numérico: '{numero_wsaida}'")
                        numero_wsaida = None        

                if numero_wsaida: 

                    # Voltar
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/a',
                                                tempo_inicial=0,
                                                msg_sucesso='Botão VOLTAR PARA SAIR DA WSAIDA clicado com sucesso',
                                                msg_falha='Falha ao tentar clicar em botão VOLTAR PARA SAIR DA WSAIDA')

                    # Menu
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/table/tbody/tr[4]/td[12]/div/span',
                                                tempo_inicial=0,
                                                msg_sucesso='Botão MENU clicado com sucesso',
                                                msg_falha='Falha ao tentar clicar em botão MENU')

                    # INICIAR SEPARACAO
                    localizar_e_clicar_elemento(driver, '/html/body/div[4]/div[2]/div[3]/table/tbody/tr[4]/td[12]/div/ul/li[6]/a',
                                                tempo_inicial=0,
                                                msg_sucesso='Botão INICIAR SEPARACAO clicado com sucesso',
                                                msg_falha='Falha ao tentar clicar em botão INICIAR SEPARACAO')

                    # OK
                    localizar_e_clicar_elemento(driver, '/html/body/div[16]/div[3]/div/button[2]/span',
                                                tempo_inicial=0,
                                                msg_sucesso='Botão OK DE INICIAR SEPARACAO clicado com sucesso',
                                                msg_falha='Falha ao tentar clicar em botão OK DE INICIAR SEPARACAO')
                    # BOTÃO IMPRESSORA
                    localizar_e_clicar_elemento(driver, '//*[@id="table_results"]/tbody/tr[4]/td[13]/div/span',
                                                tempo_inicial=0,
                                                msg_sucesso='Botão IMPRESSORA clicado com sucesso',
                                                msg_falha='Falha ao tentar clicar em botão IMPRESSORA')
                    # BOTÃO PICKING LIST TOTAL
                    localizar_e_clicar_elemento(driver, '//*[@id="table_results"]/tbody/tr[4]/td[13]/div/ul/li[4]/a',
                                                tempo_inicial=0,
                                                msg_sucesso='Botão PICKING LIST TOTAL clicado com sucesso',
                                                msg_falha='Falha ao tentar clicar em botão PICKING LIST TOTAL')
                    # BOTÃO RELATORIO PDF
                    localizar_e_clicar_elemento(driver, '//*[@id="PDF"]',
                                                tempo_inicial=0,
                                                msg_sucesso='Botão RELATORIO PDF clicado com sucesso',
                                                msg_falha='Falha ao tentar clicar em botão RELATORIO PDF')


                    # --- LOCALIZAR E IMPRIMIR O PDF (Espera Dinâmica) ---
                    print("⏳ Iniciando download e aguardando conclusão...")
                    pasta_download = os.path.expanduser("~/Downloads")  # ou caminho fixo
                
                    tempo_maximo = 30  # Espera no máximo 30 segundos
                    tempo_decorrido = 0
                    pdf_path = None

                    while tempo_decorrido < tempo_maximo:
                        # Verifica se o Chrome ainda está baixando o arquivo (existência do .crdownload)
                        arquivos_temp = glob.glob(os.path.join(pasta_download, f"*{numero_wsaida}*.crdownload"))
                    
                        # Tenta localizar o PDF final
                        pdf_path = localizar_pdf_por_numero(pasta_download, numero_wsaida)

                        # Condição de sucesso: PDF existe e não há mais arquivos .crdownload
                        if pdf_path and len(arquivos_temp) == 0:
                            print("✅ Download concluído com sucesso!")
                            break
                    
                        # Pausa de 1 segundo antes de checar novamente
                        time.sleep(1)
                        tempo_decorrido += 1

                    # Executa a impressão se o arquivo foi encontrado no tempo hábil
                    if pdf_path:
                        print(f"📄 ARQUIVO LOCALIZADO PARA IMPRIMIR: {os.path.basename(pdf_path)}")
                    
                        # Define a impressora (pode vir de um parâmetro ou interface)
                        impressora = getattr(controle, 'impressora', "Nome da Impressora Padrão")
                    
                        # Tenta imprimir (use um dos dois métodos)
                        if not IMPRIMIR_DE_VERDADE:  # [SIMULADOR] impressão simulada na demonstração
                            print(f"🖨️ [DEMO] Picking list enviada para a impressora '{impressora}' (impressão simulada).")  # [SIMULADOR]
                            if ABRIR_PDF_NA_DEMO:  # [SIMULADOR]
                                os.startfile(pdf_path)  # [SIMULADOR]
                        elif not imprimir_pdf_com_sumatra(pdf_path, impressora):
                            # Fallback para win32api
                            imprimir_pdf_win32(pdf_path, impressora)
                else:
                    print("⚠️ Falha: O download não foi concluído dentro do tempo limite ou o arquivo não foi encontrado.")



            except Exception as e:
                print(f"❌ Erro ao processar pedido {numero_pedido}: {str(e)}")
                # Você pode optar por continuar ou interromper
                # Se quiser interromper, descomente a linha abaixo:
                # raise

            # 3) Perguntar se deseja continuar
            if controle and hasattr(controle, 'perguntar_continuar'):
                continuar = controle.perguntar_continuar()
            else:
                resp = input("Deseja processar outro pedido? (s/n): ").strip().lower()
                continuar = (resp == 's' or resp == 'sim')
            if not continuar:
                print("Encerrando loop.")
                break

        # Fim do loop

    except Exception as e:
        print(f"Erro na automação: {str(e)}")
        raise
    finally:
        if not (controle and controle.automacao_ativa):
            if driver:
                driver.quit()
        else:
            print("🔵 Navegador mantido aberto (automação ativa).")


def matar_processos_navegador():
    """Função auxiliar para matar processos do ChromeDriver (mantida compatibilidade)."""
    processos = ["chromedriver.exe", "geckodriver"]
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        if proc.info["name"] in processos:
            try:
                os.kill(proc.info["pid"], signal.SIGTERM)
                sys.stderr.write(f"✅ Processo {proc.info['name']} encerrado.\n")
            except Exception as e:
                sys.stderr.write(f"⚠️ Erro ao encerrar {proc.info['name']}: {e}\n")