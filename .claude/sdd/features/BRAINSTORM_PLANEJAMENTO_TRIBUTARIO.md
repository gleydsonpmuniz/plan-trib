# BRAINSTORM: Planejamento Tributário Comparativo

> Sessão exploratória para clarificar intenção e abordagem antes da captura formal de requisitos

## Metadata

| Atributo | Valor |
|----------|-------|
| **Feature** | PLANEJAMENTO_TRIBUTARIO |
| **Data** | 2026-04-28 |
| **Author** | brainstorm-agent (executado por Claude Opus 4.7) |
| **Status** | Ready for Define |
| **Stakeholder** | Gleydson Paiva Muniz (GUINER CONTABILIDADE) |
| **Última revisão** | 2026-04-28 — atualização de infra (Docker + GitHub Actions + VPS Hostinger; KB `tributacao_brasileira` criada) |

---

## Initial Idea

**Raw Input:** "O projeto está relacionado a um planejamento tributário, onde irei comparar os regimes de tributação do Simples Nacional, lucro presumido e lucro real."

**Context Gathered:**
- Projeto novo (`.claude/sdd/features/` vazio antes desta sessão)
- KB já presente sugere stack Python + LLM (Pydantic, Gemini, OpenRouter, CrewAI, Langfuse)
- KB de IaC sugere deploy em GCP via Terraform/Terragrunt
- Documentos reais disponíveis em `.claude/documentos/`: 5 PDFs de folha, 13 SPEDs Contribuições, 47 SPEDs Fiscais, 2 PGDAS-D
- Caso de teste real identificado: grupo WIBE CONFECCOES (matriz + 3 filiais, indústria de confecção feminina, Lucro Presumido atual, Colatina/ES)
- Casos PGDAS adicionais: SANREED VESTUARIO (Anexo I) e JP CONFECCOES (Anexo II), também Colatina/ES

**Technical Context Observed (for Define):**

| Aspecto | Observação | Implicação |
|---------|------------|------------|
| Likely Location | `src/` (backend FastAPI) + `web/` (Next.js) + `docker/` (Dockerfiles + compose) + `.github/workflows/` (Actions) | Monorepo com separação clara |
| Relevant KB Domains | `pydantic`, `gemini`, `openrouter`, `langfuse`, `tributacao_brasileira` | Extração via LLM com saída estruturada; conhecimento de domínio fiscal curado |
| KB obsoletas para esta fase | `gcp`, `terraform`, `terragrunt` | Decisão de infra mudou para VPS Hostinger; mantém-se no projeto como referência futura |
| Containerização | Docker (dev e prod) | Paridade dev/prod; isolamento WSL local |
| CI/CD | GitHub Actions | Build da imagem dentro do GitHub |
| Deploy alvo | VPS Hostinger Safion (compartilhada com Nextcloud/n8n/Evolution; Traefik existente como reverse proxy) | Imagem buildada nas Actions é puxada via SSH na VPS; subdomínio `plantrib.safion.com.br`; coexistência isolada com containers `plan-trib-*` (compose dedicado em `/opt/plan-trib/`) |
| Stack Frontend | Next.js + React (validado) | Formulários complexos + dashboards |
| Stack Backend | FastAPI + Python 3.12+ | Performance + tipagem forte |
| Database | PostgreSQL **rodando na própria VPS Hostinger** (container Docker com volume persistente) | Numéricos precisos para cálculos fiscais; JSONB para semi-estruturados; co-localizado com a app na mesma VPS |

---

## Discovery Questions & Answers

