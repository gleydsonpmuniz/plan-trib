# Tributação Brasileira — Quick Reference

> Tabelas de consulta rápida. Para detalhes, ver arquivos linkados.

## Limites de Receita (anuais)

| Regime | Limite |
|--------|--------|
| Simples Nacional (federal) | R$ 4.800.000 |
| Simples — sublimite ICMS/ISS | R$ 3.600.000 |
| Lucro Presumido | R$ 78.000.000 |
| Lucro Real | sem limite (obrigatório > R$ 78M) |

## Alíquotas-Chave por Regime

| Tributo | Simples | LP | LR |
|---------|---------|-----|-----|
| PIS | embutido no DAS | 0,65% cumul. | 1,65% não-cumul. (créditos) |
| COFINS | embutido no DAS | 3,00% cumul. | 7,60% não-cumul. (créditos) |
| IRPJ | embutido no DAS | 15% × presunção | 15% × lucro real |
| CSLL | embutido no DAS | 9% × presunção | 9% × lucro real |
| Adicional IRPJ | — | 10% s/ excedente R$ 60k/trim | 10% s/ excedente R$ 60k/trim |

## Presunção IRPJ/CSLL (LP) — Lei 9.249/95

| Atividade | Presunção IRPJ | Presunção CSLL |
|-----------|----------------|----------------|
| Comércio, indústria, transporte cargas | 8% | 12% |
| Combustíveis | 1,6% | 12% |
| Transporte de passageiros | 16% | 12% |
| Hospitalar | 8% | 12% |
| Serviços profissionais | 32% | 32% |

## Anexos do Simples (alíquotas iniciais)

| Anexo | Atividade | Alíq. faixa 1 | Máx. faixa 6 |
|-------|-----------|---------------|--------------|
| I | Comércio | 4,00% | 19,00% |
| II | Indústria | 4,50% | 30,00% |
| III | Serviços / Fator R≥28% | 6,00% | 33,00% |
| IV | Construção/Vigilância | 4,50% | 33,00% |
| V | Serviços / Fator R<28% | 15,50% | 30,50% |

Tabela completa: `specs/tabelas-simples-anexos.yaml`

## Decisão de Regime (heurística)

| Cenário | Regime sugerido |
|---------|-----------------|
| RBT12 ≤ R$ 4,8M e atividade permitida | **Avaliar Simples** |
| Margem de lucro > % presunção | **LP** (paga sobre presunção, não sobre lucro real) |
| Margem baixa, prejuízo, ou muitos créditos PIS/COFINS | **LR** (não-cumulativo + base real) |
| Receita > R$ 78M | **LR obrigatório** |
| Atividade vedada ao LP (banco, seguradora) | **LR obrigatório** |
| Serviços com folha alta (Fator R ≥ 28%) | Anexo III (não V) — vantajoso no Simples |

## SPEDs Relevantes (MVP)

| SPED | Periodicidade | Encoding | Versão atual |
|------|--------------|----------|--------------|
| EFD ICMS/IPI | Mensal | ISO-8859-1 | v019 |
| EFD-Contribuições | Mensal | ISO-8859-1 | v006 |
| PGDAS-D (PDF) | Mensal | PDF | Padrão RFB |
| Folha (PDF) | Mensal | PDF | Variável por sistema |

## Pegadinhas Comuns

| Não faça | Faça |
|----------|------|
| Usar `float` para valores monetários | `Decimal` end-to-end |
| Abrir SPED com encoding default | `encoding="iso-8859-1"` |
| Hard-codar alíquotas no Python | Carregar de YAML em `specs/` |
| Esquecer exclusão do ICMS na base PIS/COFINS | Aplicar RE 574.706/STF |
| Tratar grupo como CNPJ único | Modelar `Grupo → Empresas (1:N)` com matriz/filial |
| Confundir RBT12 com receita do mês | RBT12 = soma 12 meses; define faixa |

## Documentação Relacionada

| Tópico | Caminho |
|--------|---------|
| Visão geral dos regimes | `concepts/regimes-tributarios.md` |
| Estrutura SPED | `concepts/sped-fiscal-efd.md`, `concepts/sped-contribuicoes.md` |
| Patterns de implementação | `patterns/` |
| Tabelas estruturadas | `specs/` |
| Índice completo | `index.md` |
