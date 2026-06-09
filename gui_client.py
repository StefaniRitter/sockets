import socket, threading
import tkinter as tk                     
from tkinter import scrolledtext, ttk

SERVER = '127.0.0.1'
PORT = 50005

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

def enviar(mensagem):
    client.send(mensagem.encode('utf-8'))

# Configura um placeholder fake reutilizável para campos de entrada
def configurar_placeholder(campo, texto_placeholder):
    campo.insert(0, texto_placeholder)
    campo.config(fg="gray")

    def limpar_placeholder(event):
        if campo.cget("fg") in ["gray", "red"]:
            campo.delete(0, tk.END)
            campo.config(fg="black")

    campo.bind("<FocusIn>", limpar_placeholder)
    campo.bind("<Button-1>", limpar_placeholder)

# Exibe uma mensagem de erro dentro do próprio campo
def mostrar_erro_no_input(campo, mensagem):
    campo.delete(0, tk.END)
    campo.insert(0, mensagem)
    campo.config(fg="red")

# Restaura o placeholder após limpar o campo
def restaurar_placeholder(campo, texto_placeholder):
    campo.delete(0, tk.END)
    campo.insert(0, texto_placeholder)
    campo.config(fg="gray")

# Só abre após o login ser aceito
def abrir_janela_chat():
    # Configurações da janela
    janela_chat = tk.Tk()
    janela_chat.title("Chat com Sockets")
    janela_chat.geometry("550x500")
    janela_chat.configure(bg="#f5f7fa")

    # Centralizar a janela na tela
    largura = 550
    altura = 500

    largura_tela = janela_chat.winfo_screenwidth()
    altura_tela = janela_chat.winfo_screenheight()

    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)

    janela_chat.geometry(f"{largura}x{altura}+{x}+{y}")

    # Área de exibição de mensagens
    area_mensagens = scrolledtext.ScrolledText(janela_chat, bg="white")
    area_mensagens.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    area_mensagens.config(state='disabled')

    area_mensagens.config(state='normal')
    area_mensagens.insert(tk.END, "As mensagens do chat aparecerão aqui!\n")
    area_mensagens.config(state='disabled')

    # Campo de entrada de mensagens
    entrada_mensagem = tk.Entry(janela_chat, fg="gray")
    entrada_mensagem.pack(padx=10, pady=5, fill=tk.X)
    configurar_placeholder(entrada_mensagem, "Digite sua mensagem")

    def mostrar_mensagem(texto):
        area_mensagens.config(state='normal')
        area_mensagens.insert(tk.END, texto + "\n")
        area_mensagens.config(state='disabled')
        area_mensagens.see(tk.END)

    def receber_mensagens():
        # Loop para receber mensagens do servidor
        while True:
            try:
                msg = client.recv(2048).decode()

                # Verifica o tipo da mensagem e exibe de forma adequada
                if msg.startswith('SISTEMA='):
                    mostrar_mensagem(msg.split('=', 1)[1])

                elif msg.startswith('GRUPO='):
                    partes = msg.split('=', 2)
                    mostrar_mensagem(f'[{partes[1]}] {partes[2]}')

                elif msg.startswith('PRIVADO='):
                    mostrar_mensagem(f'[privado] {msg.split("=", 1)[1]}')

                elif msg.startswith('ERRO='):
                    mostrar_mensagem(msg.split('=', 1)[1])

                else:
                    msg_tratada = msg.split("=")
                    if len(msg_tratada) >= 3:
                        mostrar_mensagem(f'[geral] {msg_tratada[1]}: {msg_tratada[2]}')

            except Exception as e:
                mostrar_mensagem(f"Erro: {e}")
                break

    def enviar_mensagem():
        # Obtém a mensagem digitada pelo usuário
        msg = entrada_mensagem.get().strip()

        # Envia apenas mensagens não vazias e diferentes do placeholder para o servidor
        if msg and entrada_mensagem.cget("fg") != "gray":
            enviar(f'msg={msg}')

        # Limpa o campo de texto após o envio e restaura o placeholder
        restaurar_placeholder(entrada_mensagem, "Digite sua mensagem")

    # Botão de enviar mensagem, return faz a tecla enter enviar a mensagem também
    botao_enviar = ttk.Button(janela_chat, text="Enviar", command=enviar_mensagem)
    botao_enviar.pack(pady=5)
    entrada_mensagem.bind("<Return>", lambda event: enviar_mensagem())

    # Inicia uma thread para ouvir mensagens do servidor em segundo plano
    thread = threading.Thread(target=receber_mensagens, daemon=True)
    thread.start()

    janela_chat.mainloop()


def abrir_janela_login():
    janela_login = tk.Tk()
    janela_login.title("Login")
    janela_login.resizable(False, False)      # Impede que o usuário redimensione a janela
    janela_login.configure(bg="#f5f7fa")

    largura = 330
    altura = 170

    largura_tela = janela_login.winfo_screenwidth()
    altura_tela = janela_login.winfo_screenheight()

    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)

    janela_login.geometry(f"{largura}x{altura}+{x}+{y}")

    # Frame central para agrupar os elementos da tela de login
    frame_login = tk.Frame(janela_login, bg="#f5f7fa")
    frame_login.pack(expand=True)

    # Título da tela de login
    titulo = tk.Label(
        frame_login,
        text="Chat com Sockets",
        font=("Arial", 14, "bold"),
        bg="#f5f7fa",
        fg="#1f2937"
    )
    titulo.pack(pady=(0, 10))

    # Campo onde o usuário informa o nome antes de entrar no chat
    entrada_nome = tk.Entry(
        frame_login,
        fg="gray",
        font=("Arial", 10),
        justify="center"
    )
    entrada_nome.pack(ipady=4, padx=20, fill=tk.X)
    configurar_placeholder(entrada_nome, "Digite seu nome")

    def fazer_login():
        nome = entrada_nome.get().strip()

        # Impede que placeholders e mensagens de erro sejam enviados como nome
        if nome == "" or nome in [
            "Digite seu nome",
            "Informe um nome",
            "Nome já está em uso, digite outro nome!"
        ]:
            mostrar_erro_no_input(entrada_nome, "Informe um nome")
            return

        enviar(f'nome={nome}')
        resposta = client.recv(2048).decode()

        if resposta.startswith('ERRO='):
            mostrar_erro_no_input(entrada_nome, resposta.split('=', 1)[1])
        else:
            janela_login.destroy()
            abrir_janela_chat()

    botao_entrar = ttk.Button(
        frame_login,
        text="Entrar",
        command=fazer_login
    )
    botao_entrar.pack(pady=(10, 0))

    entrada_nome.bind("<Return>", lambda event: fazer_login())

    janela_login.mainloop()

abrir_janela_login()