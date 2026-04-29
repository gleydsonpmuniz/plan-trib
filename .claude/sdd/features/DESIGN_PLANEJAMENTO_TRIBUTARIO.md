# DESIGN: Planejamento Tributário Comparativo

> Design técnico para implementação do sistema de planejamento tributário (Simples × LP × LR) — backend FastAPI + frontend Next.js + Postgres em Docker, deploy via GitHub Actions na VPS Hostinger.

## Metadata

| Atributo | Valor |
|----------|-------|
| **Feature** | PLANEJAMENTO_TRIBUTARIO |
| **Date** | 2026-04-28 |
| **Author** | design-agent (executado por Claude Opus 4.7) |
| **DEFINE** | [DEFINE_PLANEJAMENTO_TRIBUTARIO.md](./DEFINE_PLANEJAMENTO_TRIBUTARIO.md) |
| **Status** | Ready for Build |
| **KB Referenciada** | `kb/tributacao_brasileira/` |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────┐
│                     USUÁRIOS (Contadores GUINER)                      │
│                       Browser → HTTPS (TLS 1.2+)                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  plantrib.safion.com.br
                               ▼  Porta 443
┌──────────────────────────────────────────────────────────────────────┐
│  VPS HOSTINGER SAFION (Ubuntu 24.04 — 31.97.253.130 — compartilhada)  │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  TRAEFIK v3 (reverse proxy global EXISTENTE)                    │  │
│  │   ├─ cloud.safion.com.br        → nextcloud-app:80              │  │
│  │   ├─ <n8n-host>                 → n8n:5678                       │  │
│  │   ├─ <evolution-host>           → evolution_api:8080            │  │
│  │   ├─ plantrib.safion.com.br     → plan-trib-web:3000  [NOVO]    │  │
│  │   └─ plantrib.safion.com.br/api → plan-trib-backend:8000 [NOVO] │  │
│  │   TLS: Let's Encrypt via ACME tlschallenge (mytlschallenge)     │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                       Network Docker: root_backend (external)          │
│                                                                        │
│  ┌─────── Stack EXISTENTE Safion (NÃO TOCAR) ──────────────────────┐ │
│  │  nextcloud-app + nextcloud-db + nextcloud-redis + nextcloud-cron │ │
│  │  evolution_api + postgres_evolution + redis (Evolution)          │ │
│  │  n8n                                                              │ │
│  │  (compose em /opt/safion-stack/docker-compose.yml)               │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌─────── Stack NOVA plan-trib (deploy independente) ───────────────┐ │
│  │  Pasta: /opt/plan-trib/   Compose dedicado: docker-compose.yml   │ │
│  │                                                                    │ │
│  │  ┌──────────────────────┐    ┌──────────────────────┐           │ │
│  │  │ plan-trib-backend    │    │ plan-trib-web        │           │ │
│  │  │ (FastAPI + uvicorn)  │    │ (Next.js SSR)        │           │ │
│  │  │ Python 3.12          │    │ Node 20 + React 19   │           │ │
│  │  │ Limits: 1G / 1.0cpu  │    │ Limits: 512M/0.5cpu  │           │ │
│  │  │  ├─ api/             │    │  ├─ app/  (routes)   │           │ │
│  │  │  ├─ services/        │    │  ├─ components/      │           │ │
│  │  │  ├─ parsers/  (SPED) │    │  └─ lib/api.ts       │           │ │
│  │  │  ├─ extractors/(PDF) │    └──────────┬───────────┘           │ │
│  │  │  ├─ engine/  (calc.) │               │ fetch via Traefik      │ │
│  │  │  └─ models/   (ORM)  │               │                        │ │
│  │  └──────────┬───────────┘                                          │ │
│  │             │ asyncpg (rede root_backend)                          │ │
│  │             ▼                                                       │ │
│  │  ┌──────────────────────┐    ┌──────────────────────┐             │ │
│  │  │ plan-trib-db         │    │ plan_trib_uploads    │             │ │
│  │  │ (Postgres 16)        │    │ (Docker volume)      │             │ │
│  │  │ Vol: plan_trib_pgdata│    │ PDFs+SPED .txt brutos│             │ │
│  │  │ NÃO expõe porta host │    │ Mount: backend:/upl  │             │ │
│  │  │ Limits: 1G / 1.0cpu  │    │                       │             │ │
│  │  └──────────────────────┘    └──────────────────────┘             │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Cron 02:00 — /usr/local/bin/backup-infra.sh (EXISTENTE)       │  │
│  │   ESTENDIDO p/ incluir nosso projeto:                           │  │
│  │   • pg_dump nextcloud-db + evolution + plan-trib-db             │  │
│  │   • copia data do Nextcloud + n8n + plan_trib_uploads           │  │
│  │   • tar.zst → /opt/backups/archives/ (retenção 10 dias local)   │  │
│  │   • rclone → Google Drive infra-backups/ (offsite)              │  │
│  │   • TLS: Traefik renova automaticamente (ACME, sem cron extra)  │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼  HTTPS (timeout 30s, retry 2x)
                  ┌────────────────────────────┐
                  │  Google Gemini API         │
                  │  gemini-2.5-flash (PDFs)   │
                  │  Fallback: OpenRouter      │
                  └────────────────────────────┘
