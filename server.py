import socket, threading, time

# declarando IP e porta para o servidor
HOST = '127.0.0.1'
PORT = 50005


# Estruturas globais
conexoes = []  # clientes conectados
mensagens = []  # msg globais
 
usuarios = {}   # nome -> conexão
grupos = {}     # grupo -> membros

lock = threading.Lock()   # evita concorrência entre threads

# criando servidor com ipv4 e protocolo TCP 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# define IP e porta em que o servidor vai escutar
s.bind((HOST, PORT))


'''
ESSAS FUNÇÕES SEMPRE VÃO MANDAR MENSAGEM PARA TODOS OS USUÁRIOS!
'''

# refatorar
def enviar_mensagem_individual(conexao):
    print(f"[ENVIANDO] Enviando mensagens para {conexao['addr']}")
    for i in range(conexao['last'], len(mensagens)):
        mensagem_envio = 'AQUI=' + mensagens[i]
        conexao['conn'].send(mensagem_envio.encode())
        conexao['last'] = i + 1

        # evita mandar as mensagens mais rápido do que recebe
        time.sleep(0.2)

def enviar_mensagem_todos(conn):
    global conexoes
    for conexao in conexoes:
        enviar_mensagem_individual(conexao)

def enviar_mensagem_grupo(grupo, remetente, texto):
    membros = grupos[grupo]
    for membro in membros:
        if membro in usuarios:
            usuarios[membro].send(f'GRUPO={grupo}={remetente}: {texto}'.encode())

def enviar_mensagem_privada(destinatario, remetente, texto):
    if destinatario in usuarios:
        usuarios[destinatario].send(f'PRIVADO={remetente}: {texto}'.encode())
        usuarios[remetente].send(f'PRIVADO=Você para {destinatario}: {texto}'.encode())
    else:
        usuarios[remetente].send(f'SISTEMA=Usuário {destinatario} não está online'.encode())

