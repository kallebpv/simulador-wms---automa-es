from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time 
import pyperclip
import os  # [SIMULADOR]

# [SIMULADOR] ----------------------------------------------------------------
# Ritmo da demonstração (para gravar vídeo). Pode ser trocado no rodar.bat.
#   VELOCIDADE_DEMO  = 1.0 -> ritmo original do robô; 2.0 -> pausas pela metade; 0.5 -> pausas em dobro
#   PAUSA_EXTRA_DEMO = segundos somados antes de cada ação (deixa cada passo visível no vídeo)
VELOCIDADE_DEMO = float(os.environ.get("VELOCIDADE_DEMO", "1.0"))
PAUSA_EXTRA_DEMO = float(os.environ.get("PAUSA_EXTRA_DEMO", "0"))


def opcoes_chrome_demo():
    """[SIMULADOR] Chrome pronto para gravação: sem a faixa de 'software automatizado',
    sem pop-up de senha, janela maximizada, downloads direto na pasta Downloads e um
    perfil próprio da demonstração (o simulador lembra os pedidos entre um robô e outro)."""
    from selenium import webdriver
    opcoes = webdriver.ChromeOptions()
    opcoes.add_experimental_option("excludeSwitches", ["enable-automation"])
    opcoes.add_argument("--start-maximized")
    pasta_perfil = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_perfil_chrome_demo")
    opcoes.add_argument(f"--user-data-dir={pasta_perfil}")
    opcoes.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
        "download.default_directory": os.path.join(os.path.expanduser("~"), "Downloads"),
        "download.prompt_for_download": False,
        "profile.default_content_setting_values.automatic_downloads": 1,
    })
    return opcoes


def iniciar_chrome_demo(chrome_driver_path):
    """[SIMULADOR] Usa o chromedriver.exe da pasta, se existir e for compatível; senão o
    Selenium baixa sozinho o driver certo para o Chrome instalado (Selenium Manager)."""
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    if os.path.exists(chrome_driver_path):
        try:
            return webdriver.Chrome(service=Service(chrome_driver_path), options=opcoes_chrome_demo())
        except Exception as e:
            print(f"⚠️ chromedriver.exe da pasta não funcionou ({e.__class__.__name__}); usando o driver automático.")
    return webdriver.Chrome(options=opcoes_chrome_demo())
# [SIMULADOR] ----------------------------------------------------------------



def localizar_e_clicar_elemento(driver, xpath, tempo_inicial=2, msg_sucesso="", msg_falha=""):
    """
    Localiza e clica em um elemento usando XPath com tempos de espera progressivos.
    
    Parâmetros:
      driver         : Instância do Selenium WebDriver.
      xpath          : XPath relativo do elemento a ser localizado.
      tempo_inicial  : Tempo de espera inicial (em segundos). (default=3)
      
    Lógica:
      - Tenta localizar o elemento aguardando 'tempo_inicial' segundos.
      - Se não encontrar, tenta novamente aguardando 5 segundos.
      - Se não encontrar, tenta novamente aguardando 30 segundos.
      - Se ainda não localizar, recarrega a página e aguarda 40 segundos.
      - Se o elemento for encontrado em qualquer tentativa, rola até ele, clica nele e retorna True.
      - Se não for encontrado após todas as tentativas, retorna False.
    """
    tempos = [tempo_inicial, 5, 30]
    time.sleep((tempo_inicial + PAUSA_EXTRA_DEMO) / VELOCIDADE_DEMO)  # [SIMULADOR] ritmo da demo

    for t in tempos:
        try:
            element = WebDriverWait(driver, t).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
            if msg_sucesso: print(msg_sucesso)
            return True
        except Exception as e:
            print(f"Erro: {e}")
            pass

    driver.refresh()
    try:
        element = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()
        if msg_sucesso: print(msg_sucesso)
        return True
    except Exception as e:
        print(f"Erro: {e}")
        if msg_falha: print(msg_falha)
        return False

