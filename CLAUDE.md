# CLAUDE.md

Contexto do projeto para o Claude Code. Este arquivo é lido automaticamente no início de cada sessão. Mantenha-o atualizado quando decisões ou o estado do projeto mudarem.

## O projeto

**BicoJá** é uma plataforma de intermediação que conecta comércios (CNPJ) a prestadores de serviço esporádico (CPF): publicação de vagas, candidatura, perfil profissional, contrato, execução (check-in/out), pagamento e avaliação mútua. A plataforma não contrata nem remunera ninguém; as regras anti-vínculo empregatício são centrais.

O escopo detalhado do módulo de cadastro (prestador em 7 etapas, empresa em 6 etapas, perfil profissional gerado automaticamente, regras da seção 5, LGPD) está no documento de escopo do responsável pelo projeto. Na dúvida sobre uma regra de negócio, pergunte em vez de inventar.

## Decisões de arquitetura

- **Back-end:** Python 3.12, Django 5.2 (LTS), PostgreSQL 16 + PostGIS (distância e raio). Funciona como **API** (Django REST Framework, a configurar) + painel administrativo (Django Admin).
- **Front-end (próxima etapa):** React com Vite, um único front-end web para empresa e prestador, no PC e no celular. Área do prestador desenhada **mobile-first**.
- **App nas lojas (depois da primeira versão web):** Capacitor empacotando o mesmo front-end web. Por isso:
  - toda regra de negócio fica na API, nunca só nas telas;
  - autenticação por token (JWT com renovação), que serve para web e app;
  - API versionada desde o início (`/api/v1/`);
  - câmera, GPS e notificações isolados num módulo próprio do front-end.
- **PWA** logo após a primeira versão web (instalar na tela inicial sem passar pelas lojas).

## Padrões do código

- **Idioma:** domínio em português (apps, modelos, campos, rotas, mensagens: `contas`, `Usuario`, `criado_em`, `cadastro/`). Termos do framework em inglês (`is_active`, `Meta`). Sem acentos nem "ç" nos nomes do código; acentos só em textos exibidos (`verbose_name`).
- **Identificadores:** todo modelo exposto na API tem `id` (inteiro, interno) e `uuid` (público, nas URLs e respostas). **Nunca expor o `id` numérico.**
- **Segredos:** tudo no `.env` (nunca commitado). Variável nova vai também no `.env.example` com valor fictício.
- **Commits:** em português, no imperativo, pequenos.
- **Migrations:** sempre commitadas. Depois que chegam ao `main`, nunca são editadas; mudanças viram migrations novas.

## Segurança e desempenho (prioridade do projeto)

Toda mudança deve considerar segurança e eficiência. Já implementado:

- Dependências travadas com versão exata e hash (`backend/requirements.in` → `requirements.txt` via pip-tools; Dockerfile usa `--require-hashes`).
- Senhas com Argon2 (`PASSWORD_HASHERS`) e os 4 validadores padrão do Django.
- Painel em endereço configurável (`DJANGO_ADMIN_URL` no `.env`); `/admin/` responde 404.
- `DEBUG` desligado por padrão; `SECRET_KEY` só via ambiente; `ALLOWED_HOSTS` ignora valores vazios.
- Usuário personalizado (`contas.Usuario`): login por e-mail sempre em minúsculas (manager, `clean()` e `CheckConstraint` no banco), `uuid` público, `tipo` (prestador, empresa, equipe), `criado_em` não editável.

Planejado (não esquecer):

| Quando | Medida |
|---|---|
| API de acesso | Limite de tentativas no login/cadastro, JWT de curta duração com renovação e invalidação, CORS restrito ao front-end |
| Confirmações | 2FA obrigatório para equipe do painel e administradores de empresa; códigos SMS com hash, validade e limite de tentativas; recuperação de senha com link de uso único |
| Cadastro do prestador | Criptografia de CPF, NIT, dados bancários e documentos; selfie descartada após validação; registro de acessos ao perfil |
| Antes da produção | HTTPS, HSTS, cookies seguros; Gunicorn e contêiner sem root; banco gerenciado com backup; segredos em cofre; monitoramento; revisão de segurança independente (pentest) e validação jurídica |