| # | Pergunta | Resposta | Impacto |
|---|----------|----------|---------|
| 1 | Qual o entregável principal? | (a) Aplicação web dinâmica que coleta dados fiscais/contábeis/folha, persiste em DB protegido, gera análises e permite simular cenários | Define stack web full + DB + engine de cálculo + UI de simulação |
| 2 | Perfil dos usuários e escala? | (b) Escritório de contabilidade analisando **grupos de empresas** (1+ empresas por grupo, podendo ser independentes ou matriz/filiais) | Single-tenant interno; modelo `Grupo → Empresas (1:N)`; sem complexidade SaaS |
| 3 | Método de entrada dos dados fiscais? | (c) Importação de arquivos SPED | Alto esforço de parser; máxima precisão |
| 4 | Quais SPEDs no escopo? | EFD ICMS/IPI + EFD-Contribuições (fiscal). Folha via PDF "Resumo Mensal". PGDAS-D em PDF para empresas atualmente no Simples | Escopo enxuto vs. importar todos os SPEDs; ECD/ECF removidos |
| 5 | Tem amostras disponíveis? | Sim — 5 PDFs folha (grupo WIBE), 13 meses SPED Contribuições (matriz WIBE), 47 SPEDs Fiscais (4 CNPJs do grupo), 2 PGDAS-D (SANREED e JP CONFECCOES) | Permite TDD com casos reais; LLM extraction com few-shot |
| 6 | Como tratar despesas para Lucro Real (sem ECD)? | (a-resumido) Formulário sintético mensal com contas: Despesas Administrativas, Comerciais, Tributárias. Folha vem do PDF. UX com botão "replicar valor para todos os meses" | Módulo de despesas leve; sem plano de contas analítico |

**Total de perguntas:** 6 (mínimo: 3 ✅)

---

## Sample Data Inventory

> Amostras melhoram precisão do LLM através de in-context learning e validam parsers com casos reais.

| Tipo | Localização | Quantidade | Notas |
|------|-------------|-----------|-------|
| SPED Fiscal (EFD ICMS/IPI) | `.claude/documentos/sped_fiscal_icms_ipi/` | 47 arquivos | Grupo WIBE — 4 CNPJs (matriz + 3 filiais), 15 meses (jan/2025–mar/2026). Inclui blocos C100/C170/C190 (NFe), E100/E110 (apuração ICMS), 0150 (participantes), 0200 (itens) |
| SPED Contribuições (PIS/COFINS) | `.claude/documentos/sped_contribuicoes/` | 15 .txt + 15 .rec | WIBE matriz — 15 meses. Regime cumulativo (PIS 0,65% / COFINS 3%) confirmando Lucro Presumido. Blocos F550 (consolidação CST), 0140 (estabelecimentos), M200/M210/M600/M610 (apuração) |
| Resumo de folha (PDF) | `.claude/documentos/folhas de pagamento/` | 5 PDFs | Sistema gera PDFs estruturados. Campos: rubricas (PROVENTOS, DESCONTOS, INFORMATIVA), totalizadores INSS/FGTS/IRRF, situações empregados, apuração tributos federais. Sistema licenciado para GUINER CONTABILIDADE |
| PGDAS-D (PDF) | `.claude/documentos/PGDAS/` | 2 PDFs | SANREED VESTUARIO (Anexo I — comércio) e JP CONFECCOES (Anexo II — indústria). Estrutura padrão RFB: identificação, discriminativo de receitas, RBT12, RBA, RBAA, receitas/folha 14 meses anteriores, fator R, sublimite, débito por estabelecimento e por tributo |
| Ground truth | (derivada das amostras) | — | Os PGDAS-D fornecem o "AS IS" Simples com débito por tributo (IRPJ/CSLL/COFINS/PIS/INSS/ICMS/IPI/ISS). Os SPEDs fornecem o "AS IS" LP via apuração já feita (M200/M600/E110) |
| Documentação RFB | (a obter) | — | Manuais de leiaute oficiais (EFD ICMS/IPI v019, EFD-Contribuições v006) precisam ser referenciados; tabelas de Anexos I-V do Simples (LC 123/2006); resoluções CGSN |

**Como as amostras serão usadas:**