def localizar_e_preencher(driver, xpath, text, tempo_inicial=2, msg_sucesso="", msg_falha=""):
    """
    Localiza um elemento e preenche com o texto fornecido, utilizando tempos de espera progressivos.
    
    Parâmetros:
      driver         : Instância do Selenium WebDriver.
      xpath          : XPath relativo do elemento a ser localizado.
      text           : Texto a ser inserido no elemento.
      tempo_inicial  : Tempo de espera inicial (em segundos). (default=3)
      
    Lógica:
      - Tenta localizar o elemento aguardando 'tempo_inicial' segundos.
      - Se não encontrar, tenta novamente aguardando 5 segundos.
      - Se não encontrar, tenta novamente aguardando 30 segundos.
      - Se ainda não localizar, recarrega a página e aguarda 40 segundos.
      - Se o elemento for encontrado em qualquer tentativa, rola até ele, limpa o campo (se necessário),
        preenche com o texto e retorna True.
      - Se não for encontrado após todas as tentativas, retorna False.
    """
    tempos = [tempo_inicial, 5, 30]
    time.sleep((tempo_inicial + PAUSA_EXTRA_DEMO) / VELOCIDADE_DEMO)  # [SIMULADOR] ritmo da demo

    for t in tempos:
        try:
            element = WebDriverWait(driver, t).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView();", element)
            element.clear()
            element.send_keys(text)
            if msg_sucesso: print(msg_sucesso)
            return True
        except Exception as e:
            print(f"Erro: {e}")
            pass

    driver.refresh()
    try:
        element = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)
        element.clear()
        element.send_keys(text)
        if msg_sucesso: print(msg_sucesso)
        return True
    except Exception as e:
        print(f"Erro: {e}")
        if msg_falha: print(msg_falha)
        return False

def clicar_botao(driver, xpath, tempo_inicial=2, msg_sucesso="", msg_falha=""):
    """
    Localiza e clica em um botão usando XPath com tempos de espera progressivos.
    
    Parâmetros:
      driver         : Instância do Selenium WebDriver.
      xpath          : XPath relativo do botão a ser clicado.
      tempo_inicial  : Tempo de espera inicial (em segundos). (default=3)
      
    Lógica:
      - Tenta localizar e clicar no botão aguardando 'tempo_inicial' segundos.
      - Se não encontrar, tenta novamente com 5 segundos.
      - Se ainda não encontrar, tenta com 30 segundos.
      - Se após essas tentativas o botão não for localizado, recarrega a página e espera 40 segundos.
      - Retorna True se o botão foi clicado; caso contrário, retorna False.
    """
    tempos = [tempo_inicial, 5, 30]
    time.sleep((tempo_inicial + PAUSA_EXTRA_DEMO) / VELOCIDADE_DEMO)  # [SIMULADOR] ritmo da demo

    for t in tempos:
        try:
            botao = WebDriverWait(driver, t).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView();", botao)
            botao.click()
            if msg_sucesso: print(msg_sucesso)
            return True
        except Exception as e:
            print(f"Erro: {e}")
            pass

    driver.refresh()
    try:
        botao = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView();", botao)
        botao.click()
        if msg_sucesso: print(msg_sucesso)
        return True
    except Exception as e:
        print(f"Erro: {e}")
        if msg_falha: print(msg_falha)
        return False

