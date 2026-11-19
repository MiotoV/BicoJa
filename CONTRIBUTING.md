# Guia para novos desenvolvedores

Este guia leva você do zero até o BicoJá rodando na sua máquina, pronto para desenvolver. Siga os passos na ordem.

O ambiente roda em **Docker**: banco de dados (PostgreSQL + PostGIS) e API (Django) ficam em contêineres. O **VS Code** trabalha dentro do contêiner da API (Dev Container), então você não precisa instalar Python, Django nem PostgreSQL na sua máquina.

---

## 1. Acesso ao repositório

O repositório é privado. Peça ao responsável pelo projeto para adicionar você como colaborador (GitHub → repositório → *Settings* → *Collaborators*). Você vai receber um convite por e-mail: aceite antes de continuar.

Se ainda não tem conta, crie uma em github.com.

---

## 2. Instalar as ferramentas

### Windows

1. **WSL2 (Linux dentro do Windows).** Abra o PowerShell **como administrador** e rode:

   ```bash
   wsl --install
   ```

   Reinicie o computador. Na primeira abertura do **Ubuntu**, crie um usuário (minúsculas, sem espaço) e uma senha. A senha não aparece enquanto você digita; isso é normal.

2. **Docker Desktop.** Baixe em docker.com/products/docker-desktop e instale com a opção **"Use WSL 2"** marcada. Depois, em *Settings → Resources → WSL Integration*, ative o **Ubuntu** e clique em *Apply & restart*.

3. **VS Code.** Baixe em code.visualstudio.com e instale as extensões **WSL** e **Dev Containers** (ambas da Microsoft).

4. **Git e GitHub CLI.** No terminal do **Ubuntu**:

   ```bash
   sudo apt update && sudo apt install -y git gh
   ```

> **Importante no Windows:** todos os comandos deste guia, a partir daqui, são no terminal do **Ubuntu**, não no PowerShell. E o projeto deve ficar **dentro do Ubuntu** (ex.: `~/projetos`), nunca em `C:\`: no disco do Windows o Docker fica muito lento.

### macOS

Instale o Homebrew (brew.sh) e depois:

```bash
brew install git gh
brew install --cask docker visual-studio-code
```

Abra o Docker Desktop uma vez para concluir a configuração e instale a extensão **Dev Containers** no VS Code.

### Linux

Instale o Git, o GitHub CLI (`gh`), o Docker Engine (guia oficial em docs.docker.com) e o VS Code com a extensão **Dev Containers**. Para usar o Docker sem `sudo`:

```bash
sudo usermod -aG docker $USER
```

### Conferir

```bash
git --version
docker compose version
docker run hello-world
```

O último comando deve mostrar **"Hello from Docker!"**.

---

## 3. Configurar o Git e entrar no GitHub

Troque pelo seu nome e pelo e-mail da sua conta do GitHub:

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
git config --global init.defaultBranch main
```

Faça login no GitHub:

```bash
gh auth login
```

Responda: `GitHub.com` → `HTTPS` → `Yes` (autenticar o Git) → `Login with a web browser`. Copie o código mostrado, aperte Enter e autorize no navegador.

Confira:

```bash
gh auth status
```

---

## 4. Clonar o projeto

```bash
mkdir -p ~/projetos && cd ~/projetos
gh repo clone MiotoV/BicoJa
cd BicoJa
```

---

## 5. Criar o arquivo `.env`

O `.env` guarda senhas e chaves e **nunca vai para o repositório**. Crie o seu a partir do modelo:

```bash
cp .env.example .env
```

Gere uma chave secreta:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Abra o `.env` e cole a chave em `DJANGO_SECRET_KEY` (sem espaços ao redor do `=` e sem aspas). Os demais valores podem ficar como estão para desenvolvimento.

---

## 6. Abrir o projeto no Dev Container

1. Confira o seu número de usuário (Windows/Linux):

   ```bash
   id -u
   ```

   O esperado é `1000`. Se for outro número, avise o time antes de seguir: o Dev Container está configurado para o usuário 1000.

2. Abra o projeto no VS Code:

   ```bash
   code .
   ```

3. No VS Code, aperte `Ctrl+Shift+P` e escolha **Dev Containers: Reopen in Container**.

   Na primeira vez, ele monta o ambiente (alguns minutos). Quando terminar, o canto inferior esquerdo mostra **"Dev Container: BicoJá"**. O VS Code liga sozinho o banco e a API.

