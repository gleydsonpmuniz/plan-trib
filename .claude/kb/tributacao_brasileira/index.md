# Tributação Brasileira — Knowledge Base

> **Purpose**: Conhecimento curado sobre os três regimes tributários brasileiros (Simples Nacional, Lucro Presumido, Lucro Real), estrutura dos SPEDs (EFD ICMS/IPI, EFD-Contribuições), PGDAS-D e patterns para sistemas de planejamento tributário comparativo.
> **MCP Validated**: 2026-04-28

## Quick Navigation

### Concepts (≤ 150 linhas cada)

| Arquivo | Propósito |
|---------|-----------|
| [concepts/regimes-tributarios.md](concepts/regimes-tributarios.md) | Visão geral comparativa dos três regimes — quando escolher cada um |
| [concepts/simples-nacional.md](concepts/simples-nacional.md) | LC 123/2006, Anexos I-V, Fator R, sublimites |
| [concepts/lucro-presumido.md](concepts/lucro-presumido.md) | % presunção por atividade, PIS/COFINS cumulativo, INSS Patronal |
| [concepts/lucro-real.md](concepts/lucro-real.md) | Lucro líquido contábil ajustado, PIS/COFINS não-cumulativo c/ créditos |
| [concepts/sped-fiscal-efd.md](concepts/sped-fiscal-efd.md) | Estrutura, blocos, leiaute v019, registros C100/C170/E110 |
| [concepts/sped-contribuicoes.md](concepts/sped-contribuicoes.md) | Estrutura, blocos, regimes (cumul/não-cumul), F550 e M200/M600 |
| [concepts/pgdas-d.md](concepts/pgdas-d.md) | Declaração do Simples — RBT12, Fator R, débito por estabelecimento |

### Patterns (≤ 200 linhas cada)

| Arquivo | Propósito |
|---------|-----------|
| [patterns/parsing-sped-pipe.md](patterns/parsing-sped-pipe.md) | Parser SPED Python + Pydantic, versionado, stream-based |
| [patterns/extracao-pdf-llm.md](patterns/extracao-pdf-llm.md) | Extração de PDFs (folha, PGDAS-D) via Gemini c/ saída estruturada |
| [patterns/calculo-multi-regime.md](patterns/calculo-multi-regime.md) | Engine desacoplado para apurar e comparar os 3 regimes |

### Specs (Machine-Readable, sem limite)

| Arquivo | Propósito |
|---------|-----------|
| [specs/tabelas-simples-anexos.yaml](specs/tabelas-simples-anexos.yaml) | Anexos I-V — faixas, alíquotas nominais, parcelas a deduzir |
| [specs/presuncao-irpj-csll.yaml](specs/presuncao-irpj-csll.yaml) | % presunção IRPJ/CSLL por atividade (Lei 9.249/95) |
| [specs/leiautes-sped-versoes.yaml](specs/leiautes-sped-versoes.yaml) | Versões de leiaute SPED + bibliotecas Python referência |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) — alíquotas, limites, decisão rápida

---

## Key Concepts

| Conceito | Descrição |
|----------|-----------|
| **RBT12** | Receita Bruta dos últimos 12 meses — define faixa do Anexo no Simples |
| **Fator R** | (Folha + Pró-labore) / Receita 12m — define Anexo III (≥28%) ou V (<28%) |
| **Cumulativo × Não-Cumulativo** | Regime PIS/COFINS — define se há direito a créditos sobre insumos |
| **Lucro Presumido** | Base IRPJ/CSLL = % presunção × receita (8%/12%/16%/32%) |
| **Lucro Real** | Base IRPJ/CSLL = lucro líquido contábil + adições − exclusões |
| **DAS** | Documento de Arrecadação do Simples Nacional — guia única mensal |
| **CFOP** | Código Fiscal de Operações e Prestações — identifica origem/destino e natureza |
| **CST** | Código de Situação Tributária — para ICMS, PIS, COFINS, IPI |

---

## Learning Path

| Nível | Sequência sugerida |
|-------|---------------------|
| **Iniciante** | regimes-tributarios → simples-nacional → lucro-presumido → lucro-real |
| **Intermediário** | sped-fiscal-efd → sped-contribuicoes → pgdas-d |
| **Avançado** | patterns/parsing-sped-pipe → patterns/extracao-pdf-llm → patterns/calculo-multi-regime |

---

## Fontes Oficiais

| Fonte | URL |
|-------|-----|
| Receita Federal — SPED | <http://sped.rfb.gov.br/> |
| LC 123/2006 (Simples) | <http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm> |
| Lei 9.249/95 (LP) | <http://www.planalto.gov.br/ccivil_03/leis/l9249.htm> |
| PGDAS-D | <http://www8.receita.fazenda.gov.br/SimplesNacional/> |
| Reforma Tributária (LC 214/2025) | <https://www.gov.br/fazenda/pt-br/acesso-a-informacao/acoes-e-programas/reforma-tributaria> |
