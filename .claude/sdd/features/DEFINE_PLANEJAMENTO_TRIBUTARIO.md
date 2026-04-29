# DEFINE: Planejamento Tributário Comparativo

> Sistema web para escritório de contabilidade que importa documentos fiscais (SPED, PDFs de folha e PGDAS-D), calcula a carga tributária dos três regimes (Simples Nacional × Lucro Presumido × Lucro Real) por grupo de empresas, e permite simulação de cenários what-if.

## Metadata

| Atributo | Valor |
|----------|-------|
| **Feature** | PLANEJAMENTO_TRIBUTARIO |
| **Date** | 2026-04-28 |
| **Author** | define-agent (executado por Claude Opus 4.7) |
| **Status** | Ready for Design |
| **Clarity Score** | 15/15 |
| **Source** | `BRAINSTORM_PLANEJAMENTO_TRIBUTARIO.md` (Phase 0 — Ready for Define) |
| **Stakeholder** | Gleydson Paiva Muniz (GUINER CONTABILIDADE — Colatina/ES) |

---

## Problem Statement

Escritórios de contabilidade brasileiros decidem manualmente — em planilhas frágeis, sem versionamento e propensas a erro — qual o regime tributário ótimo (Simples × Lucro Presumido × Lucro Real) para cada grupo de empresas-clientes. O esforço repetitivo a cada simulação consome horas que poderiam ser dedicadas a consultoria estratégica, e a falta de auditabilidade dos cálculos compromete a defensabilidade da recomendação ao cliente.

---

## Target Users

| Usuário | Papel | Pain Point |
|---------|-------|------------|
| **Contador operacional** | Executa o planejamento tributário no escritório | Refaz cálculos manuais a cada simulação; risco de erro nas tabelas (Anexos do Simples, % de presunção); não tem histórico de cenários comparados; sem rastreabilidade do que mudou entre versões |
| **Sócio/gerente do escritório** | Supervisiona múltiplos planejamentos e gera recomendações | Não consegue comparar grupos de clientes lado a lado; sem visão consolidada por grupo (matriz+filiais); difícil priorizar quais clientes precisam revisão de regime |
| **Empresário cliente** (usuário indireto) | Recebe a recomendação tributária do escritório | Quer entender por que um regime foi recomendado; precisa de justificativa quantitativa, não "achismo" do contador |

---

## Goals

| Prioridade | Objetivo |
|-----------|----------|
| **MUST** | Importar arquivos SPED Fiscal (EFD ICMS/IPI v019) e SPED Contribuições (v006) com parsing correto |
| **MUST** | Extrair totalizadores de PDFs de folha de pagamento (sistema Domínio e similares) via LLM com saída estruturada |
| **MUST** | Extrair declaração PGDAS-D (PDF) para empresas atualmente no Simples |
| **MUST** | Calcular apuração tributária dos 3 regimes (Simples, LP, LR) por empresa e por competência mensal |
| **MUST** | Modelar grupo de empresas (1 grupo → N CNPJs, com tipos matriz/filial/independente) |
| **MUST** | Apresentar comparativo lado a lado dos 3 regimes com detalhamento por tributo |
| **MUST** | Permitir simulação what-if com botão "replicar valor para todos os meses" |
| **MUST** | Persistir dados em PostgreSQL com criptografia em repouso e em trânsito (LGPD) |
| **MUST** | Multi-usuário (vários contadores do escritório) com autenticação e logs de auditoria |
| **SHOULD** | Recomendar automaticamente o regime de menor carga tributária total no período analisado |
| **SHOULD** | Consolidar análise por grupo (somando ou comparando empresas do mesmo grupo) |
| **SHOULD** | Tempo de onboarding de uma empresa nova ≤ 15 minutos (cadastro + upload + 1ª análise) |
| **SHOULD** | Exportar relatório comparativo em PDF para apresentação ao cliente |
| **COULD** | Cenários nomeados (salvar e versionar simulações) |
| **COULD** | Projeções automáticas baseadas em tendência das receitas históricas (PGDAS-D 14m / SPED) |
| **COULD** | Dashboard executivo agregando múltiplos grupos para o sócio do escritório |

