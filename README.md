# Aplicação para troca de mensagens com sockets

## Visão Geral
Esta aplicação implementa um sistema de chat baseado em TCP utilizando Python e Threads. O servidor permite:

- Comunicação geral entre todos os usuários conectados.
- Criação de grupos de conversa.
- Entrada e saída de grupos.
- Mensagens privadas entre usuários.
- Persistência dos grupos em arquivo JSON.
- Controle de usuários online em tempo real.

## Arquiteura
#### Servidor
- Utiliza sockets TCP.
- Aceita múltiplos clientes simultaneamente.
- Cria uma Thread para cada conexão.
- Utiliza Locks para evitar condições de corrida.
- Mantém usuários online em memória.
- Salva grupos em arquivo JSON.

#### Cliente
Thread principal:
- Recebe comandos digitados pelo usuário.

Thread secundária:
- Escuta mensagens recebidas do servidor.

## Estrutura dos arquivos
```bash
Projeto/ 
│ 
├── server.py       # Recebe conexões, gerencia usuários, grupos e mensagens
├── client.py       # Client do chat utilizado pelos usários para conectar ao servidor
└── dados.json      # Arquivo para armazenar os grupos criados
```

## Requisitos
- Python 3.10 ou superior
- Sistema Operacional Windows, Linux ou macOS
- Biblioteca padrão do Python (não requer instalação de pacotes externos)


## Executando o servidor
Abra um terminal na pasta do projeto e execute:
```bash
python server.py
```

Ao iniciar corretamente será exibida a mensagem:
```bash
Servidor iniciado, aguardando conexões...
```

O servidor ficará escutando na porta:
```bash
50005
```
em todas as interfaces de rede:
```bash
HOST = '0.0.0.0'
```

## Executando os Clientes
### Opção 1 – Servidor e Cliente no Mesmo Computador
Se o servidor e os clientes estiverem no mesmo computador, mantenha no arquivo client.py:
```bash
SERVER = '127.0.0.1'
PORT = 50005
```

Em outro terminal execute:
```bash
python client.py
```
Você poderá abrir vários clientes simultaneamente na mesma máquina.


### Opção 2 – Clientes em Computadores Diferentes
Quando os clientes estiverem em computadores diferentes da máquina que hospeda o servidor, é necessário utilizar o endereço IP do computador servidor.

#### Passo 1 – Descobrir o IP do Servidor
No computador que executa o servidor:
```bash
ipconfig
```

Localize o endereço IPv4.
Exemplo:
```bash
IPv4: 192.168.1.50
```

#### Passo 2 – Configurar o Cliente
No arquivo client.py altere:
```bash
SERVER = '127.0.0.1'
```
para:
```bash
SERVER = '192.168.1.50'
```
(substituindo pelo IP real do servidor)


#### Passo 3 – Configuração do Firewall
Se o firewall do computador que executa o servidor estiver bloqueando as conexões, os clientes não conseguirão se conectar ao chat.
Nesse caso, pode ser necessário liberar:

- A conexão de entrada na porta 50005/TCP.
- O executável python.exe nas regras do firewall.

As configurações variam conforme o sistema operacional e o software de firewall utilizado.

## Comandos disponíveis
``` bash
Mensagem normal                     # Envia uma mensagem para todos os usuários conectados.
/criar <grupo>	                    # Cria um novo grupo.
/entrar <grupo>	                    # Entra em um grupo existente.
/sair_grupo <grupo>	                # Sai de um grupo.
/grupo <grupo> <mensagem>	        # Envia uma mensagem para um grupo.
/membros <grupo>	                # Lista os membros de um grupo.
/privado <usuário> <mensagem>	    # Envia uma mensagem privada para um usuário.
/grupos	                            # Lista todos os grupos disponíveis.
/usuarios	                        # Lista os usuários online.
/ajuda	                            # Exibe a lista de comandos.
```

## Encerramento
Para desligar o servidor, feche o terminal onde o arquivo `server.py` está sendo executado. 
- Todos os clientes conectados perderão a conexão e precisarão se reconectar após a reinicialização do servidor.

## Uso da IA
Durante o desenvolvimento deste projeto, ferramentas de Inteligência Artificial foram utilizadas como apoio ao aprendizado e à implementação da aplicação:
- Esclarecimento de dúvidas sobre sockets TCP.
- Revisão e análise do código desenvolvido.
- Sugestões de melhorias na organização e estrutura do sistema.
- Apoio na identificação e correção de erros.
