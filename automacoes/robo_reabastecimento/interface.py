import tkinter as tk
from tkinter import messagebox, filedialog
import re
from datetime import datetime
from criar_pedido import main as executar_automacao
import threading
import queue
import os
import signal
import psutil
from criar_pedido import matar_processos_navegador

class InterfaceAutomacao:
    
    def __init__(self):
        self.automacao_ativa = False
        self.driver = None  # Controle do navegador
        self.root = tk.Tk()
        self.queue = queue.Queue()  # Fila para comunicação entre threads
        self.campos_obrigatorios = ['usuario', 'senha', 'pasta', 'data do dia criado', 'nome_relatorio', 'data do dia de expedir','data_do_agendamento' ]
        self.criar_widgets()
        self.configurar_janela()
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_janela)
        self.root.after(100, self.processar_fila)  # Verifica a fila periodicamente
        self.preencher_demo()  # [SIMULADOR]

    def configurar_janela(self):
        self.root.title("Interface de Automação")
        self.root.geometry("600x750")
    def parar_automacao(self):  # <--- ADICIONE ESTE MÉTODO
        if self.automacao_ativa:
            self.automacao_ativa = False
            if self.driver:
                self.driver.quit()
            messagebox.showinfo("Info", "Automação interrompida!")
            self.btn_parar.config(state=tk.DISABLED)
        
        
    def criar_widgets(self):
        # Configuração do container principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Criação dos widgets
        self.entry_usuario = tk.Entry(main_frame, width=40)
        self.entry_senha = tk.Entry(main_frame, width=40, show="*")
        self.entry_nome_relatorio = tk.Entry(main_frame, width=40)
        self.entry_nome_arquivo = tk.Entry(main_frame, width=40)
        self.entry_nome_paciente = tk.Entry(main_frame, width=40)

        # Lista de campos
        campos = [
            ("Usuário *", self.entry_usuario),
            ("Senha *", self.entry_senha),
            ("Data de hoje (DD/MM/AAAA) *", self.criar_campo_data_de_hoje(main_frame)),
            ("Caminho da Pasta *", self.criar_campo_pasta(main_frame)),
            ("Data de Expedicao *", self.criar_campo_data_de_expedicao(main_frame)),
            ("Nome do Relatório *", self.entry_nome_relatorio),
            ("Data do Agendamento *", self.criar_campo_data_de_agendamento(main_frame))
        ]

        # Adiciona widgets
        for i, (texto, widget) in enumerate(campos):
            label = tk.Label(main_frame, text=texto, anchor='w')
            label.grid(row=i, column=0, sticky='w', pady=(10, 0))
            if isinstance(widget, tk.Entry):
                widget.grid(row=i, column=1, sticky='ew', pady=(10, 0), padx=(10, 0))
            else:
                widget.grid(row=i, column=1, sticky='w', pady=(10, 0), padx=(10, 0))

        # Botão de iniciar
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=len(campos)+1, columnspan=2, pady=20)
        tk.Button(btn_frame, text="Iniciar Automação", command=self.iniciar_automacao).pack()

        btn_parar = tk.Button(
        btn_frame, 
        text="Parar Automação", 
        command=self.parar_automacao,  # Nome correto do método
        state=tk.DISABLED
)
    
        self.btn_parar = btn_parar  # Guarda referência para controle

        # Configura peso das colunas
        main_frame.columnconfigure(1, weight=1)

    def criar_campo_data_de_hoje(self, parent):
        frame = tk.Frame(parent)
        self.entry_data_de_hoje = tk.Entry(frame, width=15)
        self.entry_data_de_hoje.pack(side=tk.LEFT)
        
        # Configuração de validação
        val_cmd = (parent.register(self.validar_data), '%P', '%V')
        self.entry_data_de_hoje.configure(
            validate="key",
            validatecommand=val_cmd
        )
        self.entry_data_de_hoje.bind("<FocusIn>", self.limpar_placeholder_data_de_hoje)
        self.entry_data_de_hoje.bind("<FocusOut>", self.verificar_data_de_hoje)
        self.entry_data_de_hoje.insert(0, "DD/MM/AAAA")
        self.entry_data_de_hoje.configure(foreground='grey')
        return frame
    
    def criar_campo_data_de_expedicao(self, parent):
        frame = tk.Frame(parent)
        self.entry_data_de_expedicao = tk.Entry(frame, width=15)
        self.entry_data_de_expedicao.pack(side=tk.LEFT)
        
        # Configuração de validação
        val_cmd = (parent.register(self.validar_data), '%P', '%V')
        self.entry_data_de_expedicao.configure(
            validate="key",
            validatecommand=val_cmd
        )
        self.entry_data_de_expedicao.bind("<FocusIn>", self.limpar_placeholder_data_de_expedicao)
        self.entry_data_de_expedicao.bind("<FocusOut>", self.verificar_data_de_expedicao)
        self.entry_data_de_expedicao.insert(0, "DD/MM/AAAA")
        self.entry_data_de_expedicao.configure(foreground='grey')
        return frame 
    def criar_campo_data_de_agendamento(self, parent):
        frame = tk.Frame(parent)
        self.entry_data_de_agendamento = tk.Entry(frame, width=15)
        self.entry_data_de_agendamento.pack(side=tk.LEFT)
        
        # Configuração de validação
        val_cmd = (parent.register(self.validar_data), '%P', '%V')
        self.entry_data_de_agendamento.configure(
            validate="key",
            validatecommand=val_cmd
        )
        self.entry_data_de_agendamento.bind("<FocusIn>", self.limpar_placeholder_data_de_agendamento)
        self.entry_data_de_agendamento.bind("<FocusOut>", self.verificar_data_de_agendamento)
        self.entry_data_de_agendamento.insert(0, "DD/MM/AAAA")
        self.entry_data_de_agendamento.configure(foreground='grey')
        return frame     

    def criar_campo_pasta(self, parent):
        frame = tk.Frame(parent)
        self.entry_pasta = tk.Entry(frame, width=30)
        self.entry_pasta.pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(frame, text="📁", command=self.escolher_pasta).pack(side=tk.LEFT)
        return frame

    def validar_data(self, texto, motivo):
        if motivo == 'focusout':
            return True
            
        if texto == "DD/MM/AAAA":
            return True
            
        padrao = r"^(\d{0,2}/?\d{0,2}/?\d{0,4})$"
        if re.fullmatch(padrao, texto):
            partes = texto.split('/')
            if len(partes[0]) == 2 and len(texto) in [2,5]:
                return texto + '/'
            return True
        return False

    def limpar_placeholder_data_de_hoje(self, event):
        if self.entry_data_de_hoje.get() == "DD/MM/AAAA":
            self.entry_data_de_hoje.delete(0, tk.END)
            self.entry_data_de_hoje.configure(foreground='black')

    def verificar_data_de_hoje(self, event):
        if not self.entry_data_de_hoje.get():
            self.entry_data_de_hoje.insert(0, "DD/MM/AAAA")
            self.entry_data_de_hoje.configure(foreground='grey')
            
    def limpar_placeholder_data_de_expedicao(self, event):
        if self.entry_data_de_expedicao.get() == "DD/MM/AAAA":
            self.entry_data_de_expedicao.delete(0, tk.END)
            self.entry_data_de_expedicao.configure(foreground='black')

    def verificar_data_de_expedicao(self, event):
        if not self.entry_data_de_expedicao.get():
            self.entry_data_de_expedicao.insert(0, "DD/MM/AAAA")
            self.entry_data_de_expedicao.configure(foreground='grey')

    def limpar_placeholder_data_de_agendamento(self, event):
        if self.entry_data_de_agendamento.get() == "DD/MM/AAAA":
            self.entry_data_de_agendamento.delete(0, tk.END)
            self.entry_data_de_agendamento.configure(foreground='black')

    def verificar_data_de_agendamento(self, event):
        if not self.entry_data_de_agendamento.get():
            self.entry_data_de_agendamento.insert(0, "DD/MM/AAAA")
            self.entry_data_de_agendamento.configure(foreground='grey')

    def validar_data_real(self, data_str):
        try:
            datetime.strptime(data_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def iniciar_automacao(self):
        dados = self.obter_dados()
        erros = []
        
        # Valida campos obrigatórios
        for campo in self.campos_obrigatorios:
            if not dados[campo].strip():
                erros.append(f"Campo '{campo.replace('_', ' ').title()}' é obrigatório")
                
        # Validações específicas
        if dados['data_do_agendamento'] not in ["", "DD/MM/AAAA"] and not self.validar_data_real(dados['data_do_agendamento']):
            erros.append("Data do dia criado inválida ou formato incorreto (DD/MM/AAAA)")
            
        if dados['data do dia criado'] not in ["", "DD/MM/AAAA"] and not self.validar_data_real(dados['data do dia criado']):
            erros.append("Data do dia criado inválida ou formato incorreto (DD/MM/AAAA)")

        if dados['data do dia de expedir'] not in ["", "DD/MM/AAAA"] and not self.validar_data_real(dados['data do dia de expedir']):
           erros.append("Data do dia criado inválida ou formato incorreto (DD/MM/AAAA)")
            
        if erros:
            messagebox.showerror("Erros de Validação", "\n".join(erros))
            return
        # Inicia a automação em uma thread separada
        self.automacao_ativa = True
        self.btn_parar.config(state=tk.NORMAL)
    
    # Cria e inicia a thread
        threading.Thread(
        target=self.executar_automacao_thread,
        args=(dados,),
        daemon=True
        ).start()
            
    def executar_automacao_thread(self, dados):
        try:
            executar_automacao(controle=self, **dados)  # Chamada indireta via interface
        except Exception as e:
            self.queue.put(("erro", f"Erro na automação: {str(e)}"))
    def processar_fila(self):
        try:
         while True:
            tipo, conteudo = self.queue.get_nowait()
            if tipo == "erro":
                messagebox.showerror("Erro", conteudo)
            elif tipo == "atualizar_botoes":
                self.btn_parar.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.root.after(100, self.processar_fila)  # Reagenda a verificação

    def obter_dados(self):
        return {
            'usuario': self.entry_usuario.get(),
            'senha': self.entry_senha.get(),
            'pasta': self.entry_pasta.get(),
            'data do dia criado': self.entry_data_de_hoje.get(),
            'data do dia de expedir': self.entry_data_de_expedicao.get(),
            'nome_relatorio': self.entry_nome_relatorio.get(),
            'data_do_agendamento': self.entry_data_de_agendamento.get()
        }

    def escolher_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.entry_pasta.delete(0, tk.END)
            self.entry_pasta.insert(0, pasta)

    def abrir_janela_parar(self):
        janela_parar = tk.Toplevel(self.root)
        janela_parar.title("Controle")
        janela_parar.geometry("300x100")
        tk.Label(janela_parar, text="Automação em execução").pack(pady=10)
        tk.Button(janela_parar, text="Parar", command=self.parar_automacao).pack()
    def fechar_janela(self):
        """Garante que a automação e todos os processos são encerrados ao fechar."""
        if self.automacao_ativa:
            if messagebox.askyesno("Confirmação", "Deseja realmente sair? A automação será interrompida."):
                self.parar_automacao()

        self.root.quit()  # Encerra a interface Tkinter
        self.root.destroy()  # Remove a janela principal


    # Na função parar_automacao:
    def parar_automacao(self):
        if self.automacao_ativa:
            self.automacao_ativa = False
            if self.driver:
                try:
                    self.driver.quit()  # Fecha o navegador
                except Exception as e:
                    print(f"Erro ao fechar navegador: {e}")
            matar_processos_navegador()  # Função já existente

    # [SIMULADOR] ------------------------------------------------------------
    def preencher_demo(self):
        """[SIMULADOR] Deixa os campos já preenchidos com os dados fictícios da demonstração."""
        import glob
        from datetime import timedelta
        pasta_demo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_exemplo")
        def data(dias):
            return (datetime.now() + timedelta(days=dias)).strftime("%d/%m/%Y")
        def colocar(entry, valor):
            entry.delete(0, tk.END)
            entry.insert(0, valor)
            entry.configure(foreground='black')
        def planilha_mais_recente(padrao):
            arquivos = sorted(glob.glob(os.path.join(pasta_demo, padrao)), key=os.path.getmtime)
            return os.path.basename(arquivos[-1]) if arquivos else ""
        colocar(self.entry_usuario, "usuario_demo")
        colocar(self.entry_senha, "demo123")
        colocar(self.entry_pasta, pasta_demo)
        colocar(self.entry_data_de_hoje, data(0))
        colocar(self.entry_data_de_expedicao, data(1))
        colocar(self.entry_nome_relatorio, planilha_mais_recente("PLANILHA_DESCONTO_*.xlsx"))
        colocar(self.entry_data_de_agendamento, data(2))
    # [SIMULADOR] ------------------------------------------------------------

if __name__ == "__main__":
    app = InterfaceAutomacao()
    app.root.mainloop()