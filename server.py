import socket
import threading
import json
import os

# Arquivo para persistência dos dados
ARQUIVO_DADOS = 'dados.json'

# IP e porta para o servidor
HOST = '127.0.0.1'
PORT = 50005

# Estruturas globais 
usuarios_online = {}  
grupos = {}           

# Locks
lock_usuarios = threading.Lock()
lock_grupos = threading.Lock()
lock_arquivo = threading.Lock()

# Servidor com ipv4 e protocolo TCP 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))

# Funcões auxiliares para persistência de dados
def carregar_dados():
    global grupos
    with lock_arquivo:
        if not os.path.exists(ARQUIVO_DADOS):
            grupos = {}
            return
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as arquivo:
            try:
                dados = json.load(arquivo)
                grupos = dados.get('grupos', {})
            except json.JSONDecodeError:
                grupos = {}

def salvar_dados():
    with lock_arquivo:
        dados = {'grupos': grupos}
        with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as arquivo:
            json.dump(dados, arquivo, indent=4, ensure_ascii=False)

# Funcões de envio
def enviar_mensagem_todos(remetente, texto):
    with lock_usuarios:
        for nome, conn in list(usuarios_online.items()):
            try:
                conn.send(f"GERAL={remetente}={texto}".encode('utf-8'))
            except socket.error:
                pass

def enviar_mensagem_grupo(remetente, nome_grupo, texto):
    with lock_grupos:
        if nome_grupo not in grupos:
            return False, "Grupo não existe."
        if remetente not in grupos[nome_grupo]:
            return False, "Você não faz parte deste grupo."
        membros = list(grupos[nome_grupo])

    for membro in membros:
        with lock_usuarios:
            conn_dest = usuarios_online.get(membro)
        if conn_dest:
            try:
                conn_dest.send(f"GRUPO={nome_grupo}={remetente}: {texto}".encode('utf-8'))
            except socket.error:
                pass
    return True, ""

def enviar_mensagem_privada(remetente, destinatario, texto):
    with lock_usuarios:
        conn_dest = usuarios_online.get(destinatario)
    if conn_dest:
        try:
            conn_dest.send(f"PRIVADO={remetente}: {texto}".encode('utf-8'))
            return True, ""
        except socket.error:
            return False, f"Erro ao enviar mensagem para {destinatario}."
    else:
        return False, f"Usuário {destinatario} está offline."

def remover_usuario(nome, conn):
    if nome:
        with lock_usuarios:
            if nome in usuarios_online:
                del usuarios_online[nome]
        print(f'[DESCONECTADO] {nome} desconectou-se.')
        enviar_mensagem_todos("SISTEMA", f"{nome} saiu do chat.")
    try:
        conn.close()
    except Exception:
        pass

