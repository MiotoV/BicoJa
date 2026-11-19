# BicoJá

Plataforma de intermediação que conecta comércios (CNPJ) a prestadores de serviço esporádico (CPF): publicação de vagas, candidatura, perfil profissional, contrato, execução, pagamento e avaliação mútua.

Este repositório contém o **back-end** (API e painel administrativo).

## Stack

- **Python 3.12** com **Django 5.2** (LTS)
- **PostgreSQL 16** com **PostGIS** (distância e raio de deslocamento)
- **Docker** e **Docker Compose** para o ambiente de desenvolvimento

## Pré-requisitos

- Windows com **WSL2** (Ubuntu), macOS ou Linux
- **Docker Desktop** (no Windows, com a integração WSL ativada)
- **Git**

No Windows, mantenha o projeto dentro do Ubuntu (ex.: `~/projetos/BicoJa`), não em `C:\`, para o Docker ter bom desempenho.

## Como rodar

1. Clone o repositório e entre na pasta:

   ```bash
   gh repo clone MiotoV/BicoJa && cd BicoJa
   ```

2. Crie o arquivo de variáveis de ambiente a partir do modelo:

   ```bash
   cp .env.example .env
   ```

3. Gere uma chave secreta e cole em `DJANGO_SECRET_KEY` no `.env`:

   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

4. Suba os serviços:

   ```bash
   docker compose up -d
   ```

5. Confira se está tudo certo:

   ```bash
   docker compose exec api python manage.py check
   ```

6. Crie as tabelas, rode os testes e crie o seu usuário administrador (login por e-mail):

   ```bash
   docker compose exec api python manage.py migrate
   docker compose exec api python manage.py test
   docker compose exec api python manage.py createsuperuser
   ```

A API fica disponível em http://localhost:8000 e o painel em `http://localhost:8000/<DJANGO_ADMIN_URL>`, com o endereço definido no `.env`.

Para desenvolver com o VS Code, veja o `CONTRIBUTING.md` (Dev Container).

## Comandos úteis

| Comando | Para que serve |
|---|---|
| `docker compose up -d` | Liga os serviços em segundo plano |
| `docker compose ps` | Mostra os serviços e se estão rodando |
| `docker compose logs -f api` | Acompanha os logs do Django |
| `docker compose stop` | Desliga os serviços (mantém os dados) |
| `docker compose down` | Remove os contêineres (os dados ficam no volume) |
| `docker compose down -v` | Remove também os dados do banco (só em desenvolvimento) |
| `docker compose exec api python manage.py <comando>` | Roda comandos do Django |

## Estrutura

```
BicoJa/
├── .devcontainer/        # ambiente do VS Code dentro do contêiner
├── .env.example          # modelo das variáveis de ambiente
├── docker-compose.yml    # serviços: banco (db) e API (api)
└── backend/
    ├── Dockerfile
    ├── requirements.in   # bibliotecas escolhidas (editar aqui)
    ├── requirements.txt  # lock com versões exatas e hashes (gerado)
    ├── manage.py
    ├── config/           # configurações, rotas e pontos de entrada do Django
    └── contas/           # identidade e acesso: usuário, login por e-mail
```

## Dependências

As bibliotecas ficam travadas com versão exata e hash em `backend/requirements.txt`, gerado a partir de `backend/requirements.in`. Para adicionar ou atualizar uma biblioteca:

1. Edite `backend/requirements.in`.
2. Gere o lock de novo, no terminal do Dev Container (em `backend/`):

   ```bash
   pip install --user pip-tools
   python -m piptools compile --generate-hashes --strip-extras -o requirements.txt requirements.in
   ```

3. Faça **Dev Containers: Rebuild Without Cache Container** e commite os dois arquivos.

## Padrões do projeto

### Idioma

- **Domínio em português:** apps, modelos, campos e mensagens. Ex.: `contas`, `Usuario`, `Vaga`, `cpf`, `criado_em`.
- **Termos técnicos do framework em inglês:** o que o Django e as bibliotecas já definem. Ex.: `is_active`, `password`, `Meta`.
- **Sem acentos nem "ç" nos nomes do código:** `Usuario`, `Funcao`, `situacao`. Acentos só nos textos exibidos ao usuário (ex.: `verbose_name="função"`).
- **Commits em português**, no imperativo e descrevendo a mudança. Ex.: `Cria app contas com usuário personalizado`.

### Identificadores

- Todo modelo exposto na API tem dois identificadores:
  - `id` (inteiro): uso interno, nas ligações entre tabelas.
  - `uuid`: uso público, nas URLs da API e no app.
- **Nunca expor o `id` numérico** em URLs ou respostas da API.

### Segredos e configurações

- Senhas, chaves e configurações por ambiente ficam no `.env`, **nunca no código**.
- O `.env` não vai para o repositório. Toda variável nova deve ser adicionada também ao `.env.example`, com um valor fictício.

### Commits

- Commits pequenos, feitos sempre que algo novo estiver funcionando.
