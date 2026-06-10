import socket
import threading
import os
import sys

# IP e porta para o client
SERVER = '127.0.0.1'
PORT = 50005

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((SERVER, PORT))
except Exception as e:
    print(f"[ERRO] Não foi possível conectar ao servidor: {e}")
    sys.exit(1)

# Função para escutar e processar mensagens recebidas do servidor
def handle_mensagens():
    while True:
        try:
            msg = client.recv(2048).decode('utf-8')
            if not msg:
                print("\n[SISTEMA] O servidor encerrou a conexão.")
                os._exit(0)

            if msg.startswith('SISTEMA='):
                print(msg.split('=', 1)[1])

            elif msg.startswith('GRUPO='):
                partes = msg.split('=', 2)
                print(f'[{partes[1]}] {partes[2]}')

            elif msg.startswith('PRIVADO='):
                print(f'[privado] {msg.split("=", 1)[1]}')

            elif msg.startswith('GERAL='):
                partes = msg.split('=', 2)
                print(f'[geral] {partes[1]}: {partes[2]}')
                
            elif msg.startswith('ERRO='):
                print(msg.split('=', 1)[1])

        except (socket.error, ConnectionResetError):
            print("\n[SISTEMA] Conexão perdida com o servidor.")
            os._exit(0)
        except Exception:
            break

# Função auxiliar para o envio de mensagens codificadas ao servidor
def enviar(mensagem):
    try:
        client.send(mensagem.encode('utf-8'))
    except OSError:
        print("[SISTEMA] Falha ao enviar dados, conexão perdida.")
        os._exit(0)

# Função para gerenciar loop de entrada do usuário e processamento de comandos
def enviar_mensagem():
    print("Digite /ajuda para ver os comandos.")
    while True:
        try:
            msg = input()
        except (EOFError, KeyboardInterrupt):
            break

        if not msg.strip():
            continue

        if msg.startswith('/'):
            partes = msg.split(' ', 2)
            comando = partes[0].lower()

            if comando == '/criar' and len(partes) >= 2:
                enviar(f'criar_grupo={partes[1].strip()}')

            elif comando == '/entrar' and len(partes) >= 2:
                enviar(f'entrar_grupo={partes[1].strip()}')

            elif comando == '/sair_grupo' and len(partes) >= 2:
                enviar(f'sair_grupo={partes[1].strip()}')

            elif comando == '/grupo' and len(partes) >= 3:
                enviar(f'grupo_msg={partes[1].strip()}|{partes[2].strip()}')

            elif comando == '/membros' and len(partes) >= 2:
                enviar(f'listar_membros={partes[1].strip()}')

            elif comando == '/privado' and len(partes) >= 3:
                enviar(f'privado_msg={partes[1].strip()}|{partes[2].strip()}')

            elif comando == '/grupos':
                enviar('listar_grupos=')

            elif comando == '/usuarios':
                enviar('listar_usuarios=')

            elif comando == '/ajuda':
                enviar('ajuda=')

            else:
                print('[SISTEMA] Comando inválido ou parâmetros insuficientes. Digite /ajuda')
        else:
            enviar(f'msg={msg}')

# Autenticação do usuário antes de liberar o chat
def validar_nome():
    while True:
        try:
            nome = input('Digite seu nome: ').strip()
            if not nome:
                print("O nome não pode ser vazio.")
                continue
            
            enviar(f'nome={nome}')
            resposta = client.recv(2048).decode('utf-8')

            if resposta == 'OK=NOME':
                print(f"[SUCESSO] Bem-vindo ao chat, {nome}!")
                break
            elif resposta.startswith('ERRO='):
                print(resposta.split('=', 1)[1])
            else:
                print("[SISTEMA] Resposta inesperada do servidor.")
        except (socket.error, ConnectionResetError):
            print("[SISTEMA] Erro de comunicação durante a autenticação.")
            os._exit(1)


if __name__ == '__main__':

    validar_nome()

    # Inicia a thread para receber mensagens em segundo plano, sem bloquear a entrada do usuário
    thread_receber = threading.Thread(target=handle_mensagens, daemon=True)
    thread_receber.start()
    enviar_mensagem()