import socket, threading

# Configurações de conexão com o servidor
SERVER = '127.0.0.1'
PORT = 50006

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

# Recebe e exibe mensagens enviadas pelo servidor
def handle_mensagens():
    while True:
        try: 
            msg = client.recv(2048).decode()

            # Mensagens do sistema
            if msg.startswith('SISTEMA='):
                print(msg.split('=', 1)[1])

            # Mensagens enviadas em grupos
            elif msg.startswith('GRUPO='):
                partes = msg.split('=', 2)
                print(f'[{partes[1]}] {partes[2]}')

            # Mensagens privadas
            elif msg.startswith('PRIVADO='):
                print(f'[privado] {msg.split("=", 1)[1]}')

            # Mensagens de erro
            elif msg.startswith('ERRO='):
                print(msg.split('=', 1)[1])

            # Mensagens do chat geral
            else:
                msg_tratada = msg.split("=")

                if len(msg_tratada) >= 3:
                    print(f'[geral] {msg_tratada[1]}: {msg_tratada[2]}')

        except Exception as e:
            print(f"Erro: {e}")
            break

# Envia dados para o servidor
def enviar(mensagem):
    client.send(mensagem.encode('utf-8'))

# Captura os comandos digitados pelo usuário
def enviar_mensagem():
    while True:
        msg = input()

        # Criar grupo
        if msg.startswith('/criar '):
            grupo = msg.split(' ', 1)[1]
            enviar(f'criar_grupo={grupo}')

        # Entrar em um grupo
        elif msg.startswith('/entrar '):
            grupo = msg.split(' ', 1)[1]
            enviar(f'entrar_grupo={grupo}')

        # Sair de um grupo
        elif msg.startswith('/sair '):
            grupo = msg.split(' ', 1)[1]
            enviar(f'sair_grupo={grupo}')

        # Enviar mensagem para um grupo
        elif msg.startswith('/grupo '):
            partes = msg.split(' ', 2)

            if len(partes) < 3:
                print('Uso: /grupo nome_grupo mensagem')
                continue

            grupo = partes[1]
            texto = partes[2]

            enviar(f'grupo_msg={grupo}|{texto}')
        
        # Listar membros de um grupo
        elif msg.startswith('/membros '):
            grupo = msg.split(' ', 1)[1].strip()

            if not grupo:
                print('Uso: /membros nome_grupo')
                continue

            enviar(f'listar_membros={grupo}')

        # Listar grupos existentes
        elif msg == '/grupos':
            enviar('listar_grupos=')

        # Enviar mensagem privad
        elif msg.startswith('/privado '):
            partes = msg.split(' ', 2)

            if len(partes) < 3:
                print('Uso: /privado nome_usuario mensagem')
                continue

            destinatario = partes[1]
            texto = partes[2]

            enviar(f'privado_msg={destinatario}|{texto}')
        
        # Listar usuários conectados
        elif msg == '/usuarios':
            enviar('listar_usuarios=')

        # Exibir comandos disponíveis
        elif msg == '/ajuda':
            enviar('ajuda=')
        
        # Enviar mensagem para o chat geral
        else:
            enviar(f'msg={msg}')

        '''
        # Aqui só funcionaria se o usuario enviasse uma mensagem ERRO=..., não é necessário
        elif msg.startswith('ERRO='):
            print(msg.split('=', 1)[1])
        ''' 

# Solicita um nome válido ao usuário antes de entrar no chat
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

# Inicializa o cliente e cria as threads de envio e recebimento
def start():
    validar_nome()
    thread1 = threading.Thread(target=handle_mensagens)
    thread2 = threading.Thread(target=enviar_mensagem)
    thread1.start()
    thread2.start()

start()