#  Cada cliente conectado ganha uma thread executando essa função
def handle_clientes(conn, addr):
    print(f'[NOVA CONEXÃO] Um novo usuário se conectou pelo endereço {addr}!')
    global conexoes
    global mensagens
    nome = False

    while True:
        # espera mensagem do cliente
        try:
            msg = conn.recv(2048).decode('utf-8')
            if not msg:
                remover_usuario(nome, conn)
                break
        except:
            remover_usuario(nome, conn)
            break

        if msg:
            # se for a primeira mensagem do usuário
            if msg.startswith('nome='):
                msg_separada = msg.split('=') 
                nome = msg_separada[1] # pega o nome que foi informado
                
                # Usa lock para evitar condição de corrida
                with lock:
                    # Valida nomes (nome deve ser único)
                    if nome in usuarios:
                        print(f"Nome duplicado detectado: {nome}")
                        conn.send("ERRO=Nome já está em uso, digite outro nome!".encode())
                        continue
                    
                    # Salva usuários na lista de usuários
                    usuarios[nome] = conn

                    # Envia ok confirmando cadastro
                    conn.send("OK=NOME".encode())

                    # salva informações da conexão criada
                    dicionario_conexao = {
                        "conn": conn,
                        "addr": addr,
                        "nome": nome,
                        "last": 0
                    }

                    # adiciona na lista de conexões (global)
                    conexoes.append(dicionario_conexao)
                    print(f'[LOGIN] {nome} conectado')

                enviar_mensagem_individual(dicionario_conexao)

            # Enviar msg 
            elif msg.startswith('msg='):
                msg_separada = msg.split("=")
                mensagem = nome + '=' + msg_separada[1]
                mensagens.append(mensagem)
                enviar_mensagem_todos(conn)
            
            # Criar grupo
            elif msg.startswith('criar_grupo='):
                nome_grupo = msg.split('=')[1]

                with lock:
                    if nome_grupo in grupos:
                        conn.send(f'SISTEMA=Grupo {nome_grupo} já existe'.encode())

                    else:
                        grupos[nome_grupo] = []
                        grupos[nome_grupo].append(nome)
                        conn.send(f'SISTEMA=Grupo {nome_grupo} criado e você entrou nele'.encode())

                        print(f'[GRUPO] Criado: {nome_grupo}')   

            # Entrar em grupo
            elif msg.startswith('entrar_grupo='):
                nome_grupo = msg.split('=')[1]

                with lock:
                    if nome_grupo not in grupos:
                        conn.send(f'SISTEMA=Grupo não existe'.encode())

                    elif nome not in grupos[nome_grupo]:
                        grupos[nome_grupo].append(nome)
                        conn.send(f'SISTEMA=Entrou em {nome_grupo}'.encode())

                        print( f'[GRUPO] {nome} entrou em {nome_grupo}')

            # Enviar mensagem grupo
            elif msg.startswith('grupo_msg='):
                conteudo = msg.split('=', 1)[1]
                grupo, texto = conteudo.split('|', 1)

                if grupo not in grupos:
                    conn.send(f'SISTEMA=Grupo não existe'.encode())

                elif nome not in grupos[grupo]:
                    conn.send(f'SISTEMA=Você não participa desse grupo'.encode())

                else:
                    enviar_mensagem_grupo(grupo,nome,texto)
                    print(f'[MSG GRUPO] {nome} -> {grupo}')

            # Enviar mensagem privada
            elif msg.startswith('privado_msg='):
                conteudo = msg.split('=', 1)[1]

                if '|' not in conteudo:
                    conn.send('SISTEMA=Uso correto: /privado nome mensagem'.encode())
                    continue

                destinatario, texto = conteudo.split('|', 1)

                if destinatario == nome:
                    conn.send('SISTEMA=Você não pode enviar mensagem privada para você mesmo'.encode())

                else:
                    enviar_mensagem_privada(destinatario, nome, texto)
                    print(f'[MSG PRIVADA] {nome} -> {destinatario}')

            # Listar grupos
            elif msg.startswith('listar_grupos='):
                with lock:
                    if len(grupos) == 0:
                        conn.send('SISTEMA=Nenhum grupo criado ainda'.encode())
                    else:
                        lista_grupos = ', '.join(grupos.keys())
                        conn.send(f'SISTEMA=Grupos disponíveis: {lista_grupos}'.encode())

            # Listar usuários online
            elif msg.startswith('listar_usuarios='):
                with lock:
                    if len(usuarios) == 0:
                        conn.send('SISTEMA=Nenhum usuário online'.encode())
                    else:
                        lista_usuarios = ', '.join(usuarios.keys())
                        conn.send(f'SISTEMA=Usuários online: {lista_usuarios}'.encode())

            # Sair do grupo
            elif msg.startswith('sair_grupo='):
                nome_grupo = msg.split('=')[1]

                with lock:
                    if nome_grupo in grupos:
                        if nome in grupos[nome_grupo]:
                            grupos[nome_grupo].remove(nome)
                            conn.send(f'SISTEMA=Saiu de {nome_grupo}'.encode())

                            print(f'[GRUPO] {nome} saiu de {nome_grupo}')
            

# Desconexões
def remover_usuario(nome, conn):
    global conexoes
    global usuarios
    global grupos

    with lock:
        if nome in usuarios:
            del usuarios[nome]

        conexoes = [c for c in conexoes if c["conn"] != conn]

        for grupo in grupos.values():
            if nome in grupo:
                grupo.remove(nome)

    print(f'[DESCONECTADO] {nome}')


def start():
    print('[INICIANDO] Iniciando socket...')
    s.listen() 

    while True:
        # aguarda até alguém conectar
        # quando acontece a conexão, salva o retorno da função, que é a conexão e o endereço que foi conectado
        conn, addr = s.accept()

        # cria uma thread toda vez que entrar uma nova conexão
        # a thread criada vai chamar a função handle_clientes com os parâmetros conn e addr
        thread = threading.Thread(target=handle_clientes, args=(conn, addr))
        thread.start()

start()