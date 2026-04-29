# Regimes Tributários (Visão Geral)

> **Purpose**: Comparativo dos três regimes de tributação federal das pessoas jurídicas no Brasil: Simples Nacional, Lucro Presumido e Lucro Real.
> **Confidence**: 0.95
> **MCP Validated**: 2026-04-28

## Overview

A pessoa jurídica brasileira escolhe anualmente seu regime tributário. A escolha define como serão apurados IRPJ, CSLL, PIS, COFINS, ICMS, IPI, ISS e contribuições previdenciárias. Cada regime tem limites de receita, regras de apuração e impactos diferentes na carga tributária total.

## Comparativo Sintético

| Aspecto | Simples Nacional | Lucro Presumido | Lucro Real |
|---------|------------------|-----------------|------------|
| **Base legal** | LC 123/2006 | Lei 9.249/95, Art. 13 da Lei 9.718/98 | Decreto 9.580/2018 (RIR), Lei 9.430/96 |
| **Limite de receita** | R$ 4,8M/ano (sublimite ICMS R$ 3,6M) | R$ 78M/ano | Sem limite (obrigatório acima de R$ 78M) |
| **IRPJ + CSLL** | Recolhidos no DAS único | 15%+10% s/ lucro presumido (8%/12%/16%/32% s/ receita) | 15%+10% s/ lucro real ajustado |
| **PIS/COFINS** | No DAS | Cumulativo: 0,65% + 3% s/ receita | Não-cumulativo: 1,65% + 7,6% c/ créditos |
| **ICMS** | No DAS (até sublimite) | Apuração normal por CFOP/CST | Apuração normal por CFOP/CST |
| **INSS Patronal** | No DAS (alíquotas reduzidas Anexos I-V) | 20% folha + 5,8% terceiros + RAT 1-3% | 20% folha + 5,8% terceiros + RAT 1-3% |
| **Periodicidade** | Mensal (DAS) | Trimestral (IRPJ/CSLL) ou mensal (demais) | Trimestral ou anual c/ estimativas mensais |
| **Quem pode optar** | ME/EPP que não exerçam atividades vedadas | Maioria das PJs até R$ 78M | Qualquer PJ; obrigatório acima R$ 78M ou em atividades específicas (bancos, seguradoras) |

## Critérios de Escolha

```text
Empresa nova ou pequena? (RBT12 ≤ R$ 4,8M)
├─ Sim → AVALIAR Simples Nacional
│       ├─ Atividade permitida? (não é vedada pela LC 123)
│       ├─ Carga tributária real é menor que LP/LR?
│       └─ Folha alta? (Fator R favorece Anexo III)
└─ Não → ESCOLHER entre LP × LR
        ├─ Margem de lucro alta (> presunção)? → LP é vantajoso
        ├─ Margem baixa ou prejuízo? → LR é vantajoso
        ├─ Muitos créditos de PIS/COFINS (insumos)? → LR (não-cumulativo)
        └─ Receita > R$ 78M ou atividade vedada ao LP? → LR obrigatório
```

## Decisão Estratégica

A escolha do regime é **anual e irretratável** (com poucas exceções). Erros de escolha custam até 10-15% da receita anual em tributos pagos a mais. Por isso, o **planejamento tributário comparativo** é uma das atividades de maior valor que um contador entrega.

## Pontos de Atenção

- **Empresas em transição (próximas ao R$ 4,8M)**: precisam simular cenário futuro pós-saída do Simples
- **Indústrias com IPI**: PI cobra IPI no Simples (Anexo II), no LP/LR pode haver créditos
- **Serviços com Fator R**: cálculo do (folha+pró-labore)/receita 12m define Anexo III ou V — diferença grande na carga
- **Reforma tributária (LC 214/2025)**: introdução gradual de CBS/IBS de 2027 a 2033 alterará a comparação — projeto deve estar pronto para evolução

## Related

- [simples-nacional](simples-nacional.md)
- [lucro-presumido](lucro-presumido.md)
- [lucro-real](lucro-real.md)
- [calculo-multi-regime](../patterns/calculo-multi-regime.md)
