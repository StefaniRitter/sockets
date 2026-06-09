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
* Listar membros de um grupo: /membros nomegrupo

### Falta fazer:
* Mensagem privada ✅
* Listar grupos ✅
* Listar usuários online ✅
* Listar membros de um grupo ✅
* Persistência dos dados (usar JSON) ✅
* Interface gráfica
* Remover grupos vazios?
* Melhorar tratamento de erros
* Comando de ajuda ✅

### Alterações:
* Mensagem privada entre usuários conectados
* Confirmação de envio para o remetente
* Exibição da mensagem para o destinatário
* Listar grupos 
* Listar usuários online 
* Listar membros de um grupo 
* Comando de "ajuda" para exibir ao usuário todos os comandos disponíveis
* Persistência de dados com JSON
* Salvamento de usuários com status online/offline
* Salvamento dos grupos criados e seus membros
* Carregamento automático dos dados ao iniciar o servidor

### Persistência de dados

A aplicação utiliza um arquivo `dados.json` para armazenar informações que devem continuar disponíveis mesmo após o servidor ser encerrado.

Atualmente, são salvos:

* Usuários já registrados, com status `online` ou `offline`;
* Grupos criados;
* Membros de cada grupo.

Ao iniciar o servidor, os dados são carregados automaticamente. Todos os usuários são definidos inicialmente como `offline`, pois conexões anteriores não permanecem válidas após reiniciar o servidor.

## Interface Gráfica

Além da versão em terminal, a aplicação também possui uma interface gráfica desenvolvida com a biblioteca Tkinter. A interface oferece uma tela de login para validação do nome do usuário e uma janela principal de chat para envio e recebimento de mensagens.

A versão gráfica utiliza a mesma comunicação baseada em sockets da versão em terminal, mantendo compatibilidade com todas as funcionalidades implementadas no servidor. O objetivo é proporcionar uma experiência mais intuitiva e amigável ao usuário, sem alterar a lógica de comunicação da aplicação.

Para executar a interface gráfica:

```bash
python3 gui_client.py

```md
> A interface gráfica está em desenvolvimento e novas funcionalidades serão adicionadas gradualmente.