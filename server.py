import socket, threading, time

# declarando IP e porta para o servidor
HOST = '127.0.0.1'
PORT = 50000

conexoes = []
mensagens = []

# criando servidor com ipv4 e protocolo TCP 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# define IP e porta em que o servidor vai escutar
s.bind((HOST, PORT))


'''
ESSAS FUNÇÕES SEMPRE VÃO MANDAR MENSAGEM PARA TODOS OS USUÁRIOS!
'''

def enviar_mensagem_individual(conexao):
    print(f'[ENVIANDO] Enviando mensagens para {conexao['addr']}')
    for i in range(conexao['last'], len(mensagens)):
        mensagem_envio = 'msg=' + mensagens[i]
        conexao['addr'].send(mensagem_envio)
        conexao['last'] = i + 1

        # evita mandar as mensagens mais rápido do que recebe
        time.sleep(0.2)

def enviar_mensagem_todos(conn):
    global conexoes
    for conexao in conexoes:
        enviar_mensagem_individual(conexao)

def handle_clientes(conn, addr):
    print(f'[NOVA CONEXÃO] Um novo usuário se conectou pelo endereço {addr}!')
    global conexoes
    global mensagens
    nome = False

    while True:
        # espera mensagem do cliente
        msg = conn.recv(2048).decode('utf-8')
        if msg:
            # se for a primeira mensagem do usuário
            if msg.startswith('nome='):
                msg_separada = msg.split('=') 
                nome = msg_separada[1] # pega o nome que foi informado

                # salva informações da conexão criada
                dicionario_conexao = {
                    "conn": conn,
                    "addr": addr,
                    "nome": nome,
                    "last": 0
                }

                # adiciona na lista de conexões (global) -> colocar algum lock?
                conexoes.append(dicionario_conexao)
                enviar_mensagem_individual(dicionario_conexao)

            elif msg.startswith('msg='):
                msg_separada = msg.split("=")
                mensagem = msg_separada[1]
                mensagens.append(mensagem)
                enviar_mensagem_todos(conn)

def start():
    print('[INICIANDO] Iniciando socket...')
    s.listen() 

    while True:
        # aguarda até alguém conectar
        # quando acontece a conexão, salva o retorno da função, que é a conexão e o endereço que foi conectado
        conn, addr = s.accept()

        # cria uma thread toda vez que entrar uma nova conexã
        # a thread criada vai chamar a função handle_clientes com os parâmetros conn e addr
        thread = threading.Thread(target=handle_clientes, args=(conn, addr))
        thread.start()
