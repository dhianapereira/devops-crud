# Projeto DevOps - Ambiente Multi-Container

![CI/CD](https://github.com/dhianapereira/devops-crud/actions/workflows/main.yml/badge.svg)

Este projeto demonstra como criar um **ambiente multi-container** utilizando **Docker Compose**. Inclui uma **API Flask com CRUD** conectada a um banco de dados **PostgreSQL**.

- [Projeto DevOps - Ambiente Multi-Container](#projeto-devops---ambiente-multi-container)
  - [Segurança](#segurança)
  - [Persistência de Dados](#persistência-de-dados)
  - [Rede Customizada](#rede-customizada)
  - [Configuração e Execução](#configuração-e-execução)
    - [Clonar o repositório](#clonar-o-repositório)
    - [Criar o arquivo de variáveis de ambiente](#criar-o-arquivo-de-variáveis-de-ambiente)
    - [Construir e subir os containers](#construir-e-subir-os-containers)
    - [Criar as tabelas no banco de dados](#criar-as-tabelas-no-banco-de-dados)
    - [Testar o funcionamento](#testar-o-funcionamento)
      - [Verificar se o serviço está ativo:](#verificar-se-o-serviço-está-ativo)
    - [Testar o CRUD](#testar-o-crud)
      - [Criar um item:](#criar-um-item)
      - [Listar todos os itens:](#listar-todos-os-itens)
      - [Buscar item por ID:](#buscar-item-por-id)
      - [Atualizar item:](#atualizar-item)
      - [Deletar item:](#deletar-item)
    - [Parar e limpar o ambiente](#parar-e-limpar-o-ambiente)
  - [CI/CD](#cicd)
    - [Secrets do GitHub](#secrets-do-github)
    - [Configuração Manual no Servidor (Primeiro Acesso)](#configuração-manual-no-servidor-primeiro-acesso)


## Segurança
- O banco **não** é acessado com o usuário padrão `postgres`.
- O script `init-db.sql` cria um usuário separado (`appuser`) com permissões apenas sobre o banco `appdb`.
- As credenciais são configuradas via variáveis de ambiente, e **não estão hardcoded** no código da aplicação.

## Persistência de Dados
O volume `db-data` garante que os dados do banco sejam mantidos mesmo que o container seja removido:

```yaml
volumes:
  db-data:
```
Assim, o banco de dados continua intacto após reiniciar o ambiente.

## Rede Customizada
O projeto utiliza uma rede customizada para comunicação isolada entre os containers:

```yaml
networks:
  app-network:
    driver: bridge
```
A aplicação Flask acessa o banco usando o nome do serviço `db` como hostname.

## Configuração e Execução
Siga os passos abaixo para configurar e executar o projeto localmente 
usando Docker Compose.

### Clonar o repositório

```bash
git clone https://github.com/dhianapereira/devops-crud.git
cd devops-crud
```

### Criar o arquivo de variáveis de ambiente
Copie o arquivo de exemplo e, se desejar, edite os valores:

```bash
cp .env.example .env
```

### Construir e subir os containers

Execute o comando abaixo para construir as imagens e iniciar os containers:

```bash
docker compose up -d --build
```

Esse comando:
- Cria a imagem da aplicação Flask usando um **Dockerfile multi-stage**
- Sobe o container do banco de dados PostgreSQL (`devops_db`)
- Executa automaticamente o script `init-db.sql`, que cria:
  - Banco: `appdb`
  - Usuário: `appuser`
  - Senha: `appsecret`
- Sobe o container da aplicação (`devops_app`) na porta **5000**

### Criar as tabelas no banco de dados
Após os containers estarem rodando, execute este comando para criar as tabelas:

```bash
docker compose exec app python -c "from app.main import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all();"
```
Esse comando cria a tabela `items` dentro do banco `appdb`.

### Testar o funcionamento

#### Verificar se o serviço está ativo:

```bash
curl http://localhost:5000/health
```

Resposta esperada:

```json
{"status": "ok"}
```

### Testar o CRUD

#### Criar um item:

```bash
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Caderno", "description": "Capa dura"}'
```

#### Listar todos os itens:

```bash
curl http://localhost:5000/items
```

#### Buscar item por ID:

```bash
curl http://localhost:5000/items/1
```

#### Atualizar item:

```bash
curl -X PUT http://localhost:5000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Caderno Atualizado"}'
```

#### Deletar item:

```bash
curl -X DELETE http://localhost:5000/items/1
```

### Parar e limpar o ambiente
Parar todos os containers:

```bash
docker compose down
```

Parar e remover volumes (inclui dados do banco):

```bash
docker compose down -v
```

## CI/CD
Este projeto utiliza um pipeline completo de CI/CD configurado com GitHub Actions, Docker e deploy automático via SSH em um servidor remoto.

O processo é executado automaticamente toda vez que um commit é enviado para a branch `main`, seguindo as etapas abaixo:

1. **Integração Contínua (CI):**

     - O GitHub Actions realiza o *checkout* do código e inicia o ambiente de testes com Docker Compose.
     - São executados todos os testes automatizados com `pytest`.
     - Se algum teste falhar, o pipeline é interrompido e o deploy não é realizado.

2. **Build e Push da Imagem:**

     - Caso os testes passem, o pipeline gera uma **imagem Docker** da aplicação.
     - A imagem é enviada automaticamente para o **Docker Hub**, com duas *tags*: `latest` e o hash curto do commit (exemplo: `a1b2c3d`).

3. **Deploy Contínuo (CD):**

     - Após o envio da imagem, o pipeline conecta-se ao servidor remoto via **SSH** (usando as chaves e credenciais armazenadas nos *Secrets* do GitHub).
     - Dentro do servidor, o workflow:
       - Atualiza o repositório com `git pull`.
       - Cria um arquivo `.env` temporário com o nome e a tag da imagem.
       - Executa os comandos:
        ```bash
        docker-compose --env-file .env -f docker-compose.prod.yml pull app
        docker-compose --env-file .env -f docker-compose.prod.yml up -d
        ```
       - Assim, a aplicação é atualizada automaticamente com a nova versão da imagem Docker.

### Secrets do GitHub
Para que o deploy funcione corretamente, é necessário configurar os seguintes *Secrets* no repositório do GitHub:

| Nome do Secret       | Descrição                                                         |
| -------------------- | ----------------------------------------------------------------- |
| `DOCKERHUB_USERNAME` | Usuário do Docker Hub                                             |
| `DOCKERHUB_TOKEN`    | Token de acesso do Docker Hub (com permissão de push)             |
| `DOCKER_IMAGE_NAME`  | Nome completo da imagem         |
| `SSH_HOST`           | IP público do servidor remoto                                     |
| `SSH_USER`           | Usuário SSH |
| `SSH_PORT`           | Porta SSH                         |
| `SSH_PRIVATE_KEY`    | Chave privada usada pelo GitHub Actions para conectar ao servidor |
| `SERVER_APP_PATH`    | Caminho do projeto no servidor |

Essas variáveis são definidas em
**Configurações → Secrets and variables → Actions → New repository secret**.

### Configuração Manual no Servidor (Primeiro Acesso)
Antes do primeiro deploy automático, é necessário preparar o servidor (VPS).

1. **Acessar o servidor via SSH**

   ```bash
   ssh root@<IP_DO_SERVIDOR>
   ```

2. **Instalar Docker e Docker Compose**

   ```bash
   apt update
   apt install -y docker.io docker-compose
   ```

3. **Clonar o repositório**

   ```bash
   git clone https://github.com/dhianapereira/devops-crud.git
   cd devops-crud
   ```

4. **Criar o arquivo `.env`**

   ```bash
   cp .env.example .env
   nano .env
   ```
   Ajuste as variáveis de ambiente necessárias (usuário, senha, banco, etc.).

5. **Executar manualmente o compose (opcional)**

   ```bash
   docker-compose up -d --build
   ```
