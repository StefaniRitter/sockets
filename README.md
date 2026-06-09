# Aplicação para troca de mensagens com sockets

## Visão Geral

Este projeto foi desenvolvido como parte da disciplina de Redes de Computadores, da Universidade Federal de Rio Grande (FURG), e se trata de um serviço de troca de mensagens, com a possibilidade de criação de múltiplos usuários, grupos e usuários por grupo.
Para isso, esta aplicação utiliza sockets e threads, implementados com a linguagem python.

## Passo a Passo para a Execução em Ambiente WSL/Linux

### 1. Clonar o repositório
```bash
git clone https://github.com/StefaniRitter/sockets.git
```

### 2. Acessar a pasta do projeto
```bash
cd sockets
```

### 3. Instalar Python, se necessário
```bash
sudo apt update
sudo apt install python3-pip python3-dev -y
```

### 4. Em um terminal, executar o servidor e manter o terminal aberto
```bash
python3 server.py
```
Saída esperada:
```
[INICIANDO] Iniciando socket...
```

### 5. Em um segundo terminal, executar o cliente
```bash
python3 client.py
```
Saída esperada:
```
Digite seu nome:
```

### 6. Para testar a troca de mensagens entre dois usuários, basta abrir um terceiro terminal, executando a criação de outro cliente
```bash
python3 client.py
```
Saída esperada:
```
Digite seu nome:
```

### 7. Depois disso, basta escrever as mensagens desejadas em cada terminal para mandar para o outro terminal. Enquanto isso, o servidor vai exibir um log com as conexões e envios de mensagem.


A imagem abaixo mostra 4 terminais diferentes, onde o primeiro é o servidor, e os outros 3 são clientes. O objetivo dessa parte do programa é simular um grupo, onde toda e qualquer mensagem enviada vai para todos os clientes conectados no servidor, e quando um novo cliente faz uma conexão, ele recebe todas as mensagens enviadas anteriormente.

<img width="1645" height="657" alt="image" src="https://github.com/user-attachments/assets/eff7e195-f7f3-45f2-b082-0c410ab990e4" />


Resolver:

* Faz sentido enviar as mensagens anteriores para os novos usuários?
* Fechar conexão nas portas para evitar erros e threads fantasmas;
* Criar funções para conversas privadas entre dois usuários;
* Criar funções para múltiplos grupos;
* Refatorar código e lógica.

### Alterações: 
* Validação de nome único no login
* Tratamento de desconexão de usuários
* Criação de grupos
* Entrada em grupos
* Saída de grupos
* Envio de mensagens para grupos
* Criador entra automaticamente no grupo criado
* Mensagens de sistema e erro
* Logs de conexão, grupos e desconexão
* Uso de Lock para evitar problemas entre threads
* Identificação visual de mensagens:
    * [GERAL]
    * [nomegrupo]

### Comandos do terminal: 
* Mensagem global: oi pessoal
* Criar grupo: /criar nomegrupo
* Entrar em grupo: /entrar nomegrupo
* Sair grupo: /sair nomegrupo
* Enviar mensagem em grupo: /grupo nomegrupo oi
* Mensagem privada: /privado destinatario mensagem
* Listar grupos: /grupos
* Listar usuários online: /usuarios

### Falta fazer:
* Mensagem privada
* Listar grupos
* Listar usuários online
* Listar membros de um grupo
* Persistência dos dados (usar JSON)
* Interface gráfica

### Alterações:
* Mensagem privada entre usuários conectados
* Listagens: grupos, usuários conectados