#OUTRA FUNÇÃO
def localizar_e_selecionar_por_visibilidade(driver, xpath, visible_text, tempo_inicial=2, msg_sucesso="", msg_falha=""):
    """
    Localiza um elemento <select> e seleciona uma opção pelo texto visível usando tempos de espera progressivos.
    
    Parâmetros:
      driver         : Instância do Selenium WebDriver.
      xpath          : XPath relativo do elemento <select> a ser localizado.
      visible_text   : Texto visível da opção que se deseja selecionar.
      tempo_inicial  : Tempo de espera inicial (em segundos). (default=3)
      msg_sucesso    : Mensagem a ser exibida se a seleção for bem-sucedida.
      msg_falha      : Mensagem a ser exibida se a seleção falhar após todas as tentativas.
      
    Lógica:
      - Tenta localizar o elemento aguardando 'tempo_inicial' segundos.
      - Se não encontrar, tenta novamente aguardando 5 segundos.
      - Se não encontrar, tenta novamente aguardando 30 segundos.
      - Se ainda não localizar, recarrega a página e aguarda 40 segundos.
      - Se o elemento for encontrado em qualquer tentativa, rola até ele, 
        utiliza o objeto Select para selecionar a opção pelo texto visível e retorna True.
      - Se não for encontrado após todas as tentativas, retorna False.
    """
    tempos = [tempo_inicial, 5, 30]
    time.sleep((tempo_inicial + PAUSA_EXTRA_DEMO) / VELOCIDADE_DEMO)  # [SIMULADOR] ritmo da demo
    
    for t in tempos:
        try:
            element = WebDriverWait(driver, t).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView();", element)
            select = Select(element)
            select.select_by_visible_text(visible_text)
            if msg_sucesso:
                print(msg_sucesso)
            return True
        except Exception as e:
            print(f"Erro: {e}")
            pass
    
    driver.refresh()
    try:
        element = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)
        select = Select(element)
        select.select_by_visible_text(visible_text)
        if msg_sucesso:
            print(msg_sucesso)
        return True
    except Exception as e:
        print(f"Erro: {e}")
        if msg_falha:
            print(msg_falha)
        return False
#OUTRA FUNÇÃO
def preencher_campo(driver, xpath, texto, tempo=5, msg_sucesso="", msg_falha=""):
    """
    Preenche um campo de input localizado por XPath com o texto desejado.
    
    Parâmetros:
      driver       : Instância do Selenium WebDriver.
      xpath        : XPath relativo do elemento input.
      texto        : Texto a ser inserido no campo.
      tempo        : Tempo máximo para aguardar o elemento estar visível (default=10 segundos).
      msg_sucesso  : Mensagem opcional exibida em caso de sucesso.
      msg_falha    : Mensagem opcional exibida em caso de falha.
      
    Lógica:
      - Aguarda o campo estar visível.
      - Limpa o conteúdo existente.
      - Envia o novo texto.
      - Retorna True se a operação for bem-sucedida; caso contrário, retorna False.
    """
    try:
        campo = WebDriverWait(driver, tempo).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        # Se necessário, pode clicar no campo somente se não estiver focado.
        # Exemplo:
        # if campo != driver.switch_to.active_element:
        #     campo.click()
        campo.clear()
        campo.send_keys(texto)
        if msg_sucesso:
            print(msg_sucesso)
        return True
    except Exception as e:
        print(f"Erro: {e}")
        if msg_falha:
            print(msg_falha)
        return False

def clicar_com_js(driver, xpath):
    element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    driver.execute_script("arguments[0].click();", element)

def fechar_overlay_se_existir(driver):
    try:
        overlay = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ui-widget-overlay"))
        )
        driver.execute_script("arguments[0].remove();", overlay)
    except:
        pass



def localizar_e_preencher_2(driver, xpath, text, tempo_inicial=2, msg_sucesso="", msg_falha=""):
    """
    Versão 4.0 - Correções:
    1. Tratamento de exceções específicas
    2. Uso de `element_to_be_clickable` para evitar overlays
    3. Remoção do TAB para prevenir mudança de foco
    """
    try:
        # Espera pelo elemento estar clicável (não apenas presente)
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.clear()

        # Método 1: Inserção via JavaScript (evita TAB/ENTER)
        try:
            texto_js = text.replace('\t', ';')  # Processa o texto ANTES
            driver.execute_script(f"arguments[0].value = `{texto_js}`;", element)
            if msg_sucesso: 
                print(msg_sucesso)
            return True

        # Fallback para send_keys se o JavaScript falhar
        except WebDriverException:
            for linha in text.split('\n'):
                if '\t' in linha:
                    codigo, quantidade = linha.split('\t')
                    element.send_keys(f"{codigo};{quantidade}")  # Usa ";" como separador
                else:
                    element.send_keys(linha)
            if msg_sucesso: 
                print(msg_sucesso)
            return True

    except TimeoutException:
        print(f"{msg_falha}: Elemento não encontrado em 20s (XPath: {xpath})")
        return False
    except NoSuchElementException:
        print(f"{msg_falha}: Elemento não existe (XPath: {xpath})")
        return False
    except Exception as e:
        print(f"{msg_falha}: Erro inesperado - {str(e)}")
        return False