- Parsers SPED desenvolvidos via TDD usando os 47+15 arquivos como fixtures de teste
- Few-shot examples para LLM no extrator de PDF (folha + PGDAS-D)
- Ground truth: cruzar valores apurados pelo nosso engine vs. valores nos arquivos (E110 ICMS, M210 PIS, M610 COFINS, débitos do PGDAS)
- Validação de cálculo cruzado: para WIBE (LP atual), simular Simples e comparar com o que ela poderia ter pago; para SANREED/JP (Simples atual), simular LP e comparar

---

## Approaches Explored

### Approach A: Monolito Python coeso ⭐ **Recomendada e Selecionada**

**Descrição:** Backend FastAPI + Frontend Next.js separados, PostgreSQL para persistência, parsers SPED em Python puro com Pydantic, extração de PDF via LLM (Gemini/OpenRouter) com saída estruturada Pydantic. Engine de cálculo desacoplado em módulo independente, testável isoladamente. Auth simples interna (sessão + JWT). **Containerização Docker para dev (WSL local isolado) e prod. CI/CD via GitHub Actions: push → build da imagem → deploy na VPS Hostinger.**

**Pros:**
- Stack coesa (Python no backend e nos parsers/engines)
- Engine de cálculo isolado → testes determinísticos por regime
- Aproveita 100% do KB já presente (Pydantic, Gemini, OpenRouter, GCP, Terraform)
- Time-to-market médio (~3-5 meses MVP)
- Next.js dá UX moderna para formulários complexos e dashboards comparativos
- Postgres oferece tipos numéricos precisos (`NUMERIC(18,6)`) — crítico para cálculos fiscais
- Deploy controlado e barato: 1 container API + 1 container web + 1 container Postgres (com volume persistente) — **toda a stack na mesma VPS Hostinger**
- Sem vendor lock-in cloud (Docker + GitHub Actions roda em qualquer host)
- Paridade dev/prod garantida pelo Docker

