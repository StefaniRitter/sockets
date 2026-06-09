import socket, threading, time, json, os

# arquivo utilizado para persistência dos dados
ARQUIVO_DADOS = 'dados.json'

# declarando IP e porta para o servidor
HOST = '127.0.0.1'
PORT = 50005

# Estruturas globais
conexoes = []  # clientes conectados
mensagens = []  # msg globais

usuarios = {}        # nome -> {"status": "online/offline"}
usuarios_online = {} # nome -> conexão
grupos = {}     # grupo -> membros

lock = threading.Lock()   # evita concorrência entre threads

# criando servidor com ipv4 e protocolo TCP 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# define IP e porta em que o servidor vai escutar
s.bind((HOST, PORT))

'''
ESSAS FUNÇÕES SEMPRE VÃO MANDAR MENSAGEM PARA TODOS OS USUÁRIOS!
'''

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
        if membro in usuarios_online:
            usuarios_online[membro].send(f'GRUPO={grupo}={remetente}: {texto}'.encode())

def enviar_mensagem_privada(destinatario, remetente, texto):
    if destinatario in usuarios_online:
        usuarios_online[destinatario].send(f'PRIVADO={remetente}: {texto}'.encode())
        usuarios_online[remetente].send(f'PRIVADO=Você para {destinatario}: {texto}'.encode())
    else:
        usuarios_online[remetente].send(f'SISTEMA=Usuário {destinatario} não está online'.encode())

# Recupera usuários e grupos salvos em JSON
def carregar_dados():
    global usuarios, grupos

    if not os.path.exists(ARQUIVO_DADOS):
        usuarios = {}
        grupos = {}
        return

    with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)

    usuarios = dados.get('usuarios', {})
    grupos = dados.get('grupos', {})

    # quando o servidor reinicia todos os usuários ficam offline
    for nome in usuarios:
        usuarios[nome]['status'] = 'offline'

# Salva o estado atual dos usuários e grupos em JSON
def salvar_dados():
    dados = {
        'usuarios': usuarios,
        'grupos': grupos
    }

    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)

#  Cada cliente conectado ganha uma thread executando essa função
def handle_clientes(conn, addr):
    print(f'[NOVA CONEXÃO] Um novo usuário se conectou pelo endereço {addr}!')
    global conexoes,mensagens
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
                    # Valida nomes (nome deve ser único) e verifica se o usuário já está online
                    if nome in usuarios and usuarios[nome]['status'] == 'online':
                        print(f"Nome duplicado detectado: {nome}")
                        conn.send("ERRO=Nome já está em uso, digite outro nome!".encode())
                        continue
                    
                    # Registra o usuário, atualiza o status e salva a conexão para mensagens futuras
                    usuarios[nome] = {"status": "online"}
                    usuarios_online[nome] = conn
                    salvar_dados()

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
                texto = msg.split("=", 1)[1]
                mensagem = nome + '=' + texto
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
                        salvar_dados()

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
                        salvar_dados()

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
                    lista_usuarios = ', '.join(usuarios_online.keys())
                    if lista_usuarios:
                        conn.send(f'SISTEMA=Usuários online: {lista_usuarios}'.encode())
                    else:
                            conn.send('SISTEMA=Nenhum usuário online'.encode())

            # Listar membros de um grupo
            elif msg.startswith('listar_membros='):
                nome_grupo = msg.split('=', 1)[1]

                with lock:
                    if nome_grupo not in grupos:
                        conn.send('SISTEMA=Grupo não existe'.encode())

                    elif len(grupos[nome_grupo]) == 0:
                        conn.send(f'SISTEMA=O grupo {nome_grupo} não possui membros'.encode())

                    else:
                        membros = ', '.join(grupos[nome_grupo])
                        conn.send(f'SISTEMA={nome_grupo} possui {len(grupos[nome_grupo])} membro(s): {membros}'.encode())

            # Exibir comandos disponíveis
            elif msg.startswith('ajuda='):
                ajuda = (
                    "\n=== COMANDOS DISPONÍVEIS ===\n"
                    "/criar nomegrupo -> cria um grupo\n"
                    "/entrar nomegrupo -> entra em um grupo\n"
                    "/sair nomegrupo -> sai de um grupo\n"
                    "/grupo nomegrupo mensagem -> envia mensagem para um grupo\n"
                    "/privado destinatario mensagem -> envia mensagem privada\n"
                    "/grupos -> lista todos os grupos\n"
                    "/usuarios -> lista usuários online\n"
                    "/membros nomegrupo -> lista membros de um grupo\n"
                    "/ajuda -> exibe esta ajuda\n"
                    "============================"
                )

                conn.send(f'SISTEMA={ajuda}'.encode())

            # Sair do grupo
            elif msg.startswith('sair_grupo='):
                nome_grupo = msg.split('=')[1]

                with lock:
                    if nome_grupo in grupos:
                        if nome in grupos[nome_grupo]:
                            grupos[nome_grupo].remove(nome)
                            salvar_dados()

                            conn.send(f'SISTEMA=Saiu de {nome_grupo}'.encode())

                            print(f'[GRUPO] {nome} saiu de {nome_grupo}')
            

# Desconexões
# Usuário desconectado: status offline, sem remover participação em grupos
def remover_usuario(nome, conn):
    global conexoes, usuarios, usuarios_online

    with lock:
        if nome in usuarios:
            usuarios[nome]["status"] = "offline"

        if nome in usuarios_online:
            del usuarios_online[nome]

        conexoes = [c for c in conexoes if c["conn"] != conn]

        salvar_dados()

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

carregar_dados()
start()