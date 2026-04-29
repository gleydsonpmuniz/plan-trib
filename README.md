# Plan Trib — Planejamento Tributário Comparativo

Sistema web para escritórios de contabilidade compararem regimes tributários
(Simples Nacional × Lucro Presumido × Lucro Real) por grupo de empresas, com
ingestão de SPED Fiscal, SPED-Contribuições, PDFs de folha (extração via LLM)
e PGDAS-D (Simples). Permite simulação de cenários what-if.

## Stack

- **Backend**: FastAPI 0.115 + Python 3.12 + SQLAlchemy 2 (async) + Pydantic 2
- **Frontend**: Next.js 15 + React 19 + TypeScript + TailwindCSS
- **DB**: PostgreSQL 16
- **LLM**: Google Gemini 2.5 Flash (via `google-genai`) com fallback OpenRouter
- **Deploy**: Docker + GitHub Actions + GHCR + VPS Hostinger Safion (Traefik existente)

## Estrutura

```
.
├── src/                # Backend Python (api, models, services, parsers, extractors, engine)
├── web/                # Frontend Next.js
├── docker/             # Dockerfiles
├── migrations/         # Alembic
├── kb/                 # Tabelas tributárias (YAML — copiado de .claude/kb/tributacao_brasileira/specs/)
├── tests/              # pytest (parsers, engine, integration)
├── .github/workflows/  # CI/CD
├── ops/                # Scripts (deploy, backup)
└── docker-compose.yml  # Prod (VPS Safion — Traefik + root_backend)
```

## Dev local (WSL + Docker)

```bash
# 1. Configure variáveis
cp .env.example .env
# edite .env com senhas e GEMINI_API_KEY

# 2. Sobe stack dev (com hot reload)
make dev

# 3. Migrations
make migrate

# 4. Tests
make test
```

API disponível em `http://localhost:8000/api`. Web em `http://localhost:3000`.

## Deploy em produção (VPS Safion)

Pré-requisitos:
- VPS Hostinger Safion (`31.97.253.130`) com Traefik v3 já rodando + network `root_backend`
- DNS A `plantrib.safion.com.br` → `31.97.253.130`
- GitHub Secrets configurados: `SSH_PRIVATE_KEY`, `GHCR_PAT`, `GEMINI_API_KEY`, `JWT_SECRET`, `DB_PASSWORD`
- `.env` em `/opt/plan-trib/.env` na VPS (não versionado)

Fluxo:
1. Push para `main` → Actions builda imagens → push GHCR
2. Actions `Deploy` (manual ou auto após build) → SSH na VPS → `docker compose pull && up -d`
3. Migrations rodam automaticamente

## Coexistência com infra Safion

A aplicação coexiste com Nextcloud/n8n/Evolution API:
- Compose dedicado em `/opt/plan-trib/`
- Postgres dedicado (`plan-trib-db`) — não compartilha com `nextcloud-db` nem `postgres_evolution`
- Volumes prefixados (`plan_trib_pgdata`, `plan_trib_uploads`)
- Resource limits configurados (não impacta vizinhos)
- Reusa Traefik (TLS Let's Encrypt automático)
- Backup integra ao `/usr/local/bin/backup-infra.sh` existente

## Documentação SDD

- [BRAINSTORM](.claude/sdd/features/BRAINSTORM_PLANEJAMENTO_TRIBUTARIO.md) (Phase 0)
- [DEFINE](.claude/sdd/features/DEFINE_PLANEJAMENTO_TRIBUTARIO.md) (Phase 1)
- [DESIGN](.claude/sdd/features/DESIGN_PLANEJAMENTO_TRIBUTARIO.md) (Phase 2)
- [Build Report](.claude/sdd/reports/BUILD_REPORT_PLANEJAMENTO_TRIBUTARIO.md) (Phase 3)
- [KB Tributação Brasileira](.claude/kb/tributacao_brasileira/index.md)

## Licença

Uso interno GUINER CONTABILIDADE.
