# Projeto DevOps - Ambiente Multi-Container

Este projeto demonstra como criar um **ambiente multi-container** utilizando **Docker Compose**. Inclui uma **API Flask com CRUD** conectada a um banco de dados **PostgreSQL**.

## Objetivos

- Criar um `Dockerfile` multi-stage utilizando imagens Alpine  
- Configurar um ambiente multi-container (API + Banco de Dados)  
- Utilizar volumes do Docker para persistência de dados  
- Criar uma rede customizada para comunicação entre containers  
- Usar variáveis de ambiente para configurações sensíveis  
- Evitar o uso do usuário root no banco de dados  

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

---

## Parar e limpar o ambiente

Parar todos os containers:

```bash
docker compose down
```

Parar e remover volumes (inclui dados do banco):

```bash
docker compose down -v
```

Ver logs dos containers:

```bash
docker compose logs -f app
docker compose logs -f db
```

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

## Comandos Úteis
Recompilar a aplicação após alterações:

```bash
docker compose build app
```

Reiniciar a aplicação:

```bash
docker compose restart app
```

Listar containers em execução:

```bash
docker ps
```

Entrar no shell da aplicação:

```bash
docker compose exec app sh
```

Entrar no shell do PostgreSQL:

```bash
docker compose exec db psql -U appuser -d appdb
```
