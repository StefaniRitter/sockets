import socket, threading, time

SERVER = '127.0.0.1'
PORT = 50005

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

def handle_mensagens():
    while True:
        try: 
            msg = client.recv(2048).decode()

            if msg.startswith('SISTEMA='):
                print(msg.split('=', 1)[1])

            elif msg.startswith('GRUPO='):
                partes = msg.split('=', 2)
                print(f'[{partes[1]}] {partes[2]}')

            elif msg.startswith('PRIVADO='):
                print(f'[privado] {msg.split("=", 1)[1]}')

            elif msg.startswith('ERRO='):
                print(msg.split('=', 1)[1])

            else:
                msg_tratada = msg.split("=")

                if len(msg_tratada) >= 3:
                    print(f'[geral] {msg_tratada[1]}: {msg_tratada[2]}')

        except Exception as e:
            print(f"Erro: {e}")
            break

def enviar(mensagem):
    client.send(mensagem.encode('utf-8'))

def enviar_mensagem():
    while True:
        msg = input()

        if msg.startswith('/criar '):
            grupo = msg.split(' ', 1)[1]
            enviar(f'criar_grupo={grupo}')

        elif msg.startswith('/entrar '):
            grupo = msg.split(' ', 1)[1]
            enviar(f'entrar_grupo={grupo}')

        elif msg.startswith('/sair '):
            grupo = msg.split(' ', 1)[1]
            enviar(f'sair_grupo={grupo}')

        elif msg.startswith('/grupo '):
            partes = msg.split(' ', 2)

            if len(partes) < 3:
                print('Uso: /grupo nome_grupo mensagem')
                continue

            grupo = partes[1]
            texto = partes[2]

            enviar(f'grupo_msg={grupo}|{texto}')
        
        elif msg == '/grupos':
            enviar('listar_grupos=')

        elif msg.startswith('/privado '):
            partes = msg.split(' ', 2)

            if len(partes) < 3:
                print('Uso: /privado nome_usuario mensagem')
                continue

            destinatario = partes[1]
            texto = partes[2]

            enviar(f'privado_msg={destinatario}|{texto}')
        
        elif msg == '/usuarios':
            enviar('listar_usuarios=')

        elif msg.startswith('ERRO='):
            print(msg.split('=', 1)[1])

        else:
            enviar(f'msg={msg}')

def validar_nome():
    while True:
        nome = input('Digite seu nome: ')
        enviar(f'nome={nome}')
        resposta = client.recv(2048).decode()

        if resposta.startswith('ERRO='):
            print(resposta.split('=', 1)[1])
        else:
            print('Nome aceito!')
            return

def start():
    validar_nome()
    thread1 = threading.Thread(target=handle_mensagens)
    thread2 = threading.Thread(target=enviar_mensagem)
    thread1.start()
    thread2.start()

start()