def preencher_com_tabs(driver, xpath, dados, msg_sucesso="", msg_falha=""):
    """
    Versão 2.0 - Com tratamento de erros e mensagens
    Preenche campo com TABs literais preservando formato: "7498    30"
    """
    try:
        # Localizar campo e garantir que está visível
        campo = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        campo.clear()
        
        # Converter lista de dados para string com quebras de linha
        texto_formatado = "\n".join(dados)
        
        # Preencher usando send_keys direto
        campo.send_keys(texto_formatado)
        
        # Mensagem de sucesso se fornecida
        if msg_sucesso:
            print(f"\033[92m{msg_sucesso}\033[0m")  # Texto verde
        return True

    except TimeoutException:
        erro = f"Timeout: Campo não encontrado em 20s (XPath: {xpath})"
    except NoSuchElementException:
        erro = f"Elemento não existe (XPath: {xpath})"
    except Exception as e:
        erro = f"Erro inesperado: {str(e)}"

    # Mensagem de falha personalizada ou padrão
    if msg_falha:
        print(f"\033[91m{msg_falha}\033[0m")  # Texto vermelho
    else:
        print(f"\033[91m{erro}\033[0m")
    
    return False
def colar_texto_formatado(driver, xpath_campo, dados, msg_sucesso="", msg_falha=""):
    """
    Simula colagem (Ctrl+V) de texto formatado com TABs e quebras de linha.
    
    Parâmetros:
      driver: Instância do WebDriver
      xpath_campo: XPath do campo de texto
      dados: Lista de strings no formato ["COD\tQTD", ...]
      msg_sucesso: Mensagem de sucesso (opcional)
      msg_falha: Mensagem de falha (opcional)
    """
    try:
        # Formatar os dados
        texto_para_colar = "\n".join(dados)
        pyperclip.copy(texto_para_colar)  # Copia para a área de transferência

        # Localizar o campo
        campo = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, xpath_campo))
        )
        campo.clear()

        # Colar o texto
        campo.send_keys(Keys.CONTROL + 'v')  # Ctrl+V
        
        if msg_sucesso:
            print(f"\033[92m{msg_sucesso}\033[0m")
        return True

    except Exception as e:
        if msg_falha:
            print(f"\033[91m{msg_falha}\033[0m")
        print(f"Erro detalhado: {str(e)}")
        return False
    
def colar_via_javascript(driver, xpath_campo, texto):
    try:
        campo = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath_campo))
        )
        driver.execute_script(f"""
            arguments[0].value = `{texto}`;
        """, campo)
        print("✅ Texto inserido via JavaScript!")
        return True
    except Exception as e:
        print(f"❌ Erro no JavaScript: {str(e)}")

def preencher_com_tabs_seguro(driver, xpath_campo, texto, msg_sucesso="", msg_falha=""):
    """
    Preenche o campo com TABs literais via JavaScript, sem mudar o foco.
    Formato esperado: "7498\t30\n7644\t60"
    """
    try:
        # Localizar o campo
        campo = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath_campo))
        )
        
        # Usar JavaScript para definir o valor (TABs como texto)
        driver.execute_script(f"""
            arguments[0].value = `{texto}`;
        """, campo)
        
        if msg_sucesso:
            print(f" {msg_sucesso}")
        return True

    except Exception as e:
        if msg_falha:
            print(f" {msg_falha}")
        print(f"Erro detalhado: {str(e)}")
        return False