## Ambiente de desenvolvimento

- Windows + WSL2 (Ubuntu), Docker Desktop, VS Code com **Dev Container** (`.devcontainer/`). O projeto fica em `~/projetos/BicoJa` dentro do Ubuntu.
- `docker-compose.yml`: serviços `db` (postgis/postgis:16-3.4, volume `pgdata`) e `api` (Django `runserver` na porta 8000). Ambos leem o `.env`.
- No Dev Container, o projeto está em `/workspace`; o código Django em `/workspace/backend`.
- **Dois terminais:**
  - VS Code (Dev Container, usuário `vscode`): comandos Django direto (`python manage.py ...`) e Git.
  - Ubuntu (fora do contêiner): comandos Docker (`docker compose ps`, `logs`, `stop`, `start`). **Não rodar `docker compose up -d` com o Dev Container aberto** (recria a API e derruba o VS Code).
- Mudou `requirements.in` ou `Dockerfile`: gerar o lock e usar **Dev Containers: Rebuild Without Cache Container**.
- Mudou o `.env`: **Rebuild Container**.

Comandos frequentes (no Dev Container, em `/workspace/backend`):

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py test
python manage.py createsuperuser
```

## Fluxo de trabalho (GitHub Flow)

- `main` sempre funcionando. Nunca commitar direto no `main`.
- Um branch por tarefa: `feature/...`, `fix/...`, `docs/...`.
- Pull request revisado e **Squash and merge**; branches apagados automaticamente após o merge.
- Antes de commitar: `python manage.py test` passando e `git status` sem `.env`.

## Estado atual

- `main`: ambiente Docker + Dev Container, segurança base, app `contas` (etapa 1: modelo, admin, migration `0001_initial`, 10 testes), README e CONTRIBUTING.
- Branch `fix/ajustes-revisao` (sem PR ainda): `ALLOWED_HOSTS` ignorando vazios; linha com espaços removida do `contas/admin.py`. Precisa de `git merge main` (correção do CONTRIBUTING feita no `main`).

## Próximos passos

1. Terminar `fix/ajustes-revisao`:
   - porta da API só local: `"127.0.0.1:8000:8000"` no `docker-compose.yml`;
   - serviço `db` recebendo só as variáveis `POSTGRES_*` (não o `.env` inteiro);
   - `healthcheck` no `db` e `depends_on` com `condition: service_healthy`;
   - remover o import não usado de `contas/views.py`;
   - linha final nos arquivos que não têm.
2. ruff (formatação e lint), pytest e GitHub Actions rodando os testes a cada PR. Marcar a senha de teste em `contas/tests.py` como exceção da regra S106.
3. Etapa 2 do `contas`: Django REST Framework, JWT (entrar, renovar, sair), criar conta com registro de aceite dos termos (`AceiteTermos`: versão, IP, user agent, data), `contas/eu/`, documentação em `/api/docs/`.
4. Iniciar o front-end React (Vite) com design system (pode ser feito em paralelo pelo segundo desenvolvedor).
5. Etapa 3 do `contas`: confirmação de e-mail e celular, 2FA, recuperação de senha.
6. Cadastros da empresa e do prestador.

Pendências fora do código: decidir a visibilidade do repositório (hoje público; recomendado privado) e ativar a proteção do `main` (ruleset exigindo PR).

## Como trabalhar com o responsável pelo projeto

- Responder sempre em **português**.
- Ir **um passo de cada vez**: explicar o que o passo faz e por que importa, dar os comandos em blocos separados e dizer o resultado esperado de cada um. Esperar a confirmação antes do próximo passo.
- Construção **incremental**: cada arquivo ou configuração entra só quando há necessidade.
- Manter no repositório apenas o que é de fato do desenvolvimento.
- Ao revisar, rodar de fato os testes e checagens em vez de só ler o código, e relatar o resultado com honestidade.