---

## Success Criteria

Métricas mensuráveis de aceitação do MVP:

- [ ] **Parser SPED**: importar com sucesso ≥ 95% dos arquivos EFD ICMS/IPI e EFD-Contribuições do escritório (medido contra amostras reais — mínimo 47 arquivos do grupo WIBE + arquivos adicionais)
- [ ] **Extração PDF**: precisão ≥ 98% em totalizadores chave (INSS Total, FGTS, base IRRF, RBT12 do PGDAS) validada contra valores conferidos manualmente em ≥ 5 amostras
- [ ] **Cálculo tributário**: erro absoluto < R$ 1,00 vs. apuração de referência (PGDAS-D para Simples; SPED M210/M610/E110 para LP)
- [ ] **Performance comparativo**: gerar comparativo consolidado por grupo em < 5 segundos (p95)
- [ ] **Performance simulação**: criar cenário what-if com replicação em < 30 segundos
- [ ] **Onboarding**: cadastro + upload + 1ª análise concluídos em ≤ 15 minutos por empresa
- [ ] **LGPD**: dados sensíveis criptografados em repouso (Postgres TDE ou pgcrypto) e em trânsito (TLS 1.2+); todos os acessos logados com usuário+timestamp+ação
- [ ] **Disponibilidade**: uptime mensal ≥ 99% (downtime aceitável: ~7h/mês para manutenção e incidentes — compatível com SLA típico de VPS Hostinger)
- [ ] **Cobertura de teste**: ≥ 80% no engine de cálculo (módulo crítico); ≥ 60% nos parsers

---

## Acceptance Tests

| ID | Cenário | Given | When | Then |
|----|---------|-------|------|------|
| **AT-001** | Importar SPED Fiscal válido (caso WIBE) | Arquivo `23735214000101-...-20250101-20250131-...-SPED-EFD.txt` válido (leiaute v019, encoding ISO-8859-1) | Usuário faz upload no módulo de ingestão | Sistema parseia 100% dos registros relevantes (0000, C100, C170, C190, E110, H010), persiste no banco e exibe resumo: período, CNPJ, faturamento por CFOP, ICMS apurado |
| **AT-002** | Importar SPED Contribuições válido (caso WIBE) | Arquivo `PISCOFINS_20250101_20250131_23735214000101_...txt` válido (leiaute v006) | Usuário faz upload | Sistema identifica regime via 0110 (cumulativo = LP), extrai estabelecimentos (0140), receitas por CST/CFOP (F550), apuração consolidada (M200/M210, M600/M610) |
| **AT-003** | Extrair PDF de folha (caso WIBE) | PDF `171-Resumo Mensal.pdf` (formato Domínio) | Usuário envia arquivo para o extrator LLM | Sistema retorna `FolhaTotalizadores` Pydantic-validado com: CNPJ, competência, INSS Total, FGTS, base IRRF, qtd empregados; precisão ≥ 98% vs valores impressos no PDF |
| **AT-004** | Extrair PGDAS-D (caso SANREED Anexo I) | PDF `PGDASD-DECLARACAO-59372013202603001.pdf` | Usuário envia arquivo | Sistema retorna `PgdasDeclaracao` com RBT12, RBA, RBAA, débito por estabelecimento e por tributo (8 colunas), Anexo I inferido a partir da descrição "Revenda de mercadorias..." |
| **AT-005** | Calcular comparativo dos 3 regimes (empresa LP atual) | Empresa WIBE matriz (LP), com 12 meses de dados ingeridos (SPED + folha + despesas manuais sintéticas) | Usuário aciona "Comparar regimes" para o período jan-dez/2025 | Sistema retorna 3 `ResultadoApuracao` (Simples simulado, LP atual apurado, LR simulado) com tributos detalhados (8 tributos), alíquota efetiva e total; tempo p95 < 5 segundos |
| **AT-006** | Simulação what-if com replicação | Usuário visualiza despesas mensais sintéticas (Adm/Com/Trib) de uma empresa | Usuário informa novo valor para "Despesas Administrativas" do mês de janeiro e clica em "Replicar para todos os meses" | Sistema preenche os outros 11 meses com o mesmo valor, recalcula os 3 regimes e exibe novo comparativo em < 30s; cenário marcado como "não persistido" até usuário salvar explicitamente |
| **AT-007** | Consolidação por grupo (WIBE matriz + 3 filiais) | Grupo WIBE com 4 CNPJs cadastrados; 12 meses de dados ingeridos para todos | Usuário aciona "Comparar grupo" para o período anual | Sistema soma faturamento, créditos e tributos de cada CNPJ; calcula 3 regimes a nível de empresa individual (regime é por CNPJ) e apresenta visão consolidada do grupo com totalizadores |
| **AT-008** | Validação de erro: SPED com leiaute desconhecido | Arquivo SPED com `0000.cod_ver = "999"` (versão inexistente) | Usuário faz upload | Sistema rejeita o arquivo com mensagem clara: "Versão de leiaute 999 não suportada. Versões aceitas: 016, 017, 018, 019. Atualize o sistema ou contate suporte." Nada é persistido |
| **AT-009** | Auditoria de acesso (LGPD) | Usuário contador autenticado | Faz qualquer ação que leia ou modifique dados (login, upload, simulação, exportação) | Sistema grava log estruturado: `{usuario_id, timestamp, acao, recurso_id, resultado}` em tabela `audit_log` imutável |
| **AT-010** | Multi-usuário sem colisão | 2 contadores do escritório autenticados simultaneamente | Ambos editam a mesma empresa em cenários what-if diferentes | Cada cenário é isolado por usuário; ao salvar, sistema impede sobrescrita silenciosa (optimistic locking — exibe diff e exige resolução manual) |