---

## 7. Preparar o banco e testar

No terminal do VS Code (*Terminal → New Terminal*), que agora roda **dentro do contêiner**:

```bash
cd backend
python manage.py check
```

Esperado: `System check identified no issues (0 silenced).`

Crie as tabelas e o seu usuário administrador (o login é por e-mail):

```bash
python manage.py migrate
python manage.py createsuperuser
```

Abra no navegador:

- http://localhost:8000: a API no ar.
- http://localhost:8000/admin: o painel. Entre com o e-mail e a senha que você criou.

Se chegou até aqui, seu ambiente está pronto.

---

## 8. Como trabalhar no dia a dia

### Dois terminais, dois papéis

| Terminal | Para quê |
|---|---|
| **VS Code** (selo "Dev Container") | Comandos do Django, direto: `python manage.py ...`. Também Git. |
| **Ubuntu** (fora do contêiner) | Comandos do Docker: `docker compose ps`, `logs`, `stop`, `start`. |

> Enquanto estiver usando o Dev Container, **não rode `docker compose up -d`** no Ubuntu: ele recria a API sem a configuração do Dev Container e derruba o VS Code. Para religar tudo, use **Dev Containers: Reopen in Container** ou `docker compose start`.

### Fluxo de uma tarefa

1. Atualize o `main` antes de começar:

   ```bash
   git checkout main
   git pull
   ```

2. Crie um branch para a tarefa (nome curto, em português, com prefixo):

   ```bash
   git checkout -b feature/cadastro-empresa
   ```

   Prefixos: `feature/` (funcionalidade nova), `fix/` (correção), `docs/` (documentação).

3. Desenvolva e faça commits pequenos, sempre que algo funcionar:

   ```bash
   git add .
   git commit -m "Cria modelo de unidade da empresa"
   ```

4. Envie o branch e abra um Pull Request para o `main`:

   ```bash
   git push -u origin feature/cadastro-empresa
   gh pr create --fill
   ```

   Outra pessoa do time revisa antes do merge. Não faça commits direto no `main`.

### Depois de cada `git pull`

| Se mudou... | Rode |
|---|---|
| Arquivos de `migrations/` | `python manage.py migrate` |
| `requirements.txt` ou `Dockerfile` | `Ctrl+Shift+P` → **Dev Containers: Rebuild Container** |
| `.env.example` (variável nova) | Copie a variável nova para o seu `.env` |

### Regras do projeto

- Siga os **Padrões do projeto** descritos no `README.md` (idioma, identificadores, segredos e commits).
- **Nunca** coloque senhas ou chaves no código nem no `.env.example`. Variável nova vai no `.env` e, com valor fictício, no `.env.example`.
- Alterou um modelo? Gere a migration e **inclua o arquivo no commit**:

  ```bash
  python manage.py makemigrations
  ```

- Ao colar logs em chats ou issues, apague antes as linhas com chaves e senhas.

---

## 9. Problemas comuns

| Problema | Solução |
|---|---|
| **"An error occurred setting up the container"** com `unable to find user vscode` no log | A API foi ligada fora do VS Code. No Ubuntu, rode `docker compose rm -sf api` e depois **Reopen in Container**. |
| **"port is already allocated"** (porta 8000) | Outro programa usa a porta 8000. Feche-o, ou troque `"8000:8000"` por `"8001:8000"` no `docker-compose.yml` só na sua máquina (sem commitar). |
| **Docker muito lento no Windows** | O projeto está em `C:\`. Clone de novo dentro do Ubuntu (`~/projetos`). |
| **Imports do Django sublinhados no editor** | Confira se o selo mostra "Dev Container: BicoJá". Se mostrar "WSL", use **Reopen in Container**. |
| **`InconsistentMigrationHistory`** ao rodar `migrate` | Seu banco local ficou com um histórico antigo. Em desenvolvimento, zere: no Ubuntu, `docker compose down -v` e depois **Reopen in Container** e `migrate` de novo. Isso apaga os dados locais. |
| **`KeyError: 'DJANGO_SECRET_KEY'`** | O `.env` não existe ou está sem a chave. Refaça o passo 5 e use **Rebuild Container**. |

Ficou travado? Copie o comando e a mensagem de erro completa (sem senhas) e mande para o time.