```

---

## Components

| # | Componente | Propósito | Tecnologia | Origem |
|---|------------|-----------|------------|--------|
| 1 | **traefik** | Reverse proxy + TLS Let's Encrypt + roteamento por Host | Traefik v3.0 | **Reusado** (já existente na VPS Safion — `/opt/safion-stack/`) |
| 2 | **plan-trib-backend** | API REST, parsers SPED, extractor LLM, engine de cálculo | FastAPI 0.115 + Python 3.12 + uvicorn + Pydantic 2 | **Novo** |
| 3 | **plan-trib-web** | UI de upload, dashboards comparativos, simulação what-if | Next.js 15 + React 19 + TypeScript 5 + TailwindCSS | **Novo** |
| 4 | **plan-trib-db** | Persistência relacional + auditoria (DEDICADO ao projeto) | PostgreSQL 16 | **Novo** (isolado de nextcloud-db e postgres_evolution) |
| 5 | **plan_trib_uploads** | Volume Docker para arquivos brutos (PDFs e SPED) | Docker named volume | **Novo** |
| 6 | **gemini** (externo) | Extração estruturada de PDF (folha, PGDAS-D) | Google Gemini API + Pydantic structured output | Externo |
| 7 | **GitHub Actions** | CI (lint+test) + CD (build imagem + push GHCR + deploy SSH) | GitHub-hosted runners | Novo |
| 8 | **GHCR** | Container registry para imagens versionadas | `ghcr.io/{user}/plan-trib-{backend,web}` | Novo |

**Decisão fundamental:** o projeto **não levanta NGINX próprio nem certbot**. Reaproveita o **Traefik v3 já configurado na VPS** (que serve Nextcloud, n8n e Evolution API), apenas declarando labels de roteamento — minimizando duplicação e padronizando a configuração de TLS.

**Por que NÃO há message broker (Celery/Redis/RabbitMQ):** o volume estimado (escritório, dezenas de empresas, processamento mensal) cabe em processamento síncrono com `BackgroundTasks` do FastAPI. Adicionar broker seria overengineering. Decisão revisitável se volume crescer.

**Coexistência com a stack Safion existente:**

| Aspecto | Tratamento |
|---------|-----------|
| **Compose** | Arquivo separado em `/opt/plan-trib/docker-compose.yml` (nunca tocar `/opt/safion-stack/docker-compose.yml`) |
| **Network** | Conecta-se à network externa `root_backend` já existente (necessário para Traefik enxergar) |
| **Postgres** | Dedicado (`plan-trib-db`) — não compartilha com nextcloud-db nem postgres_evolution |
| **Volumes** | Prefixados (`plan_trib_pgdata`, `plan_trib_uploads`) — sem colisão com `pgdata` (Evolution), `nextcloud_db`, etc. |
| **Container names** | Prefixados `plan-trib-*` |
| **Resource limits** | `deploy.resources.limits` conservadores em todos os containers (evita starvation dos serviços vizinhos) |
| **TZ + restart** | `TZ=America/Sao_Paulo` e `restart: always` (consistente com convenção Safion) |
| **Backup** | Estende `/usr/local/bin/backup-infra.sh` (já cobre Nextcloud+n8n; adicionar `pg_dump plan-trib-db` + cópia do volume `plan_trib_uploads`) |

---

## Key Decisions (ADRs)

### Decision 1: Monorepo (backend + web + infra)

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-28 |

**Context:** Projeto envolve backend Python, frontend Next.js, infra Docker e workflows CI. Precisamos decidir se vão em repos separados ou um único.

**Choice:** Monorepo único no GitHub com pastas `src/` (backend), `web/` (frontend), `docker/`, `.github/`, `migrations/`, `tests/`.

**Rationale:** Time de 1 desenvolvedor; mudanças frequentemente cruzam fronteiras (novo endpoint API + UI consumidora); CI único simplifica versionamento conjunto; OpenAPI gera types do frontend automaticamente.

**Alternatives Rejected:**
1. Repos separados (`plan-trib-api`, `plan-trib-web`) — overhead de coordenação versão; PRs ficam fragmentados
2. Monorepo com Nx/Turborepo — overengineering para 2 deployables

**Consequences:**
- ✅ Single source of truth, PRs atômicos cobrindo full-stack
- ✅ CI/CD simplificado (1 workflow por vez)
- ⚠️ Build do frontend e backend disparam mesmo no push de mudança isolada (mitigação: paths filter no Actions)

---

### Decision 2: SQLAlchemy 2 (async) + Alembic, sem ORM "exótico"

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-28 |

**Context:** Precisamos de ORM para PostgreSQL com tipos `Decimal` precisos, JSONB, transações, migrations.

**Choice:** SQLAlchemy 2.0 em modo async (`AsyncSession` + `asyncpg`). Alembic para migrations. Pydantic 2 para schemas de API (separados dos models ORM).

**Rationale:** SQLAlchemy é o ORM Python mais maduro, suporta tipos avançados (Numeric, JSONB, ENUM, índices funcionais), migrations robustas via Alembic. Async alinha com FastAPI. Separar Pydantic (API) de SQLAlchemy (DB) evita acoplamento e permite evolução independente do schema da API.

**Alternatives Rejected:**
1. SQLModel — atrai pelo mesclamento Pydantic+SQLAlchemy, mas embaralha responsabilidades de validação API vs persistência; documentação imatura
2. Tortoise ORM / Piccolo — comunidade menor, menos features
3. Django ORM — traria framework completo desnecessário

**Consequences:**
- ✅ Tipagem forte em todo o stack
- ✅ Migrations versionadas e reversíveis
- ⚠️ Boilerplate adicional (model + schema + mapper) — mitigação: helper functions

---

### Decision 3: `Decimal(18, 6)` em todos os campos monetários

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-28 |

**Context:** Constraint do DEFINE: erros de arredondamento em cálculos fiscais não são tolerados.

**Choice:** PostgreSQL `NUMERIC(18, 6)` para todos os valores monetários e percentuais. Python `Decimal` end-to-end (parsers, engine, API). Conversão de strings SPED com vírgula → `Decimal` via util `parse_brl_decimal`. Arredondamento `ROUND_HALF_EVEN` apenas na apresentação (2 casas para R$, 4 para alíquotas).

**Rationale:** `NUMERIC(18, 6)` cobre R$ 999.999.999.999,999999 — espaço sobrando para todos os casos do escritório. 6 casas internas evitam acúmulo de erros em multiplicações compostas (ex.: alíquota efetiva × receita × % de repartição).

**Alternatives Rejected:**
1. `float` / `double` — proibido por contraint LGPD/precisão
2. `NUMERIC(15, 2)` (apenas 2 casas) — perde precisão em cálculos intermediários

**Consequences:**
- ✅ Cálculos auditáveis e determinísticos
- ✅ Aderência a normas tributárias
- ⚠️ Performance ligeiramente menor que float (irrelevante neste volume)

---

### Decision 4: Parser SPED "stream + selective registry" com versionamento

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-28 |
| **KB ref** | `kb/tributacao_brasileira/patterns/parsing-sped-pipe.md` |

**Context:** SPED tem ~200 tipos de registros por leiaute, mudança anual de leiaute, tamanho de arquivo grande (centenas KB a vários MB).

**Choice:** Parser que lê arquivo em stream linha-a-linha e usa registry seletivo (`dict[str, Type[SpedRecord]]`) só dos registros do interesse (~10-15 por SPED). Detecção de versão via `0000.cod_ver` seleciona o registry adequado. Encoding `iso-8859-1` obrigatório.

**Rationale:** Modelar 200 registros é desperdício; só precisamos de ~15 (0000, 0140, C100/C170/C190, E110, F550, M200/M210, M600/M610, etc.). Stream evita carregar arquivos grandes na memória.

**Alternatives Rejected:**
1. Lib `python-sped` direto — última atualização desconhecida; risco de leiaute desatualizado
2. Parser monolítico com 200 modelos Pydantic — esforço desproporcional

**Consequences:**
- ✅ Manutenção localizada (adicionar registro = adicionar uma classe)
- ✅ Performance: stream, sem allocação extra
- ⚠️ Adicionar suporte a novos campos requer mudança de código (mitigação: `sped-extractor` para regenerar modelos quando RFB publicar)

---

### Decision 5: LLM (Gemini 2.5 Flash) para extração de PDF, com schema Pydantic

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-28 |
| **KB ref** | `kb/tributacao_brasileira/patterns/extracao-pdf-llm.md` |

**Context:** PDFs de folha (vários sistemas) e PGDAS-D têm leiautes estruturados mas variáveis. Regex frágil; necessitamos robustez.

**Choice:** Google Gemini 2.5 Flash com `response_schema=PydanticModel`, `temperature=0.0`. Validação pós-extração de invariantes (ex.: soma das partes do INSS = total). Fallback OpenRouter (mesmo prompt, modelo equivalente) em caso de falha de Gemini.

**Rationale:** Gemini Flash custa ~US$ 0,001/PDF, latência 2-5s, precisão alta com `temperature=0` e schema enforced. Alinhado com KB existente (Gemini, OpenRouter, Pydantic).

**Alternatives Rejected:**
1. `pdfplumber` + regex — frágil a variações de leiaute
2. AWS Textract / Google DocAI — caro, complexo, vendor lock-in
3. LLM local (Ollama + Llava) — qualidade insuficiente para precisão fiscal exigida

**Consequences:**
- ✅ Robustez a variações de PDF
- ✅ Custo desprezível (escritório: ~1.200 PDFs/ano = ~US$ 1,20)
- ⚠️ Dependência de API externa (mitigação: fallback OpenRouter + retry)
- ⚠️ Custo cresce com volume — irrelevante neste escopo

---

### Decision 6: Engine de cálculo desacoplado (Protocol-based, 3 calculadoras)

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-28 |
| **KB ref** | `kb/tributacao_brasileira/patterns/calculo-multi-regime.md` |

**Context:** Cálculo dos 3 regimes deve ser determinístico, testável e versionável.

**Choice:** 3 classes (`CalculadoraSimples`, `CalculadoraLucroPresumido`, `CalculadoraLucroReal`) implementando `Calculadora` Protocol. Input único `DadosFiscaisCompetencia` (Pydantic). Output uniforme `ResultadoApuracao`. Tabelas (Anexos, % presunção) carregadas no startup do YAML em `kb/tributacao_brasileira/specs/`.

**Rationale:** Permite TDD por regime; possibilita simulação what-if trivial (mutar `DadosFiscaisCompetencia` e re-rodar); evolução para novos regimes (CBS/IBS futuro) é adicionar 4ª classe sem mudar contratos existentes.

**Alternatives Rejected:**
1. Função única com `if regime == ...` — viola SRP, difícil de testar
2. Microserviços por regime — overengineering

**Consequences:**
- ✅ TDD por regime (fixtures de PGDAS-D e SPEDs servem como golden tests)
- ✅ YAML versionável: alíquotas mudam sem redeploy de código
- ✅ Pronto para CBS/IBS quando regulamentar

---

### Decision 7: Autenticação JWT em cookie httpOnly + refresh token

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-28 |

**Context:** App é multi-usuário (escritório). Sem self-service signup. Necessário audit trail.

**Choice:** Login com email+senha (Argon2id hash). JWT (access ~30min, refresh ~7d) em cookies `httpOnly` + `Secure` + `SameSite=Lax`. Endpoint `/auth/refresh` rotaciona tokens. Logout limpa cookies + invalida refresh em DB.

**Rationale:** Cookie httpOnly evita XSS; SameSite mitiga CSRF; refresh permite expiração curta do access sem fricção. Argon2id é o padrão moderno para hash.

**Alternatives Rejected:**
1. Sessions em DB — adiciona round-trip por request
2. JWT em localStorage — vulnerável a XSS
3. OAuth (Google/Microsoft) — overkill para escritório fechado

**Consequences:**
- ✅ Stateless, escalável
- ✅ Audit trail por usuário fácil
- ⚠️ Refresh token em DB requer cleanup de tokens expirados (cron diário)

---

### Decision 8: Reuso do Traefik v3 já existente na VPS Safion (em vez de NGINX próprio)

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted (revisão 2026-04-28 após análise da infra existente) |
| **Date** | 2026-04-28 |

**Context:** Análise da pasta `.claude/documentos/infraestrutura/` revelou que a VPS-alvo (Safion) já possui Traefik v3 configurado, servindo Nextcloud, n8n e Evolution API com TLS Let's Encrypt automático via ACME tlschallenge. Levantar NGINX próprio criaria conflito de portas (80/443) e duplicaria infra.

**Choice:** Reutilizar o **Traefik v3 existente**. Nossa aplicação declara labels Docker (`traefik.enable=true` + roteador + middlewares) e se conecta à network externa `root_backend`. TLS é gerenciado automaticamente pelo Traefik via `mytlschallenge` (certresolver já configurado). Rate limit aplicado via middleware Traefik.

**Rationale:**
- Evita duplicação de reverse proxy na mesma VPS
- Aproveita certificados Let's Encrypt já em uso (renovação automática via Traefik, sem cron extra)
- Padroniza com a convenção Safion (Nextcloud/n8n/Evolution já usam o mesmo padrão de labels)
- Simplifica deploy: nosso compose só precisa subir os containers da app, sem configurar TLS

**Alternatives Rejected:**
1. NGINX próprio em container (proposta original) — conflito de porta com Traefik existente; duplicação de TLS
2. Caddy próprio — mesmo problema
3. Subir Traefik separado em outras portas — fragmentaria operação; sem ganho

**Consequences:**
- ✅ Sem duplicação de reverse proxy
- ✅ TLS automático sem cron adicional
- ✅ Padronização operacional com Safion
- ⚠️ Dependência do Traefik existente: se Safion mudar de proxy, nosso compose precisa ajuste
- ⚠️ Rate limiting fica via middleware Traefik (sintaxe específica) em vez de NGINX `limit_req_zone`

---

### Decision 9: Tabelas tributárias carregadas dos YAMLs do KB no startup

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-28 |

**Context:** Tabelas dos Anexos do Simples, % de presunção LP, leiautes SPED, etc., podem mudar (legislação) sem mudança no código de aplicação.

**Choice:** Engine carrega no startup os YAMLs de `kb/tributacao_brasileira/specs/`. Modelos Pydantic validam estrutura. Cache em memória (sem hit no DB). Endpoint `/admin/reload-tables` (autenticado) permite recarregar sem restart.

**Rationale:** YAML em KB versionado por Git; alterações ficam rastreáveis; engine puro Python não precisa rebuild.

**Alternatives Rejected:**
1. Hard-code no Python — quebra constraint do DEFINE
2. Tabela no DB com seed — adiciona migrations para mudanças simples; YAML é mais legível para o contador

**Consequences:**
- ✅ Atualização de alíquotas via PR + reload, sem redeploy
- ✅ Versionamento histórico via Git
- ⚠️ Volume Docker do backend deve mountar `kb/` em modo read-only

---

### Decision 10: GitHub Actions com 3 workflows + GHCR

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-28 |

**Context:** Precisamos: lint+test em PRs, build de imagens em main, deploy automatizado para VPS.

**Choice:**
- `ci.yml` — em PRs e push: ruff, mypy, pytest, npm test
- `build-push.yml` — em push para `main`: build de imagens backend+web+nginx → push GHCR taggeado com `git sha` + `latest`
- `deploy.yml` — manual ou após `build-push.yml`: SSH na VPS executando `docker compose pull && docker compose up -d`

**Rationale:** Separação de concerns; deploy manual permite controlar timing; SSH key no GitHub Secrets.

**Alternatives Rejected:**
1. Workflow único — dificulta retry parcial
2. Deploy via webhook — adiciona componente; SSH é mais simples
3. Watchtower (auto-pull) — perde controle de quando atualizar

**Consequences:**
- ✅ Pipeline rastreável e revisitável
- ✅ Rollback = `deploy.yml` apontando para SHA anterior
- ⚠️ Secrets (DB password, JWT secret, Gemini API key, SSH key) gerenciados em GitHub Secrets

---

### Decision 11: Coexistência isolada com a stack Safion (Nextcloud/n8n/Evolution)

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-28 |

**Context:** A VPS-alvo já hospeda 3 serviços críticos da Safion (Nextcloud com dados de usuários, n8n com workflows automatizados, Evolution API). Constraint do usuário: o projeto plan-trib **não pode** apresentar risco aos serviços existentes nem causar regressão.

**Choice:**

1. **Compose dedicado**: `/opt/plan-trib/docker-compose.yml` separado do `/opt/safion-stack/docker-compose.yml` existente. Deploy/restart afeta apenas nossos containers.
2. **Postgres dedicado** (`plan-trib-db`): isolado de `nextcloud-db` e `postgres_evolution`. Schema, credenciais, volume independentes.
3. **Volumes prefixados**: `plan_trib_pgdata`, `plan_trib_uploads` — sem colisão com `pgdata` (Evolution), `nextcloud_db`, `n8n_data`, etc.
4. **Container names prefixados**: `plan-trib-backend`, `plan-trib-web`, `plan-trib-db` — sem ambiguidade.
5. **Resource limits explícitos**: `deploy.resources.limits` em cada container (1G/1cpu backend, 512M/0.5cpu web, 1G/1cpu db) — total ~2.5G/2.5cpu, ainda sobra para Nextcloud/n8n/Evolution.
6. **Compartilha apenas**: rede Docker `root_backend` (necessária para Traefik) e o próprio Traefik (via labels). Nada mais é compartilhado.
7. **Backup integrado**: estende o script `/usr/local/bin/backup-infra.sh` existente para incluir nosso Postgres e volume de uploads — aproveita a janela de 02:00 e a integração rclone→GoogleDrive já configurada.
8. **Subdomínio próprio**: `plantrib.safion.com.br` — não impacta DNS de `cloud.safion.com.br` (Nextcloud) nem dos demais.

**Rationale:** A separação de processos (compose), dados (DB+volumes), nomes (containers) e quotas (limits) garante que falha/restart/deploy do projeto plan-trib não impacte os outros serviços. Reutilizar Traefik+rede+backup é eficiente operacionalmente sem comprometer isolamento.

**Alternatives Rejected:**
1. Subir uma nova VPS dedicada — custo desnecessário; recursos da Safion estão folgados
2. Compose unificado com tudo — falha em um serviço afetaria deploy de todos
3. Compartilhar Postgres com Nextcloud — viola isolamento de dados sensíveis (LGPD)

**Consequences:**
- ✅ Risco zero de impacto cruzado em operação normal
- ✅ Deploy independente (rollback do plan-trib não afeta Safion)
- ✅ Backup unificado (operacionalmente simples)
- ⚠️ Dependência operacional: se Traefik cair, nossa app fica inacessível (mesmo risco que Nextcloud/n8n; mitigação é manter Traefik saudável)
- ⚠️ Compartilhamento de recursos da VPS (CPU/RAM/disk) exige monitoramento; resource limits servem como guarda-corpo

---

### Decision 12: Soft delete + audit log imutável

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-28 |

**Context:** LGPD exige rastreabilidade de acessos e mudanças; "exclusão" não pode perder histórico fiscal.

**Choice:** Tabelas principais (`empresa`, `documento`, `apuracao`) têm `deleted_at TIMESTAMPTZ NULL`. Queries default filtram `WHERE deleted_at IS NULL`. Tabela `audit_log` é append-only (sem UPDATE/DELETE), gravada em todo acesso/mutação.

**Rationale:** Soft delete preserva histórico de planejamentos antigos; audit log atende LGPD e permite forense.

**Consequences:**
- ✅ Compliance LGPD básico
- ✅ Recuperação de dados "deletados" possível
- ⚠️ Storage cresce com tempo (mitigação: política de retenção do audit_log — ex.: 7 anos)

---

## File Manifest

> Files marcados com `[*]` são críticos para o MVP. Files agrupados por convenção (ex.: "13 models") estão listados por pasta no Build phase.

| # | Arquivo | Ação | Propósito | Agente | Dependências |
|---|---------|------|-----------|--------|--------------|
| **— Raiz / Config —** | | | | | |
| 1 | `README.md` | Create | Setup, dev workflow, deploy | @code-documenter | — |
| 2 | `.env.example` | Create | Variáveis de ambiente esperadas | @python-developer | — |
| 3 | `.gitignore` | Create | Ignora `.env`, `__pycache__`, `node_modules`, etc. | @python-developer | — |
| 4 | `pyproject.toml` | Create | Deps Python + ruff + pytest config | @python-developer | — |
| 5 | `Makefile` | Create | Comandos `make dev`, `make test`, `make migrate` | @python-developer | — |
| **— Docker / Infra local e prod —** | | | | | |
| 6 [*] | `docker-compose.yml` | Create | Prod: backend + web + db; Traefik labels; network `root_backend` external; resource limits | @infra-deployer | — |
| 7 [*] | `docker-compose.dev.yml` | Create | Override dev (WSL): hot reload, mount source, sem Traefik (porta direta) | @infra-deployer | 6 |
| 8 | `docker-compose.test.yml` | Create | Containers efêmeros para CI (DB efêmero) | @infra-deployer | 6 |
| 9 [*] | `docker/backend.Dockerfile` | Create | Multi-stage Python 3.12 + uv | @python-developer | — |
| 10 [*] | `docker/web.Dockerfile` | Create | Multi-stage Node 20 + Next.js standalone | @python-developer | — |
| 11 | `ops/extend-backup-infra.sh.patch` | Create | Patch documentando como estender `/usr/local/bin/backup-infra.sh` (Safion existente) p/ incluir `pg_dump plan-trib-db` + cópia volume `plan_trib_uploads` | @infra-deployer | — |
| 12 | `ops/deploy-vps.sh` | Create | Script de deploy via SSH (executado pelo Actions): `cd /opt/plan-trib && docker compose pull && docker compose up -d` | @infra-deployer | 6 |
| 13 | `ops/dns-setup.md` | Create | Documentação do registro DNS A `plantrib.safion.com.br` → `31.97.253.130` | @code-documenter | — |
| **— GitHub Actions —** | | | | | |
| 14 [*] | `.github/workflows/ci.yml` | Create | Lint + test em PR | @ci-cd-specialist | 4, 9, 10 |
| 15 [*] | `.github/workflows/build-push.yml` | Create | Build e push GHCR em main | @ci-cd-specialist | 9, 10, 11 |
| 16 [*] | `.github/workflows/deploy.yml` | Create | SSH deploy na VPS | @ci-cd-specialist | 6, 15 |
| **— Backend: entrypoint, config, deps —** | | | | | |
| 17 [*] | `src/main.py` | Create | FastAPI app, lifespan, middlewares | @python-developer | 18-22 |
| 18 [*] | `src/config.py` | Create | `pydantic-settings` (env vars) | @python-developer | — |
| 19 [*] | `src/db.py` | Create | `AsyncSession` factory + engine | @python-developer | 18 |
| 20 [*] | `src/deps.py` | Create | FastAPI deps (auth user, db session) | @python-developer | 19, 35 |
| 21 | `src/middleware.py` | Create | Logging estruturado + audit | @python-developer | 19 |
| 22 | `src/exceptions.py` | Create | Exception handlers padronizados | @python-developer | — |
| **— Backend: Models (SQLAlchemy 2 async) —** | | | | | |
| 23 [*] | `src/models/__init__.py` | Create | Import de todos os models | @python-developer | 24-37 |
| 24 [*] | `src/models/base.py` | Create | `Base`, mixins (timestamps, soft delete) | @python-developer | — |
| 25 [*] | `src/models/usuario.py` | Create | `Usuario` (email, senha hash Argon2id) | @python-developer | 24 |
| 26 [*] | `src/models/grupo.py` | Create | `GrupoEmpresas` | @python-developer | 24 |
| 27 [*] | `src/models/empresa.py` | Create | `Empresa` (CNPJ, regime atual, tipo: matriz/filial/independente, FK grupo) | @python-developer | 24, 26 |
| 28 [*] | `src/models/documento.py` | Create | `Documento` (raw file metadata: tipo, hash, status processamento) | @python-developer | 24, 27 |
| 29 [*] | `src/models/periodo.py` | Create | `Periodo` (competência ano/mês) | @python-developer | 24, 27 |
| 30 [*] | `src/models/faturamento.py` | Create | `FaturamentoMensal` (por CFOP/CST, vindo do SPED) | @python-developer | 24, 27, 29 |
| 31 [*] | `src/models/credito.py` | Create | `CreditoPISCOFINS`, `CreditoICMS` | @python-developer | 24, 27, 29 |
| 32 [*] | `src/models/folha.py` | Create | `FolhaMensal` (totalizadores extraídos do PDF) | @python-developer | 24, 27, 29 |
| 33 [*] | `src/models/pgdas.py` | Create | `PgdasDeclaracao` (PDF extraído) | @python-developer | 24, 27, 29 |
| 34 [*] | `src/models/despesa.py` | Create | `DespesaSintetica` (Adm/Com/Trib, manual) | @python-developer | 24, 27, 29 |
| 35 [*] | `src/models/apuracao.py` | Create | `Apuracao` (resultado dos 3 regimes por período) | @python-developer | 24, 27, 29 |
| 36 [*] | `src/models/cenario.py` | Create | `Cenario` (overrides nomeados para what-if) | @python-developer | 24, 27, 29 |
| 37 [*] | `src/models/audit_log.py` | Create | `AuditLog` (append-only) | @python-developer | 24, 25 |
| **— Backend: Schemas (Pydantic) —** | | | | | |
| 38 [*] | `src/schemas/*.py` | Create | 1 arquivo por módulo (request/response, separados de Models) | @python-developer | 23-37 |
| **— Backend: API endpoints —** | | | | | |
| 39 [*] | `src/api/auth.py` | Create | `/auth/login`, `/auth/refresh`, `/auth/logout` | @python-developer | 20, 25, 38 |
| 40 [*] | `src/api/grupos.py` | Create | CRUD `/grupos` | @python-developer | 20, 26, 38 |
| 41 [*] | `src/api/empresas.py` | Create | CRUD `/empresas` (filtros por grupo) | @python-developer | 20, 27, 38 |
| 42 [*] | `src/api/documentos.py` | Create | `POST /documentos/upload`, listagem, status processamento | @python-developer | 20, 28, 56-58, 38 |
| 43 [*] | `src/api/despesas.py` | Create | CRUD despesas sintéticas + endpoint "replicar mês" | @python-developer | 20, 34, 38 |
| 44 [*] | `src/api/apuracao.py` | Create | `POST /apuracao/calcular`, listar histórico | @python-developer | 20, 35, 60, 38 |
| 45 [*] | `src/api/simulacao.py` | Create | `POST /simulacao` (cenário ad-hoc), `POST /cenarios` (salvar) | @python-developer | 20, 36, 60, 38 |
| 46 | `src/api/usuarios.py` | Create | CRUD `/usuarios` (admin only) | @python-developer | 20, 25, 38 |
| 47 | `src/api/admin.py` | Create | `/admin/reload-tables` | @python-developer | 20, 64 |
| **— Backend: Services —** | | | | | |
| 48 [*] | `src/services/auth_service.py` | Create | Hash Argon2id, JWT issue/verify | @python-developer | 25 |
| 49 [*] | `src/services/ingestao_service.py` | Create | Orquestra parsing/extração via BackgroundTasks | @python-developer | 28, 50-58 |
| 50 [*] | `src/services/audit_service.py` | Create | Helper para gravar `AuditLog` | @python-developer | 37 |
| 51 [*] | `src/services/comparador_service.py` | Create | Engine.apurar() para os 3 regimes; consolidação por grupo | @python-developer | 60-63 |
| **— Backend: Parsers SPED —** | | | | | |
| 52 [*] | `src/parsers/__init__.py` | Create | Detecção de versão e seleção de registry | @extraction-specialist | — |
| 53 [*] | `src/parsers/base.py` | Create | `SpedRecord`, `RegistryParser`, helpers | @extraction-specialist | — |
| 54 [*] | `src/parsers/sped_fiscal/v019.py` | Create | Modelos Pydantic dos registros 0000, C100, C170, C190, E110, H010 | @extraction-specialist | 53 |
| 55 [*] | `src/parsers/sped_fiscal/parser.py` | Create | Function `parse_efd_icms_ipi(path) -> ParsedSpedFiscal` | @extraction-specialist | 53, 54 |
| 56 [*] | `src/parsers/sped_contribuicoes/v006.py` | Create | Modelos dos registros 0000, 0110, 0140, F550, M200/M210, M600/M610 | @extraction-specialist | 53 |
| 57 [*] | `src/parsers/sped_contribuicoes/parser.py` | Create | Function `parse_efd_contribuicoes(path) -> ParsedSpedContrib` | @extraction-specialist | 53, 56 |
| **— Backend: Extractors LLM —** | | | | | |
| 58 [*] | `src/extractors/base.py` | Create | Cliente Gemini, fallback OpenRouter, retry com backoff | @llm-specialist | 18 |
| 59 [*] | `src/extractors/folha_extractor.py` | Create | Extrai PDF folha → `FolhaTotalizadores` (Pydantic) | @llm-specialist | 58 |
| 60 [*] | `src/extractors/pgdas_extractor.py` | Create | Extrai PGDAS-D → `PgdasDeclaracaoExtraida` | @llm-specialist | 58 |
| **— Backend: Engine de cálculo —** | | | | | |
| 61 [*] | `src/engine/inputs.py` | Create | `DadosFiscaisCompetencia` (Pydantic) | @python-developer | — |
| 62 [*] | `src/engine/outputs.py` | Create | `Tributos`, `ResultadoApuracao` | @python-developer | — |
| 63 [*] | `src/engine/interface.py` | Create | `Calculadora` Protocol | @python-developer | 61, 62 |
| 64 [*] | `src/engine/tabelas.py` | Create | Loader dos YAMLs (`kb/tributacao_brasileira/specs/*.yaml`) | @python-developer | — |
| 65 [*] | `src/engine/normalizador.py` | Create | Converte rows DB → `DadosFiscaisCompetencia` | @python-developer | 30-34, 61 |
| 66 [*] | `src/engine/simples.py` | Create | `CalculadoraSimples` (Anexos + Fator R + sublimites) | @python-developer | 61-64 |
| 67 [*] | `src/engine/lucro_presumido.py` | Create | `CalculadoraLucroPresumido` | @python-developer | 61-64 |
| 68 [*] | `src/engine/lucro_real.py` | Create | `CalculadoraLucroReal` | @python-developer | 61-64 |
| **— Backend: Utils —** | | | | | |
| 69 [*] | `src/utils/decimal_utils.py` | Create | `parse_brl_decimal("1,23") -> Decimal` | @python-developer | — |
| 70 | `src/utils/datetime_utils.py` | Create | Parse `DDMMAAAA` SPED → date | @python-developer | — |
| **— Migrations —** | | | | | |
| 71 [*] | `migrations/env.py` | Create | Alembic env (async) | @python-developer | 19, 23 |
| 72 [*] | `migrations/versions/0001_initial.py` | Create | Schema inicial completo | @python-developer | 23-37, 71 |
| **— Tests —** | | | | | |
| 73 [*] | `tests/conftest.py` | Create | Fixtures: db efêmero, sample SPEDs/PDFs | @test-generator | — |
| 74 [*] | `tests/unit/parsers/test_sped_fiscal.py` | Create | Parsing dos 47 fixtures reais (WIBE) | @test-generator | 55, 73 |
| 75 [*] | `tests/unit/parsers/test_sped_contrib.py` | Create | Parsing dos 13 fixtures reais (WIBE) | @test-generator | 57, 73 |
| 76 [*] | `tests/unit/extractors/test_folha_mock.py` | Create | Mock Gemini, valida schema Pydantic | @test-generator | 59, 73 |
| 77 [*] | `tests/unit/extractors/test_pgdas_mock.py` | Create | Mock Gemini, valida com 2 PGDAS reais | @test-generator | 60, 73 |
| 78 [*] | `tests/unit/engine/test_simples.py` | Create | Casos de borda dos 5 Anexos + Fator R + sublimite | @test-generator | 66, 73 |
| 79 [*] | `tests/unit/engine/test_lucro_presumido.py` | Create | Cruzamento com SPED M210/M610/E110 do WIBE | @test-generator | 67, 73 |
| 80 [*] | `tests/unit/engine/test_lucro_real.py` | Create | Casos sintéticos + invariantes | @test-generator | 68, 73 |
| 81 [*] | `tests/integration/test_api_apuracao.py` | Create | E2E ingestão → cálculo → comparativo | @test-generator | 44, 73 |
| **— Frontend (Next.js) —** | | | | | |
| 82 [*] | `web/package.json` | Create | Deps: next, react, tailwindcss, swr, zod | @python-developer | — |
| 83 | `web/next.config.js` | Create | `output: 'standalone'` para Docker | @python-developer | — |
| 84 | `web/tsconfig.json` | Create | Strict mode + path aliases | @python-developer | — |
| 85 [*] | `web/lib/api.ts` | Create | Client tipado (gerado do OpenAPI) | @python-developer | 17 |
| 86 [*] | `web/lib/auth.ts` | Create | Helpers de sessão (cookies httpOnly) | @python-developer | 39 |
| 87 [*] | `web/app/layout.tsx` | Create | Layout raiz + tema | @python-developer | — |
| 88 [*] | `web/app/login/page.tsx` | Create | Página login | @python-developer | 86 |
| 89 [*] | `web/app/(app)/grupos/page.tsx` | Create | Lista/CRUD grupos | @python-developer | 85, 86 |
| 90 [*] | `web/app/(app)/empresas/[id]/page.tsx` | Create | Detalhe empresa + uploads + análise | @python-developer | 85, 86 |
| 91 [*] | `web/app/(app)/documentos/page.tsx` | Create | Upload de SPED + PDFs + status | @python-developer | 42, 85 |
| 92 [*] | `web/app/(app)/comparativo/[empresa_id]/page.tsx` | Create | Tabela comparativa 3 regimes + gráficos | @python-developer | 44, 85 |
| 93 [*] | `web/app/(app)/simulacao/page.tsx` | Create | Form de simulação what-if + recalc on change | @python-developer | 45, 85 |
| 94 [*] | `web/components/DespesasReplicador.tsx` | Create | Form despesas + botão "Replicar p/ todos os meses" | @python-developer | 43 |
| 95 [*] | `web/components/ComparativoTable.tsx` | Create | Componente de tabela 3 regimes lado a lado | @python-developer | — |

**Total Files:** 95 (62 marcados como críticos para MVP)

---

## Agent Assignment Rationale

| Agente | Files | Justificativa |
|--------|-------|---------------|
| **@python-developer** | 1-5, 17-51, 61-72, 82-95 | Backend FastAPI + ORM + frontend Next.js (full-stack TypeScript/Python) |
| **@infra-deployer** | 6-13 | Docker Compose, NGINX, scripts de ops |
| **@ci-cd-specialist** | 14-16 | GitHub Actions workflows |
| **@extraction-specialist** | 52-57 | Parsing de formatos estruturados (SPED) |
| **@llm-specialist** | 58-60 | Integração com Gemini, prompts, structured output |
| **@test-generator** | 73-81 | Fixtures, pytest, mocks, golden tests |
| **@code-documenter** | 1 | README e docs internos |
| **@code-reviewer** | (transversal) | Revisão final pré-merge de cada PR |

---

## Code Patterns

### Pattern 1: SQLAlchemy 2 Model com Soft Delete

```python
# src/models/base.py
from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Numeric, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

# src/models/empresa.py
from sqlalchemy import String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

class TipoEmpresa(str, enum.Enum):
    MATRIZ = "matriz"
    FILIAL = "filial"
    INDEPENDENTE = "independente"

class RegimeTributario(str, enum.Enum):
    SIMPLES = "SIMPLES"
    LUCRO_PRESUMIDO = "LP"
    LUCRO_REAL = "LR"

class Empresa(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "empresa"
    id: Mapped[int] = mapped_column(primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, index=True)  # só dígitos
    razao_social: Mapped[str] = mapped_column(String(255))
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupo.id"))
    tipo: Mapped[TipoEmpresa] = mapped_column(SAEnum(TipoEmpresa))
    regime_atual: Mapped[RegimeTributario] = mapped_column(SAEnum(RegimeTributario))
    grupo: Mapped["Grupo"] = relationship(back_populates="empresas")
```

### Pattern 2: Endpoint FastAPI async com auth + audit

```python
# src/api/empresas.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.deps import get_db, get_current_user
from src.models.empresa import Empresa
from src.models.usuario import Usuario
from src.schemas.empresa import EmpresaCreate, EmpresaResponse
from src.services.audit_service import audit

router = APIRouter(prefix="/empresas", tags=["empresas"])

@router.post("", response_model=EmpresaResponse, status_code=201)
async def criar_empresa(
    payload: EmpresaCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> EmpresaResponse:
    empresa = Empresa(**payload.model_dump())
    db.add(empresa)
    await db.flush()  # popula o id sem commit ainda
    await audit(db, user, "create", "empresa", empresa.id)
    await db.commit()
    return EmpresaResponse.model_validate(empresa)
```

### Pattern 3: Parser SPED stream-based com Decimal

```python
# src/parsers/base.py
from decimal import Decimal
from datetime import date
from pathlib import Path
from typing import ClassVar, Type, Iterator
from pydantic import BaseModel, ConfigDict

def parse_brl_decimal(s: str | None) -> Decimal | None:
    if not s:
        return None
    return Decimal(s.replace(",", "."))

def parse_sped_date(s: str) -> date:
    return date(int(s[4:8]), int(s[2:4]), int(s[0:2]))

class SpedRecord(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    REG: ClassVar[str]

    @classmethod
    def from_line(cls, line: str) -> "SpedRecord":
        parts = line.strip().strip("|").split("|")
        # subclasses overridem para mapear parts → campos
        raise NotImplementedError

def stream_records(path: Path, registry: dict[str, Type[SpedRecord]]) -> Iterator[SpedRecord]:
    with path.open("r", encoding="iso-8859-1") as f:
        for line in f:
            if not line.startswith("|"):
                continue  # ignora certificado ICP-Brasil ao final
            reg_type = line[1:].split("|", 1)[0]
            if reg_type in registry:
                yield registry[reg_type].from_line(line)
```

### Pattern 4: Extractor LLM com Pydantic + retry

```python
# src/extractors/base.py
import asyncio
from pathlib import Path
from typing import Type, TypeVar
from google import genai
from google.genai import types
from pydantic import BaseModel
from src.config import settings

T = TypeVar("T", bound=BaseModel)

_client = genai.Client(api_key=settings.gemini_api_key)

async def extract_pdf(
    pdf_path: Path,
    schema: Type[T],
    prompt: str,
    model: str = "gemini-2.5-flash",
    max_retries: int = 2,
) -> T:
    pdf_bytes = pdf_path.read_bytes()
    last_err: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = await _client.aio.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.0,
                ),
            )
            return schema.model_validate_json(response.text)
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
    raise RuntimeError(f"LLM extraction failed after {max_retries+1} attempts") from last_err
```

### Pattern 5: docker-compose.yml (produção — VPS Safion, integrado com Traefik existente)

```yaml
# /opt/plan-trib/docker-compose.yml
# Coexiste com /opt/safion-stack/docker-compose.yml (Nextcloud/n8n/Evolution).
# Compartilha APENAS: network root_backend (necessária p/ Traefik enxergar).

services:
  plan-trib-backend:
    image: ghcr.io/${GITHUB_USER}/plan-trib-backend:${TAG:-latest}
    container_name: plan-trib-backend
    restart: always
    env_file: .env
    environment:
      - TZ=America/Sao_Paulo
    volumes:
      - plan_trib_uploads:/uploads
      - ./kb:/app/kb:ro   # tabelas tributárias (read-only)
    depends_on:
      - plan-trib-db
    networks:
      - root_backend
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=root_backend"
      - "traefik.http.routers.plan-trib-api.rule=Host(`plantrib.safion.com.br`) && PathPrefix(`/api`)"
      - "traefik.http.routers.plan-trib-api.entrypoints=websecure"
      - "traefik.http.routers.plan-trib-api.tls=true"
      - "traefik.http.routers.plan-trib-api.tls.certresolver=mytlschallenge"
      - "traefik.http.services.plan-trib-api.loadbalancer.server.port=8000"
      # Rate limit no /api/auth/login para mitigar brute force
      - "traefik.http.middlewares.plan-trib-ratelimit.ratelimit.average=10"
      - "traefik.http.middlewares.plan-trib-ratelimit.ratelimit.burst=20"

  plan-trib-web:
    image: ghcr.io/${GITHUB_USER}/plan-trib-web:${TAG:-latest}
    container_name: plan-trib-web
    restart: always
    env_file: .env.web
    environment:
      - TZ=America/Sao_Paulo
    networks:
      - root_backend
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=root_backend"
      - "traefik.http.routers.plan-trib-web.rule=Host(`plantrib.safion.com.br`)"
      - "traefik.http.routers.plan-trib-web.entrypoints=websecure"
      - "traefik.http.routers.plan-trib-web.tls=true"
      - "traefik.http.routers.plan-trib-web.tls.certresolver=mytlschallenge"
      - "traefik.http.services.plan-trib-web.loadbalancer.server.port=3000"
      # Headers de segurança espelhando padrão Safion (Nextcloud)
      - "traefik.http.middlewares.plan-trib-headers.headers.STSSeconds=315360000"
      - "traefik.http.middlewares.plan-trib-headers.headers.browserXSSFilter=true"
      - "traefik.http.middlewares.plan-trib-headers.headers.contentTypeNosniff=true"
      - "traefik.http.middlewares.plan-trib-headers.headers.forceSTSHeader=true"
      - "traefik.http.middlewares.plan-trib-headers.headers.SSLRedirect=true"
      - "traefik.http.middlewares.plan-trib-headers.headers.STSIncludeSubdomains=true"
      - "traefik.http.middlewares.plan-trib-headers.headers.STSPreload=true"
      - "traefik.http.middlewares.plan-trib-headers.headers.referrerPolicy=no-referrer"
      - "traefik.http.routers.plan-trib-web.middlewares=plan-trib-headers"

  plan-trib-db:
    image: postgres:16
    container_name: plan-trib-db
    restart: always
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=plan_trib
      - POSTGRES_INITDB_ARGS=--data-checksums
      - TZ=America/Sao_Paulo
    volumes:
      - plan_trib_pgdata:/var/lib/postgresql/data
    networks:
      - root_backend
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
    # NÃO expor 5432 ao host — acesso só via rede docker root_backend

volumes:
  plan_trib_pgdata:
  plan_trib_uploads:

networks:
  root_backend:
    external: true   # Rede já criada pela stack Safion existente
```

**Observações importantes:**
- Não há container `nginx` (Traefik existente faz o roteamento)
- Não há volume `letsencrypt` (Traefik existente já tem `traefik_data:/letsencrypt`)
- `kb/` é mountado read-only no container backend a partir de cópia do `.claude/kb/tributacao_brasileira/specs/*.yaml` no diretório de deploy

### Pattern 6: GitHub Actions — build & push

```yaml
# .github/workflows/build-push.yml
name: Build and Push Images
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build & push backend
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/backend.Dockerfile
          push: true
          tags: |
            ghcr.io/${{ github.repository_owner }}/plan-trib-backend:${{ github.sha }}
            ghcr.io/${{ github.repository_owner }}/plan-trib-backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
      # idem para web e nginx
```

---

## Data Flow

```text
1. Usuário faz LOGIN
   │  POST /api/auth/login {email, senha}
   ▼
2. backend valida com Argon2id, emite JWT (access + refresh em cookies httpOnly)
   │
   ▼
3. Usuário cadastra GRUPO + EMPRESAS (CNPJs, regime atual, tipo matriz/filial)
   │  POST /api/grupos, POST /api/empresas
   ▼
4. Usuário UPLOAD documentos
   │  POST /api/documentos/upload (multipart) — SPED .txt, PDFs folha, PGDAS-D
   ▼
5. backend persiste raw em volume `uploads/`, cria registro `Documento` (status=PENDENTE),
   │  dispara BackgroundTask de processamento
   ▼
6. Background processing:
   │  ├─ Tipo SPED Fiscal → src.parsers.sped_fiscal.parse() → upsert FaturamentoMensal,
   │  │                                                        CreditoICMS
   │  ├─ Tipo SPED Contribuições → parse() → upsert CreditoPISCOFINS, ApuracaoExistente
   │  ├─ Tipo PDF Folha → src.extractors.folha_extractor → upsert FolhaMensal
   │  └─ Tipo PDF PGDAS-D → src.extractors.pgdas_extractor → upsert PgdasDeclaracao
   │  → marca Documento.status = PROCESSADO (ou ERRO com mensagem)
   ▼
7. Usuário preenche DESPESAS sintéticas (Adm/Com/Trib) com replicador "todos os meses"
   │  PUT /api/despesas {empresa_id, periodo, valores...}
   ▼
8. Usuário clica em "COMPARAR REGIMES"
   │  POST /api/apuracao/calcular {empresa_id, periodo_de, periodo_ate}
   ▼
9. backend.comparador_service:
   │  ├─ Carrega DadosFiscaisCompetencia para cada mês via Normalizador
   │  ├─ Para cada calculadora (Simples, LP, LR): apurar(dados) → ResultadoApuracao
   │  ├─ Persiste 3 registros Apuracao por mês
   │  └─ Retorna comparativo agregado (12 meses × 3 regimes)
   ▼
10. UI renderiza tabela comparativa + gráficos + recomendação automática
    │  (regime de menor carga)
    ▼
11. (Opcional) Usuário simula CENÁRIO what-if
    │  POST /api/simulacao {empresa_id, overrides: {folha_bruta: ..., despesas: ...}}
    ▼
12. backend re-executa engine sobre dados sobrepostos, retorna sem persistir
    │  (até usuário salvar como Cenario nomeado: POST /api/cenarios)
    ▼
13. Audit log gravado em CADA acesso/mutação (passos 1, 4, 7, 8, 11, 12)
```

---

## Integration Points

| Sistema externo | Tipo de integração | Autenticação | Mitigação de falha |
|-----------------|--------------------|--------------|--------------------|
| **Google Gemini API** | HTTPS REST via `google-genai` SDK | API key (env var `GEMINI_API_KEY`) | Retry com backoff (2x); fallback OpenRouter; timeout 30s; status do `Documento` marca ERRO se falhar |
| **OpenRouter (fallback)** | HTTPS REST | API key (env var `OPENROUTER_API_KEY`) | Mesmo schema Pydantic; ativado apenas se Gemini falhar |
| **Traefik (existente na VPS)** | Labels Docker no compose | (nenhuma — descoberta via socket Docker do Traefik) | TLS via ACME tlschallenge (`mytlschallenge`) já configurado; renovação automática gerenciada pelo Traefik existente |
| **GitHub Actions → VPS Safion** | SSH para `root@31.97.253.130` + `cd /opt/plan-trib && docker compose pull && up -d` | SSH key em `secrets.SSH_PRIVATE_KEY` | `deploy.yml` é manual ou disparado após `build-push.yml`; só toca containers `plan-trib-*` |
| **GHCR (GitHub Container Registry)** | Docker push/pull | `GITHUB_TOKEN` (push CI), `secrets.GHCR_PAT` (pull na VPS via `docker login ghcr.io`) | Tags `:latest` + `:{sha}` para rollback fácil |
| **Backup script existente** (`/usr/local/bin/backup-infra.sh`) | Bash + Docker exec + rclone | (nenhuma — roda como root via cron) | Estendido para incluir `pg_dump plan-trib-db` e `tar` do volume `plan_trib_uploads`; offsite via Google Drive já configurado |

---

## Testing Strategy

| Tipo | Escopo | Arquivos | Ferramentas | Meta de cobertura |
|------|--------|----------|-------------|-------------------|
| **Unit (parsers)** | Parsing dos 47 SPEDs Fiscal + 13 SPEDs Contrib reais (WIBE) | `tests/unit/parsers/test_*.py` | pytest + fixtures linkadas a `.claude/documentos/` | 100% dos registros do interesse |
| **Unit (extractors)** | Schemas Pydantic, mocks Gemini, parsing JSON | `tests/unit/extractors/test_*.py` | pytest + `respx`/`pytest-mock` para mock HTTP do SDK | 90% — mock LLM evita custo |
| **Unit (engine)** | 3 calculadoras + cruzamento c/ valores reais (PGDAS-D para Simples; M210/M610 para LP) | `tests/unit/engine/test_*.py` | pytest paramétrizado; golden files | **≥ 80% (módulo crítico)** |
| **Integration (API)** | Fluxo upload → parsing → cálculo → response | `tests/integration/test_api_apuracao.py` | pytest + `httpx.AsyncClient` + DB efêmero | Caminho feliz + 3 erros principais |
| **E2E (manual no MVP)** | Fluxo completo no browser (login → upload → comparativo → exportação) | Checklist em `tests/e2e/checklist.md` | Manual; Playwright em fase 2 | Smoke test antes de cada deploy |
| **Snapshot** | Output JSON do `/apuracao/calcular` para fixtures conhecidos | `tests/snapshots/` | `syrupy` | Detecta regressão silenciosa em mudanças no engine |

**Fixtures críticas (em `tests/fixtures/`):**
- Symlinks para `.claude/documentos/` (47 SPED Fiscal + 13 Contrib + 5 PDFs folha + 2 PGDAS-D)
- Golden file: apuração esperada do WIBE para jan/2025 (LP) com valores extraídos manualmente

---

## Error Handling

| Tipo de erro | Estratégia | Retry? |
|--------------|-----------|--------|
| **SPED com encoding inválido** | Detecta antes de parsing; `Documento.status = ERRO`, mensagem ao usuário | Não |
| **SPED com leiaute desconhecido** | Erro `UnsupportedLayoutError`; status ERRO | Não — exige update de código |
| **PDF folha mal formado / não-leitura LLM** | Retry 2x com backoff; depois fallback OpenRouter; depois ERRO | Sim (2x) |
| **Falha API Gemini (5xx, timeout)** | Retry 2x com backoff exponencial; fallback OpenRouter | Sim |
| **CNPJ inválido (≠ 14 dígitos)** | 400 Bad Request; mensagem clara | Não |
| **Cálculo com receita 0** | Retorna `ResultadoApuracao` com tributos zerados; warning no payload | Não |
| **DB connection lost** | Retry com backoff (3x); se persistir, 503 Service Unavailable | Sim |
| **JWT expirado** | 401; frontend chama `/auth/refresh` automaticamente | Sim (transparente ao usuário) |
| **Conflito multi-usuário (cenário simultâneo)** | Optimistic locking via `version` column; 409 com diff | Não |
| **Upload > 50 MB** | Rejeita no NGINX (`client_max_body_size`); 413 | Não |

---

## Configuration

> Settings via `pydantic-settings` lendo `.env`. Valores sensíveis em GitHub Secrets para CI/deploy.

| Chave | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `DATABASE_URL` | string | `postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@plan-trib-db:5432/plan_trib` | Conexão via rede docker `root_backend` (host = nome do container) |
| `DB_USER` | string | (obrigatório) | Usuário Postgres do projeto |
| `DB_PASSWORD` | string | (obrigatório) | Senha Postgres (32+ chars random) |
| `JWT_SECRET` | string | (obrigatório) | Secret para assinatura JWT (gerar 32+ bytes random) |
| `JWT_ACCESS_TTL_MINUTES` | int | `30` | TTL access token |
| `JWT_REFRESH_TTL_DAYS` | int | `7` | TTL refresh token |
| `GEMINI_API_KEY` | string | (obrigatório) | Chave Gemini API |
| `GEMINI_MODEL` | string | `gemini-2.5-flash` | Modelo padrão |
| `OPENROUTER_API_KEY` | string | (opcional) | Chave fallback |
| `OPENROUTER_MODEL` | string | `google/gemini-2.5-flash` | Modelo fallback no OpenRouter |
| `UPLOADS_DIR` | path | `/uploads` | Volume Docker mountado |
| `KB_DIR` | path | `/app/kb` | Volume read-only com YAMLs |
| `MAX_UPLOAD_SIZE_MB` | int | `50` | Validação de upload |
| `LOG_LEVEL` | string | `INFO` | Logging |
| `APP_DOMAIN` | string | `plantrib.safion.com.br` | Domínio público; usado em links/cookies |
| `CORS_ORIGINS` | list[str] | `[]` | Traefik faz reverse proxy mesmo host; CORS desabilitado em prod |
| `TZ` | string | `America/Sao_Paulo` | Timezone (consistente com infra Safion) |
| `GITHUB_USER` | string | (obrigatório p/ pull) | User/org do GHCR para resolver imagem em prod |
| `TAG` | string | `latest` | Tag da imagem (use `${SHA}` para fixar versão) |
| `SENTRY_DSN` | string | (opcional) | Errors em produção (fase 2) |

---

## Security Considerations

- **LGPD**: Dados sensíveis (CPFs, salários, faturamento) criptografados em repouso via `pgcrypto` (campos selecionados). TLS 1.2+ obrigatório em trânsito — gerenciado pelo **Traefik existente** com Let's Encrypt automático (mesma infra que protege Nextcloud).
- **Auth**: Argon2id para hash de senha (parâmetros: `time_cost=2, memory_cost=64MiB, parallelism=2`). Nunca log de senhas/tokens.
- **JWT**: Cookies `httpOnly` + `Secure` + `SameSite=Lax`. Secret rotacionável (suporte a múltiplos secrets simultâneos para rotação sem invalidar sessões).
- **Rate limit**: Middleware Traefik (`plan-trib-ratelimit`) aplicado ao `/api/auth/login` — 10 req/s média, 20 burst. Login com 5 falhas em 15min bloqueia conta por 15min (lógica adicional no backend).
- **CSRF**: SameSite=Lax mitiga; endpoints mutativos exigem header `X-Requested-With: XMLHttpRequest`.
- **SQL Injection**: SQLAlchemy 2 com bind parameters; nunca f-strings em SQL.
- **XSS**: Next.js escapa por default; nunca `dangerouslySetInnerHTML` com input do usuário.
- **Postgres NÃO exposto à internet**: Container `plan-trib-db` em rede docker `root_backend`; porta 5432 não publicada no host. Acesso só via outros containers (backend, scripts de backup via `docker exec`).
- **Isolamento de DBs entre projetos**: `plan-trib-db` é instância dedicada — não compartilha credenciais/dados com `nextcloud-db` ou `postgres_evolution`.
- **Audit log imutável**: Tabela `audit_log` sem GRANT de UPDATE/DELETE para o user da app.
- **Secrets**: `.env` no `.gitignore`. Em CI/Deploy: GitHub Secrets (`GEMINI_API_KEY`, `JWT_SECRET`, `DB_PASSWORD`, `SSH_PRIVATE_KEY`, `GHCR_PAT`). Rotação documentada em `ops/`.
- **Dependency scanning**: `pip-audit` + `npm audit` no CI bloqueiam vulnerabilidades altas.
- **Backups**: Estende `/usr/local/bin/backup-infra.sh` existente — `pg_dump` diário do `plan-trib-db` + cópia do volume `plan_trib_uploads`, comprimidos em `.tar.zst` e enviados via rclone para Google Drive (offsite).
- **Patch da VPS**: `unattended-upgrades` (já instalado no Ubuntu 24.04 da Safion) cuida de patches de segurança automáticos do OS.
- **Resource limits**: cada container tem `deploy.resources.limits` para evitar que falha do plan-trib (ex.: memory leak) afete Nextcloud/n8n/Evolution.
- **Network share**: usar `root_backend` é necessário para Traefik enxergar; mitigação contra movimento lateral: postgres aceita conexão APENAS do user da app (sem trust), Argon2id em senhas.

---

## Observability

| Aspecto | Implementação |
|---------|----------------|
| **Logging** | Structured JSON via `structlog` para stdout dos containers; logs persistidos via Docker driver `json-file` com rotação (`max-size=50m`, `max-file=5`); acessíveis via `docker logs plan-trib-backend` ou `journalctl` na VPS |
| **Logs Traefik** | Reaproveita logs do Traefik existente (já configurado pela infra Safion) — mostra latência, status code, host por requisição |
| **Métricas** | Endpoint `/metrics` no FastAPI (Prometheus format) — opcional fase 2; mínimo MVP: contador de uploads, latência média, taxa de erro de extração LLM |
| **Tracing** | Skip MVP (overengineering para single VPS); avaliar OpenTelemetry em fase 2 se houver problemas de performance |
| **Error tracking** | Sentry SDK opcional (`SENTRY_DSN` env) — fase 2 |
| **LLM observability** | Langfuse (opcional, KB presente) — instrumenta `extractors/base.py` para tracear requests Gemini com custo/latência/qualidade |
| **Uptime** | Monitor externo (UptimeRobot free tier) verifica `https://plantrib.safion.com.br/api/health` a cada 5min |
| **Health endpoint** | `GET /api/health` — checa DB connection (`SELECT 1`), retorna `{status, db, version}` |
| **Status compartilhado** | n8n existente pode ser usado para alertas de healthcheck (workflow simples: HTTP request → if status != 200 → notificação email/Slack) |

---

## Revision History

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 2026-04-28 | design-agent (Claude Opus 4.7) | Versão inicial extraída do DEFINE_PLANEJAMENTO_TRIBUTARIO.md (Phase 1). Incorpora 11 ADRs, 95 arquivos no manifest, 6 patterns de código, infra Docker+Actions+VPS, integração com KB `tributacao_brasileira` |
| 1.1 | 2026-04-28 | design-agent | **Ajustes de coexistência com infra Safion existente**: análise de `.claude/documentos/infraestrutura/` revelou Traefik v3, Nextcloud, n8n, Evolution já rodando. Mudanças: (a) Decision 8 reescrita — Traefik reutilizado em vez de NGINX próprio; (b) Decision 12 nova — coexistência isolada com stack Safion; (c) docker-compose.yml com labels Traefik + network `root_backend` external + container_names `plan-trib-*` + volumes prefixados + resource limits; (d) backup integrado ao `/usr/local/bin/backup-infra.sh` existente; (e) subdomínio definido: `plantrib.safion.com.br`; (f) removidos `docker/nginx.conf` e `ops/letsencrypt.sh` do file manifest; (g) configuração e segurança atualizadas para refletir Traefik |

---

## Next Step

**Pronto para:** `/build .claude/sdd/features/DESIGN_PLANEJAMENTO_TRIBUTARIO.md`

A próxima fase (Build) executará o manifest:

1. Inicializar projeto: `pyproject.toml`, `Makefile`, `.gitignore`, `README.md`
2. Setup Docker: Dockerfiles, compose, NGINX config
3. CI/CD: workflows GitHub Actions
4. Backend: models → schemas → services → API → parsers → extractors → engine
5. Migrations Alembic + seed inicial
6. Frontend Next.js: layout → auth → CRUDs → upload → comparativo → simulação
7. Tests: parsers (com fixtures reais) → engine → integration
8. README com instruções dev/deploy
