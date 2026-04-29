# Simples Nacional

> **Purpose**: Regime tributário unificado para Microempresas (ME) e Empresas de Pequeno Porte (EPP) com recolhimento em DAS único.
> **Confidence**: 0.95
> **MCP Validated**: 2026-04-28

## Overview

Instituído pela Lei Complementar 123/2006, unifica oito tributos (IRPJ, CSLL, PIS, COFINS, IPI, ICMS, ISS, INSS Patronal) em uma guia única (DAS). A alíquota efetiva varia conforme a Receita Bruta dos últimos 12 meses (RBT12) e o Anexo aplicável (I a V), determinado pela atividade exercida.

## Anexos

| Anexo | Atividade | Faixa de Alíquota | Tributos incluídos |
|-------|-----------|--------------------|---------------------|
| **I** | Comércio (revenda) | 4,00% – 19,00% | IRPJ, CSLL, COFINS, PIS, INSS, ICMS |
| **II** | Indústria | 4,50% – 30,00% | I + IPI |
| **III** | Serviços (locação, agência, etc.) e serviços com Fator R ≥ 28% | 6,00% – 33,00% | IRPJ, CSLL, COFINS, PIS, INSS, ISS |
| **IV** | Serviços de construção, vigilância, limpeza | 4,50% – 33,00% | Sem INSS no DAS — recolhe à parte (20% + RAT + terceiros) |
| **V** | Serviços com Fator R < 28% | 15,50% – 30,50% | IRPJ, CSLL, COFINS, PIS, INSS, ISS |

## Cálculo da Alíquota Efetiva

```text
Alíquota Efetiva = ((RBT12 × Alíq_Nominal) − PD) / RBT12
```

Onde:
- `RBT12` = Receita Bruta Total dos últimos 12 meses
- `Alíq_Nominal` = alíquota nominal da faixa de RBT12
- `PD` = Parcela a Deduzir da faixa

**Exemplo (Anexo I, RBT12 = R$ 1.000.000):**
- Faixa: R$ 720.000,01 a R$ 1.800.000,00
- Alíquota nominal: 10,70%
- PD: R$ 22.500,00
- Alíq. efetiva = (1.000.000 × 0,107 − 22.500) / 1.000.000 = **8,45%**

## Fator R (Anexos III × V)

```text
Fator R = (Folha 12m + Pró-labore 12m) / Receita Bruta 12m
```

- Fator R **≥ 28%** → atividade tributada pelo **Anexo III**
- Fator R **< 28%** → atividade tributada pelo **Anexo V** (alíquota maior)

A diferença entre Anexo III e V pode ser de até 15 pontos percentuais — é uma das alavancas mais relevantes do planejamento.

## Sublimites

| Tipo | Valor (anual) | Consequência se ultrapassar |
|------|---------------|------------------------------|
| Federal (Simples) | R$ 4.800.000,00 | Exclusão do Simples |
| Estadual (ICMS/ISS) | R$ 3.600.000,00 | Recolhe ICMS/ISS por fora (regime normal); IRPJ/CSLL/PIS/COFINS continuam no DAS |

## Atividades Vedadas (resumo)

- Bancos, seguradoras, instituições financeiras
- Geração/transmissão/distribuição de energia
- Importação/fabricação de automóveis, motos, embarcações
- Cervejarias, fabricação de cigarros, refino de petróleo
- Cessão de mão de obra (exceto Anexo IV permitidos)

Lista completa: LC 123/2006, art. 17.

## Related

- [regimes-tributarios](regimes-tributarios.md)
- [pgdas-d](pgdas-d.md)
- Spec: `../specs/tabelas-simples-anexos.yaml`