**Cons:**
- Sem horizontal scaling automático (não é necessário no escopo single-tenant)
- 2 deployables para gerenciar (backend e frontend) — pequeno overhead operacional
- VPS exige gestão manual de SO, backups, certificados (SSL Let's Encrypt) — não é PaaS

**Por que recomendada:** Equilíbrio ótimo entre simplicidade, manutenibilidade e capacidade de evolução. Atende o escopo (escritório de contabilidade) sem overengineering, e respeita restrições do domínio (precisão numérica, segurança LGPD, complexidade de UI).

---

### Approach B: Streamlit (protótipo rápido)

**Descrição:** Streamlit como UI+backend integrados, DuckDB local para persistência, mesmos parsers Python. LLM extraction igual à Approach A.

**Pros:**
- MVP em ~1/3 do tempo (1-2 meses)
- Excelente para validar lógica de cálculo isoladamente
- Sem necessidade de gerenciar frontend separado

**Cons:**
- UX limitada para formulários multi-etapa e dashboards interativos
- Multi-usuário fraco (escritório com vários contadores acessando)
- Dificulta evolução posterior (refatoração total se for migrar)
- Segurança questionável para dados fiscais sensíveis (LGPD)
- Sem isolamento backend/frontend dificulta versionamento de API

**Por que não recomendada:** Trade-off de UX e segurança não compensa o ganho de velocidade. Útil apenas se o objetivo fosse provar a lógica antes de investir em produção.

---

### Approach C: Microsserviços / arquitetura escalável

**Descrição:** FastAPI + workers Celery + Redis + Next.js + Postgres + S3 + Kubernetes; CrewAI para orquestrar agentes de extração de PDF.

**Pros:**
- Escalável para virar SaaS comercial no futuro
- Modularidade extrema (cada serviço evolui independente)

**Cons:**
- **Massivo overengineering** para o caso de uso (escritório, não SaaS)
- Custo operacional 5-10× maior que Approach A
- Time-to-market 3× pior
- Complexidade operacional desproporcional ao tamanho do time
- KB de Kubernetes não está presente

**Por que não recomendada:** Justifica-se apenas se houver intenção clara de virar SaaS comercial multi-tenant em 6-12 meses, o que **não** é o caso.

---

## Selected Approach

| Atributo | Valor |
|----------|-------|
| **Escolhida** | **Approach A — Monolito Python coeso** |
| **Confirmação do usuário** | 2026-04-28 (Validações 1 e 2 confirmadas explicitamente) |
| **Razão** | Equilíbrio ótimo entre simplicidade, manutenibilidade e cobertura de funcionalidade. Aproveita totalmente o KB já presente. UX adequada para o público-alvo (contadores). Atende às restrições de precisão numérica e LGPD. |

---

## Key Decisions Made

| # | Decisão | Justificativa | Alternativa rejeitada |
|---|---------|--------------|----------------------|
| 1 | Aplicação web dinâmica como entregável | Necessidade de persistência, multi-usuário e simulação interativa | Documento de pesquisa, planilha, ferramenta CLI, agente conversacional |
| 2 | Single-tenant para escritório (não SaaS) | Caso de uso interno, escala controlada (dezenas/centenas de empresas) | SaaS multi-tenant com cobrança e planos |
| 3 | Unidade de análise = grupo de empresas | Empresas reais frequentemente operam como grupo (matriz+filiais ou independentes do mesmo grupo); decisão tributária estratégica é grupal | Análise apenas por CNPJ individual |
| 4 | Importar EFD ICMS/IPI + EFD-Contribuições (sem ECD/ECF/eSocial/Reinf) | Cobre os tributos relevantes para os 3 regimes; ECD/ECF/eSocial seriam ganho marginal vs. alto custo de parser | Importar todos os SPEDs |
| 5 | Folha via PDF (não eSocial) | PDF de "Resumo Mensal" cobre os totalizadores necessários (INSS, FGTS, base p/ Fator R) com extração via LLM | Parser de eSocial (XMLs complexos) |
| 6 | PGDAS-D via PDF para empresas Simples | Fornece "AS IS" pronto com débito por tributo + 14 meses de histórico + fator R | Cálculo do Simples sempre por simulação |
| 7 | Despesas Lucro Real via formulário sintético | Sem ECD, precisa de entrada manual; formulário sintético com 3 contas (Adm/Com/Trib) é suficiente para apuração razoável | Plano de contas analítico, parser de ECD |
| 8 | Stack: FastAPI + Next.js + PostgreSQL + LLM (Gemini/OpenRouter) | Stack coesa com Python em todo backend; aproveita KB; precisão numérica em Postgres; Next.js para UI rica | Streamlit, microsserviços, Django, Flask |
| 9 | Extração de PDF via LLM com Pydantic structured output | Robustez a variações de leiaute; aproveita KB; Pydantic garante schema validado | Regex + pdfplumber (frágil a mudanças de leiaute) |
| 10 | **Deploy via Docker em VPS Hostinger; build via GitHub Actions** (atualizada 2026-04-28) | Controle total de custo; sem vendor lock-in cloud; paridade dev/prod via Docker; código fica versionado no GitHub e CI roda Actions a cada push. KBs `gcp`/`terraform`/`terragrunt` ficam como referência futura | GCP gerenciado (Cloud Run/SQL), AWS, Heroku, deploy manual |
| 13 | **Workflow dev: WSL + Docker local isolado** | Ambiente reproduzível; mesma imagem que vai para produção; sem "funciona na minha máquina" | Dev nativo no host WSL sem container |
| 14 | **GitHub como source of truth + Actions como CI** | Histórico versionado; pipeline declarativo (.github/workflows); review/PR-based; image registry (GHCR ou Docker Hub) | GitLab, manual scripting, Jenkins |
| 11 | UX de despesas: campo único + botão "replicar para todos os meses" | Reduz fricção de preenchimento de 12+ meses | Preenchimento mês-a-mês obrigatório |
| 12 | Mapeamento Atividade → Anexo do Simples baseado em descrição textual | PGDAS-D usa descrição livre; precisa tabela versionada com fallback LLM | Cadastro manual de Anexo por empresa |

---

## Features Removed (YAGNI)

| Feature sugerida | Motivo da remoção | Pode adicionar depois? |
|------------------|-------------------|------------------------|
| Importação SPED ECD (Contábil) | Substituída por formulário sintético de despesas | Sim, fase 2 |
| Importação SPED ECF | Apuração IRPJ/CSLL é calculada pelo nosso engine, não importada | Sim, fase 2 |
| Importação eSocial (S-1200/S-1210) | Folha via PDF cobre o necessário | Sim, fase 2 |
| Importação EFD-Reinf | Não essencial para os 3 regimes no MVP | Sim, fase 2 |
| Integração com ERPs (Domínio, Sage, Conta Azul, Omie) | Upload manual atende escritório | Sim, fase 3 |
| Multi-tenant SaaS | Single-tenant (escritório) é o caso atual | Apenas se virar produto comercial |
| ICMS-ST detalhado (substituição tributária) | Complexidade desproporcional ao MVP; aproximação geral atende | Sim, fase 2 |
| DIFAL (diferencial de alíquota interestadual) | Refinamento posterior | Sim, fase 2 |
| Reforma tributária CBS/IBS (LC 214/2025) | Em fase de transição/regulamentação | Sim, quando regulamentar |
| Geração de obrigações acessórias (DCTFWeb, GIA) | Escopo é planejamento, não execução | Não no escopo |
| Plano de contas analítico para LR | Sintético (3 contas) é suficiente | Sim, fase 2 |
| Cobrança/billing/planos | Não é SaaS comercial | Apenas se virar produto |
| Workers assíncronos (Celery/Redis) | Volume não justifica; processamento síncrono atende | Sim, se volume crescer |
| Dashboard executivo gerencial multi-grupo | MVP foca análise por grupo | Sim, fase 2 |

---

## Incremental Validations

| Seção | Apresentada | Feedback do usuário | Ajustada? |
|-------|-------------|---------------------|-----------|
| Entrega: aplicação web dinâmica | ✅ | Confirmado: web app dinâmica com persistência e simulação | Não (alinhado de primeira) |
| Modelo Grupo → Empresas (matriz/filial) | ✅ | Confirmado, com possibilidade de empresas independentes do mesmo grupo | Não |
| Entrada via SPED + PDF folha + PGDAS | ✅ | Confirmado: EFD ICMS/IPI, EFD-Contribuições, PDF folha, PGDAS para Simples | Refinada: PGDAS adicionado após análise dos PDFs |
| Despesas LR via formulário sintético | ✅ | Confirmado, com sugestão adicional: botão de replicar valor para todos os meses | Sim — UX de replicação adicionada às decisões |
| Approach A (FastAPI + Next.js + PostgreSQL + LLM) | ✅ | "Concordo com a validação 1" | Não |
| Decomposição em 6 módulos | ✅ | "Concordo com a validação 2" | Não (refinada com submódulos PGDAS após análise dos PDFs) |

**Total de validações:** 6 (mínimo: 2 ✅)

---

## Decomposição Modular (referência para /design)

```
┌─────────────────────────────────────────────────────────────┐
│  1. CADASTROS                                                │
│   ├─ Grupos de empresas                                      │
│   ├─ Empresas (CNPJ, regime atual, atividade, matriz/filial) │
│   ├─ Períodos (competências mensais)                         │
│   └─ Usuários (contadores do escritório, RBAC simples)       │
└─────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. INGESTÃO                                                 │
│   ├─ Parser SPED Fiscal (EFD ICMS/IPI) — Python + Pydantic   │
│   ├─ Parser SPED Contribuições — Python + Pydantic           │
│   ├─ Extrator PDF Folha (LLM Gemini + Pydantic structured)   │
│   ├─ Extrator PDF PGDAS-D (LLM Gemini + Pydantic structured) │
│   └─ Form. despesas sintéticas LR (UI Next.js + replicação)  │
└─────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. NORMALIZAÇÃO / DATA MODEL                                │
│   ├─ Faturamento (por CNPJ, competência, CFOP, CST)          │
│   ├─ Créditos (PIS/COFINS, ICMS)                             │
│   ├─ Tributos apurados (AS IS por SPED/PGDAS)                │
│   ├─ Folha (totalizadores INSS, FGTS, IRRF, base Fator R)    │
│   └─ Despesas adicionais (LR, sintéticas)                    │
└─────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. ENGINE DE CÁLCULO TRIBUTÁRIO                             │
│   ├─ Calculador Simples Nacional                             │
│   │    ├─ Mapeador Atividade → Anexo (tabela + fallback LLM) │
│   │    ├─ Calculador Fator R                                 │
│   │    ├─ Validador de Sublimites (estadual e federal)       │
│   │    └─ Aplicador de tabelas Anexos I-V (LC 123/2006)      │
│   ├─ Calculador Lucro Presumido                              │
│   │    ├─ PIS/COFINS cumulativo (0,65% + 3%)                 │
│   │    ├─ IRPJ/CSLL presumido (% sobre receita por atividade)│
│   │    ├─ ICMS apurado (entradas/saídas)                     │
│   │    └─ INSS Folha + Pró-labore                            │
│   └─ Calculador Lucro Real                                   │
│        ├─ PIS/COFINS não-cumulativo (1,65% + 7,6%, créditos) │
│        ├─ IRPJ/CSLL real (sobre lucro líquido contábil)      │
│        ├─ ICMS apurado                                       │
│        └─ INSS Folha + Pró-labore                            │
└─────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────┐
│  5. SIMULAÇÃO WHAT-IF                                        │
│   ├─ Overrides paramétricos (faturamento, folha, despesas)   │
│   ├─ Cenários nomeados (salvar e comparar)                   │
│   └─ Projeções (baseadas em tendências do PGDAS/SPED)        │
└─────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────┐
│  6. COMPARADOR + DASHBOARD                                   │
│   ├─ Comparativo dos 3 regimes por empresa (mês a mês)       │
│   ├─ Consolidado por grupo de empresas                       │
│   ├─ Recomendação automática (regime com menor carga)        │
│   ├─ Detalhamento por tributo                                │
│   └─ Exportação (PDF/Excel) para apresentação ao cliente     │
└─────────────────────────────────────────────────────────────┘
```

---

## Suggested Requirements for /define

### Problem Statement (Draft)

Escritórios de contabilidade no Brasil precisam comparar regimes tributários (Simples Nacional × Lucro Presumido × Lucro Real) para grupos de empresas-clientes, mas hoje fazem isso em planilhas frágeis, propensas a erro e sem versionamento, perdendo precisão analítica e tempo de consultoria estratégica.

### Target Users (Draft)

| Usuário | Dor |
|---------|-----|
| Contador do escritório | Refazer cálculos manuais a cada simulação; risco de erro nas tabelas/alíquotas; falta de histórico de cenários |
| Sócio/gerente do escritório | Comparar regimes para vários grupos de clientes ao mesmo tempo; gerar recomendações fundamentadas |
| Cliente final do escritório (indireto) | Receber recomendação tributária com base em dados reais e cenários simulados, não em "achismo" |

### Success Criteria (Draft)

- [ ] Importar com sucesso EFD ICMS/IPI e EFD-Contribuições de pelo menos 95% dos casos do escritório (medido contra amostras reais)
- [ ] Extrair com precisão ≥ 98% os totalizadores de PDFs de folha e PGDAS-D (validado contra valores manuais)
- [ ] Calcular os 3 regimes com erro absoluto < R$ 1,00 vs. apuração manual de referência (em casos de teste)
- [ ] Gerar comparativo consolidado por grupo de empresas em < 5 segundos
- [ ] Permitir simulação what-if com replicação de valores em < 30 segundos por cenário
- [ ] Atender LGPD: dados criptografados em repouso e em trânsito; auditoria de acessos
- [ ] Tempo de onboarding de uma nova empresa < 15 minutos (upload + cadastro + primeira análise)

### Constraints Identified

- **Domínio**: legislação tributária brasileira em constante mudança (LC 123/2006, RFB, CGSN, Sefaz estaduais)
- **Precisão numérica**: cálculos fiscais não toleram arredondamentos fora de norma (`Decimal`/`NUMERIC` obrigatório; nunca `float`)
- **LGPD**: dados fiscais e folha são sensíveis; criptografia, controle de acesso, logs de auditoria são obrigatórios
- **Multi-CNPJ**: SPED traz múltiplos estabelecimentos; modelo deve respeitar; consolidação por grupo é regra de negócio
- **Reforma tributária (CBS/IBS — LC 214/2025)**: em transição; o sistema deve ser desenhado para aceitar novos regimes futuramente sem refatoração massiva
- **Dependência de LLM externo**: extração de PDF depende de Gemini/OpenRouter (custo, latência, fallback necessário)
- **Layout dos SPEDs muda anualmente**: parser deve ser versionado por leiaute (atual: EFD ICMS/IPI v019, EFD-Contribuições v006)
- **Stack**: FastAPI + Next.js + PostgreSQL + Gemini/OpenRouter + Docker + GitHub Actions + VPS Hostinger
- **Infra autogerida (VPS)**: requer responsabilidade por SO, backups (pg_dump agendado), certificados SSL (Let's Encrypt + renovação), monitoramento básico (uptime, logs)
- **Imagem Docker reproduzível**: dev local (WSL) e prod (Hostinger) devem usar a mesma imagem produzida pelo Actions — único ponto de verdade do build

### Out of Scope (Confirmed)

- Geração e transmissão de obrigações acessórias (DCTFWeb, GIA, GFIP, etc.) — escopo é planejamento, não execução
- Integração direta com ERPs ou sistemas contábeis (Domínio, Sage, Conta Azul, Omie) — upload manual atende
- Importação de SPED ECD, ECF, eSocial, EFD-Reinf — fora do MVP
- ICMS-ST e DIFAL detalhados — aproximação geral atende; refinamento em fase 2
- Reforma tributária CBS/IBS — adicionar quando regulamentação estiver estável
- Multi-tenant SaaS com cobrança/planos — escritório single-tenant
- Dashboard gerencial multi-grupo agregado — fase 2
- Apuração de IRRF/Folha exterior, partic. lucros — fora do escopo principal
- Análise de regime do MEI (Microempreendedor Individual) — fora do escopo

---

## Session Summary

| Métrica | Valor |
|---------|-------|
| Perguntas de discovery | 6 |
| Abordagens exploradas | 3 |
| Features removidas (YAGNI) | 14 |
| Validações incrementais | 6 |
| Amostras analisadas | 4 tipos × 67+ arquivos |
| Casos reais identificados | 3 empresas/grupos (WIBE, SANREED, JP CONFECCOES) |
| Tributos mapeados | 8 (IRPJ, CSLL, COFINS, PIS, INSS/CPP, ICMS, IPI, ISS) |
| Regimes contemplados | 3 (Simples Nacional, Lucro Presumido, Lucro Real) |
| Anexos do Simples cobertos | 5 (I-V), com Fator R |

---

## Próximo Passo

**Pronto para:** `/define .claude/sdd/features/BRAINSTORM_PLANEJAMENTO_TRIBUTARIO.md`

A próxima fase (`/define`) deve transformar este brainstorm em requisitos formais (User Stories, critérios de aceitação, modelo de dados detalhado, contratos de API) usando o template `DEFINE_TEMPLATE.md`.