---

## Out of Scope

Itens explicitamente **fora** do MVP (já validados via YAGNI no brainstorm):

- Importação de SPED ECD (Contábil), ECF, eSocial, EFD-Reinf — substituídos por formulário sintético de despesas (LR) e PDF de folha
- Integração direta com ERPs ou sistemas contábeis (Domínio, Sage, Conta Azul, Omie) — apenas upload manual
- Multi-tenant SaaS com cobrança/planos — single-tenant para escritório
- ICMS-ST detalhado, DIFAL, monofásicos detalhados — aproximação geral atende; refinamento futuro
- Reforma tributária (CBS/IBS — LC 214/2025) — aguardar regulamentação estável
- Geração e transmissão de obrigações acessórias (DCTFWeb, GIA, GFIP) — escopo é planejamento, não execução
- Análise do regime MEI (Microempreendedor Individual) — fora do escopo
- Apuração de IRRF/folha do exterior, participação em lucros (PLR) — fora do escopo principal
- Plano de contas analítico para LR — sintético (3 contas) é suficiente
- Dashboard executivo agregado multi-grupo — fase 2 (COULD apenas)
- Workers assíncronos (Celery/Redis) — processamento síncrono atende ao volume
- Auto-scaling, multi-região, CDN — single VPS Hostinger atende
- Mobile app — apenas web responsivo

---

## Constraints

