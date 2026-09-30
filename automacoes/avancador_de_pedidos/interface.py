import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
import queue
from avancar_pedido import main as executar_automacao

class ControleAvancar:
    """Classe para comunicação entre interface e thread da automação."""
    def __init__(self, interface):
        self.interface = interface
        self.automacao_ativa = False
        self.parar_flag = False

    def obter_numero_pedido(self):
        """Exibe janela para digitar o número do pedido."""
        if not self.automacao_ativa:
            return None
        # Usa a fila para pedir à interface que mostre o diálogo
        # Como será chamado na thread da automação, precisamos usar a fila
        # para esperar a resposta da interface.
        self.interface.queue.put(("pedir_numero", None))
        # Aguarda a resposta em uma fila interna
        try:
            numero = self.interface.numero_pedido_queue.get(timeout=None)
            return numero
        except:
            return None

    def perguntar_continuar(self):
        """Pergunta se deseja processar outro pedido."""
        if not self.automacao_ativa:
            return False
        self.interface.queue.put(("perguntar_continuar", None))
        try:
            resposta = self.interface.continuar_queue.get(timeout=None)
            return resposta
        except:
            return False

    def parar_solicitada(self):
        """Verifica se o usuário pediu para parar."""
        return self.parar_flag


class InterfaceAvancar:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Automação - Avançar Pedido")
        self.root.geometry("400x300")
        self.queue = queue.Queue()
        self.numero_pedido_queue = queue.Queue()
        self.continuar_queue = queue.Queue()

        self.automacao_ativa = False
        self.thread = None
        self.controle = ControleAvancar(self)

        self.criar_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_janela)
        self.root.after(100, self.processar_fila)

    def criar_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Campos
        tk.Label(main_frame, text="Usuário *").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_usuario = tk.Entry(main_frame, width=30)
        self.entry_usuario.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(main_frame, text="Senha *").grid(row=1, column=0, sticky='w', pady=5)
        self.entry_senha = tk.Entry(main_frame, width=30, show="*")
        self.entry_senha.grid(row=1, column=1, padx=5, pady=5)

        # Botões
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        self.btn_iniciar = tk.Button(btn_frame, text="Iniciar Automação", command=self.iniciar_automacao)
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)

        self.btn_parar = tk.Button(btn_frame, text="Parar", command=self.parar_automacao, state=tk.DISABLED)
        self.btn_parar.pack(side=tk.LEFT, padx=5)

        # Status
        self.label_status = tk.Label(main_frame, text="Aguardando início...", fg="blue")
        self.label_status.grid(row=3, column=0, columnspan=2, pady=10)

        #impressora
        tk.Label(main_frame, text="Impressora (nome exato) *").grid(row=3, column=0, sticky='w', pady=5)
        self.entry_impressora = tk.Entry(main_frame, width=35)
        self.entry_impressora.grid(row=3, column=1, padx=5, pady=5)
        self.entry_impressora.insert(0, "Minha Impressora")  # valor padrão

        # [SIMULADOR] Credenciais fictícias já preenchidas para a demonstração.
        self.entry_usuario.insert(0, "usuario_demo")
        self.entry_senha.insert(0, "demo123")

    def iniciar_automacao(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()
        if not usuario or not senha:
            messagebox.showerror("Erro", "Usuário e senha são obrigatórios.")
            return

        self.automacao_ativa = True
        self.controle.automacao_ativa = True
        self.controle.parar_flag = False
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_parar.config(state=tk.NORMAL)
        self.label_status.config(text="Automação em execução...", fg="green")

        # Inicia a thread
        self.thread = threading.Thread(
            target=self.executar_automacao_thread,
            args=(usuario, senha),
            daemon=True
        )
        self.thread.start()

        impressora = self.entry_impressora.get().strip()
        # Armazena no controle
        self.controle.impressora = impressora

    def executar_automacao_thread(self, usuario, senha):
        try:
            executar_automacao(usuario, senha, controle=self.controle)
        except Exception as e:
            self.queue.put(("erro", f"Erro na automação: {str(e)}"))
        finally:
            self.queue.put(("finalizado", None))

    def parar_automacao(self):
        if self.automacao_ativa:
            self.controle.parar_flag = True
            self.label_status.config(text="Parando...", fg="orange")
            self.btn_parar.config(state=tk.DISABLED)

    def processar_fila(self):
        try:
            while True:
                msg, valor = self.queue.get_nowait()
                if msg == "pedir_numero":
                    # Mostra diálogo para digitar o número
                    numero = simpledialog.askstring(
                        "Número do Pedido",
                        "Digite o número do pedido para processar:",
                        parent=self.root
                    )
                    self.numero_pedido_queue.put(numero)
                elif msg == "perguntar_continuar":
                    resposta = messagebox.askyesno(
                        "Continuar?",
                        "Deseja processar outro pedido?",
                        parent=self.root
                    )
                    self.continuar_queue.put(resposta)
                elif msg == "erro":
                    messagebox.showerror("Erro", valor)
                    self.finalizar_automacao()
                elif msg == "finalizado":
                    self.finalizar_automacao()
        except queue.Empty:
            pass
        self.root.after(100, self.processar_fila)

    def finalizar_automacao(self):
        self.automacao_ativa = False
        self.controle.automacao_ativa = False
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_parar.config(state=tk.DISABLED)
        self.label_status.config(text="Automação finalizada.", fg="blue")

    def fechar_janela(self):
        if self.automacao_ativa:
            if messagebox.askyesno("Confirmação", "Deseja realmente sair? A automação será interrompida."):
                self.parar_automacao()
                if self.thread and self.thread.is_alive():
                    self.thread.join(timeout=3)
            self.root.destroy()
        else:
            self.root.destroy()




if __name__ == "__main__":
    app = InterfaceAvancar()
    app.root.mainloop()