#  Handler do cliente
def handle_cliente(conn, addr):
    nome = None
    print(f"[NOVA CONEXÃO] {addr} conectado.")

    # loop 1: autenticação
    while True:
        try:
            msg = conn.recv(2048).decode('utf-8')
            if not msg:
                conn.close()
                return

            if msg.startswith('nome='):
                candidato_nome = msg.split('=', 1)[1].strip()
                if not candidato_nome:
                    conn.send("ERRO=O nome não pode ser vazio.".encode('utf-8'))
                    continue

                with lock_usuarios:
                    if candidato_nome in usuarios_online:
                        conn.send("ERRO=Nome já em uso.".encode('utf-8'))
                        continue
                    else:
                        nome = candidato_nome
                        usuarios_online[nome] = conn
                
                conn.send("OK=NOME".encode('utf-8'))
                print(f"[AUTENTICADO] {nome} entrou usando o endereço {addr}.")
                enviar_mensagem_todos("SISTEMA", f"{nome} entrou no chat.")
                break
            else:
                conn.send("ERRO=Envie o comando 'nome=SeuNome' primeiro.".encode('utf-8'))
        except (socket.error, ConnectionResetError):
            try:
                conn.close()
            except Exception:
                pass
            return

    # Loop 2: comandos 
    while True:
        try:
            msg = conn.recv(2048).decode('utf-8')
            if not msg:
                break

            if msg.startswith('msg='):
                texto = msg.split('=', 1)[1]
                enviar_mensagem_todos(nome, texto)

            elif msg.startswith('criar_grupo='):
                nome_grupo = msg.split('=', 1)[1].strip()
                if not nome_grupo:
                    conn.send("SISTEMA=Uso: /criar nome_grupo".encode('utf-8'))
                    continue

                with lock_grupos:
                    if nome_grupo in grupos:
                        conn.send("SISTEMA=Esse grupo já existe.".encode('utf-8'))
                    else:
                        grupos[nome_grupo] = [nome]
                        salvar_dados()
                        conn.send(f"SISTEMA=Grupo '{nome_grupo}' criado e você foi adicionado.".encode('utf-8'))
                        print(f"[GRUPO] {nome} criou o grupo {nome_grupo}")

            elif msg.startswith('entrar_grupo='):
                nome_grupo = msg.split('=', 1)[1].strip()
                with lock_grupos:
                    if nome_grupo not in grupos:
                        conn.send("SISTEMA=Esse grupo não existe.".encode('utf-8'))
                    elif nome in grupos[nome_grupo]:
                        conn.send("SISTEMA=Você já está neste grupo.".encode('utf-8'))
                    else:
                        grupos[nome_grupo].append(nome)
                        salvar_dados()
                        conn.send(f"SISTEMA=Você entrou no grupo {nome_grupo}.".encode('utf-8'))
                        print(f"[GRUPO] {nome} entrou no grupo {nome_grupo}")

            elif msg.startswith('sair_grupo='):
                nome_grupo = msg.split('=', 1)[1].strip()
                with lock_grupos:
                    if nome_grupo in grupos and nome in grupos[nome_grupo]:
                        grupos[nome_grupo].remove(nome)
                        salvar_dados()
                        conn.send(f"SISTEMA=Você saiu do grupo {nome_grupo}.".encode('utf-8'))
                        print(f"[GRUPO] {nome} saiu do grupo {nome_grupo}")
                    else:
                        conn.send("SISTEMA=Você não faz parte deste grupo ou ele não existe.".encode('utf-8'))

            elif msg.startswith('grupo_msg='):
                conteudo = msg.split('=', 1)[1]
                if '|' in conteudo:
                    nome_grupo, texto = conteudo.split('|', 1)
                    sucesso, erro_msg = enviar_mensagem_grupo(nome, nome_grupo, texto)
                    if not sucesso:
                        conn.send(f"SISTEMA={erro_msg}".encode('utf-8'))
                else:
                    conn.send("SISTEMA=Formato incorreto de mensagem de grupo.".encode('utf-8'))

            elif msg.startswith('privado_msg='):
                conteudo = msg.split('=', 1)[1]
                if '|' in conteudo:
                    destinatario, texto = conteudo.split('|', 1)
                    sucesso, erro_msg = enviar_mensagem_privada(nome, destinatario, texto)
                    if not sucesso:
                        conn.send(f"SISTEMA={erro_msg}".encode('utf-8'))
                else:
                    conn.send("SISTEMA=Formato incorreto de mensagem privada.".encode('utf-8'))

            elif msg.startswith('listar_membros='):
                nome_grupo = msg.split('=', 1)[1].strip()
                with lock_grupos:
                    membros = grupos.get(nome_grupo)
                if membros is not None:
                    conn.send(f"SISTEMA=Membros de {nome_grupo}: {', '.join(membros)}".encode('utf-8'))
                else:
                    conn.send("SISTEMA=Grupo não encontrado.".encode('utf-8'))

            elif msg == 'listar_grupos=':
                with lock_grupos:
                    lista_g = list(grupos.keys())
                conn.send(f"SISTEMA=Grupos disponíveis: {', '.join(lista_g) if lista_g else 'Nenhum'}".encode('utf-8'))

            elif msg == 'listar_usuarios=':
                with lock_usuarios:
                    lista_u = list(usuarios_online.keys())
                conn.send(f"SISTEMA=Usuários online: {', '.join(lista_u)}".encode('utf-8'))

            elif msg == 'ajuda=':
                ajuda_txt = (
                    "\n--- Comandos Disponíveis ---\n"
                    "/criar <grupo> - Cria um novo grupo\n"
                    "/entrar <grupo> - Entra num grupo existente\n"
                    "/sair_grupo <grupo> - Sai de um grupo\n"
                    "/grupo <grupo> <msg> - Envia mensagem para um grupo\n"
                    "/membros <grupo> - Lista os membros de um grupo\n"
                    "/privado <usuario> <msg> - Envia uma mensagem privada\n"
                    "/grupos - Lista todos os grupos\n"
                    "/usuarios - Lista todos os usuários online\n"
                    "/ajuda - Mostra esta lista"
                )
                conn.send(f"SISTEMA={ajuda_txt}".encode('utf-8'))

        except (socket.error, ConnectionResetError):
            break

    # Desconexão
    remover_usuario(nome, conn)

def start():
    print('Servidor iniciado, aguardando conexões...')
    carregar_dados()
    s.listen()

    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_cliente, args=(conn, addr), daemon=True)
        thread.start()

if __name__ == '__main__':
    start()