| Tipo | Constraint | Impacto |
|------|------------|---------|
| **Domínio (legal)** | Legislação tributária brasileira muda anualmente (LC 123, RFB, CGSN, Sefaz estaduais) | Tabelas (Anexos, % presunção) **não podem** ficar hard-coded — devem viver em `kb/tributacao_brasileira/specs/*.yaml` versionados |
| **Domínio (precisão)** | Cálculos fiscais não toleram erros de arredondamento | Usar `Decimal` end-to-end (nunca `float`); arredondamento `ROUND_HALF_EVEN`; persistir como `NUMERIC(18,6)` no Postgres |
| **Domínio (LGPD)** | Dados fiscais e folha são sensíveis (CPF, CNPJ, salários) | Criptografia em repouso (TDE ou pgcrypto), em trânsito (TLS 1.2+), logs de auditoria imutáveis, controle de acesso por usuário |
| **Domínio (multi-CNPJ)** | SPED é por estabelecimento; planejamento é por grupo | Modelo `Grupo (1) → Empresas (N)` com tipos matriz/filial/independente; consolidação é regra de negócio explícita |
| **Domínio (versionamento SPED)** | Leiautes mudam (~anualmente); arquivos antigos seguem versão da época | Parser deve detectar versão via `0000.cod_ver` e aplicar registry adequado |
| **Técnico (LLM externo)** | Extração de PDF depende de Gemini/OpenRouter (custo, latência, disponibilidade) | Implementar fallback (Gemini 2.5 Flash → Pro; ou Gemini → OpenRouter); timeout configurável; retry com backoff |
| **Técnico (encoding)** | Arquivos SPED são ISO-8859-1, não UTF-8 | Parser obrigatoriamente abre com `encoding="iso-8859-1"` |
| **Infra (VPS Safion compartilhada)** | VPS Hostinger já hospeda Nextcloud, n8n, Evolution API; o projeto plan-trib **não pode** apresentar risco aos serviços existentes | Compose dedicado (`/opt/plan-trib/`); Postgres dedicado (`plan-trib-db`); volumes prefixados (`plan_trib_*`); resource limits explícitos; reuso do Traefik existente (sem NGINX próprio); subdomínio `plantrib.safion.com.br`; backup integrado ao `/usr/local/bin/backup-infra.sh` |
| **Infra (VPS autogerida)** | VPS não é PaaS; sem auto-scaling, sem managed DB | Backups via script Safion (rclone → Google Drive); patches via `unattended-upgrades`; TLS gerenciado pelo Traefik (Let's Encrypt automático) |
| **Infra (recursos compartilhados)** | App + Postgres co-localizados; vizinhos: Nextcloud (PHP+Postgres+Redis), n8n (Node+SQLite), Evolution (Postgres+Redis) | Recursos atuais: ~16% RAM em uso, 41% disco, CPU load 0.06 — folga confortável; resource limits do plan-trib (~2.5G RAM total) ainda deixa folga ampla |
| **Infra (rede)** | Postgres NUNCA exposto à internet; rede `root_backend` é compartilhada (necessária para Traefik) | Container `plan-trib-db` sem `ports:` publicada; senha forte do Postgres; sem `trust` em `pg_hba.conf` |
| **Time/orçamento** | Desenvolvedor único (você), aprendendo dev na prática | Stack escolhida (FastAPI + Next.js + Docker) é deliberadamente simples; KB curado reduz curva |
| **Time/orçamento** | Custo de infra deve ser previsível (~US$ 15-30/mês) | VPS Hostinger plano básico-médio; sem produtos cloud gerenciados |

---

## Technical Context

> Contexto essencial para a Phase 2 (Design) — evita arquivos no lugar errado e necessidades de infra esquecidas.

| Aspecto | Valor | Notas |
|---------|-------|-------|
| **Deployment Location (monorepo)** | `src/` (backend Python/FastAPI) · `web/` (frontend Next.js) · `docker/` (Dockerfiles + `docker-compose.yml`) · `.github/workflows/` (CI Actions) · `migrations/` (Alembic) · `tests/` (pytest) | Estrutura nova (projeto greenfield); decisão de monorepo confirmada no brainstorm |
| **KB Domains aplicáveis** | `pydantic` (modelos), `gemini` (LLM extraction), `openrouter` (fallback LLM), `langfuse` (observabilidade LLM), `tributacao_brasileira` (domínio fiscal — criada nesta fase) | Design phase deve consultar primeiro |
| **KB Domains NÃO aplicáveis nesta fase** | `gcp`, `terraform`, `terragrunt`, `crewai` | Marcadas como "obsoletas para esta fase" no brainstorm; mantém-se para evolução futura |
| **IaC Impact** | **Nenhum** (não usa Terraform) — infra declarada via `docker-compose.yml` + workflows GitHub Actions | Substitui o que seria Terraform por Docker Compose para orquestração local da VPS |
| **CI/CD** | GitHub Actions: lint → test → build imagem Docker → push GHCR/Docker Hub → deploy via SSH/webhook na VPS Hostinger | Imagem é o único artefato — dev local roda a mesma imagem para paridade |
| **Banco de dados** | PostgreSQL 16+ rodando como container Docker na VPS Hostinger, com volume persistente (`pgdata`) | NUNCA exposto à internet; `pg_dump` agendado para backup |
| **Frontend ↔ Backend** | API REST JSON (FastAPI auto-gera OpenAPI 3.1); Next.js consome via fetch/SWR | OpenAPI permite gerar types TypeScript no frontend automaticamente |
| **Autenticação** | JWT em sessão httpOnly + refresh token; usuários internos (escritório) cadastrados manualmente | Sem self-service signup; sem OAuth público |
| **Observabilidade** | Logs estruturados (JSON) → arquivo na VPS + opcional Langfuse para LLM calls; uptime monitor externo (UptimeRobot free tier) | Sem stack pesada (Prometheus/Grafana) — overkill para single VPS |

**Por que isso importa:**

- **Location** → Design phase usa estrutura correta de monorepo, evita confusão entre código backend, frontend e infra
- **KB Domains** → Design phase puxa patterns corretos (LLM com Pydantic, parsing SPED, cálculo multi-regime); evita reinventar
- **IaC Impact** → Confirma que o Design não precisa planejar Terraform; foca em `Dockerfile` + `docker-compose.yml` + workflows
- **CI/CD** → Design phase sabe que o pipeline é GitHub Actions desde o dia 0 (não é decisão deferida)
- **DB co-localizado** → Design phase considera `shared_buffers` adequado, conexão via rede Docker interna, backup como responsabilidade explícita

---

## Assumptions

Premissas que, se incorretas, podem invalidar o design:

| ID | Premissa | Se errada, impacto | Validada? |
|----|----------|--------------------|-----------|
| **A-001** | Volume do escritório é compatível com VPS única (~dezenas a baixas centenas de empresas, processamento mensal) | Se for milhares de empresas com processamento simultâneo, VPS vira gargalo — necessário workers/queue ou cloud | ✅ Confirmado no brainstorm (escritório, não SaaS) |
| **A-002** | LLM (Gemini 2.5 Flash) consegue extrair PDFs de folha com precisão ≥ 98% em <5s | Se precisão for baixa, precisamos: (a) few-shot examples, (b) Gemini Pro (mais caro), ou (c) pipeline híbrido (regex + LLM) | ⚠️ Validar em AT-003 com 5 amostras reais |
| **A-003** | Leiaute do PDF de folha permanece consistente em ≥ 90% dos casos do escritório | Se houver muitas variações de sistema (Domínio, Sage, Sage Saas, etc.), precisamos few-shot por sistema ou modelo mais robusto | ⚠️ Validar com PDFs de outros sistemas além do Domínio |
| **A-004** | PGDAS-D mantém leiaute padrão da RFB sem alterações disruptivas no MVP timeframe | Se RFB lançar novo formato, precisamos atualizar prompt/schema | 🟡 Histórico estável — risco baixo |
| **A-005** | SPED ICMS/IPI v019 e Contribuições v006 são as versões em uso pelos clientes do escritório | Se houver clientes ainda em v018/v005, parser precisa suportar múltiplas versões simultâneas | ✅ Já mapeado no spec `leiautes-sped-versoes.yaml` (v016-v019 fiscal; v004-v006 contrib) |
| **A-006** | Dados de despesas adicionais (Adm/Com/Trib) sintéticas são suficientes para apuração razoável de Lucro Real | Se contadores precisarem de plano analítico, formulário fica insuficiente | ✅ Confirmado pelo usuário no brainstorm |
| **A-007** | VPS Hostinger Safion (~16GB RAM, ~57GB livres, CPU load 0.06) atende plan-trib (~2.5G RAM com limits) sem prejudicar Nextcloud/n8n/Evolution | Se ficar lento, precisamos upgrade ou ajustar limits | ✅ **Confirmado** via análise da infra existente — recursos folgados |
| **A-008** | GitHub Actions consegue construir e publicar imagem Docker em < 10 minutos por push | Se demorar muito, prejudica DX; pode precisar cache de layers ou self-hosted runner | 🟡 Risco baixo — pipeline padrão |
| **A-009** | Fator R, sublimites e mapeamento Atividade→Anexo são determinísticos a partir das amostras analisadas | Se houver casos ambíguos (ex.: atividade não listada no PGDAS textualmente), precisa LLM fallback | ✅ Spec `tabelas-simples-anexos.yaml` cobre os 5 anexos com regras explícitas |
| **A-010** | Cálculos do engine podem ser determinísticos sem dependência de serviços externos | Se Sefaz mudar interpretação ou se houver casos legais novos (jurisprudência), precisa atualização manual das specs | ✅ Specs são atualizáveis sem deploy de código |

**Nota:** Premissas marcadas com ⚠️ devem ser validadas durante a Phase 2 (Design) ou cedo na Phase 3 (Build) para evitar retrabalho.

---

## Clarity Score Breakdown

| Elemento | Pontos (0-3) | Justificativa |
|----------|--------------|---------------|
| **Problem** | 3 | Claro, específico, acionável: contadores fazem em planilha frágil; impacto (horas, erro, falta de auditoria) está explícito |
| **Users** | 3 | 3 personas identificadas (contador operacional, sócio, empresário cliente) com pain points distintos |
| **Goals** | 3 | Priorizados em MUST/SHOULD/COULD com base em decisões já validadas no brainstorm; 9 MUST, 4 SHOULD, 3 COULD |
| **Success** | 3 | Critérios mensuráveis com números explícitos (95%, 98%, < R$1, < 5s, < 30s, < 15min, ≥ 99%, ≥ 80%, ≥ 60%) |
| **Scope** | 3 | Out of scope explícito com 14 itens; constraints (12 itens) bem detalhadas; decisões #10/#13/#14 atualizadas para Docker+Actions+VPS |
| **TOTAL** | **15/15** | |

**Mínimo para avançar:** 12/15 ✅ (atingido com folga)

---

## Open Questions

Nenhuma pergunta bloqueante para iniciar Phase 2 (Design).

**Premissas a validar durante Design** (não bloqueantes, mas antes de Build):

1. **A-002, A-003** — Rodar extração LLM nas 5 amostras de folha disponíveis e medir precisão real (pode requerer ajuste de prompt ou few-shot)
2. **A-007** — Definir plano da VPS Hostinger no início do Design para confirmar RAM/CPU/SSD adequados

---

## Revision History

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 2026-04-28 | define-agent (Claude Opus 4.7) | Versão inicial extraída do BRAINSTORM_PLANEJAMENTO_TRIBUTARIO.md (Phase 0). Já incorpora atualizações de infra (Docker + GitHub Actions + VPS Hostinger; Postgres co-localizado) e KB `tributacao_brasileira` recém-criada |

---

## Next Step

**Pronto para:** `/design .claude/sdd/features/DEFINE_PLANEJAMENTO_TRIBUTARIO.md`

A próxima fase (Design) deve produzir:

- Modelo de dados PostgreSQL (schemas, tabelas, índices, relacionamentos Grupo↔Empresa↔Período↔Documento↔Apuração)
- Contratos de API REST (endpoints, schemas request/response, autenticação)
- Arquitetura interna dos módulos (parsers, extractor LLM, engine de cálculo, comparador)
- `Dockerfile`s, `docker-compose.yml` (dev e prod), workflows `.github/workflows/*.yml`
- Estratégia de testes (fixtures com SPEDs reais, mocks para LLM, golden files para apurações de referência)
- Plano de migração e seeds iniciais (tabelas de Anexos, % presunção carregadas dos specs do KB)
- Plano de segurança (criptografia, autenticação, audit trail, gestão de secrets)
