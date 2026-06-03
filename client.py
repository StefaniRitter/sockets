import socket, threading, time

SERVER = '127.0.0.1'
PORT = 50005

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

def handle_mensagens():
    while True:
        msg = client.recv(2048).decode()
        msg_tratada = msg.split("=")
        print(f'{msg_tratada[1]}: {msg_tratada[2]}')

def enviar(mensagem):
    client.send(mensagem.encode('utf-8'))


def enviar_mensagem():
    while True:
        msg = input()
        enviar(f'msg={msg}')

def enviar_nome():
    nome = input('Digite seu nome: ')
    enviar(f'nome={nome}')

def iniciar_envio():
    enviar_nome()
    enviar_mensagem()

def start():
    thread1 = threading.Thread(target=handle_mensagens)
    thread2 = threading.Thread(target=iniciar_envio)
    thread1.start()
    thread2.start()



start()