# Lucro Presumido

> **Purpose**: Regime tributário simplificado onde IRPJ/CSLL incidem sobre uma base de lucro presumida (% sobre receita), e PIS/COFINS são cumulativos.
> **Confidence**: 0.95
> **MCP Validated**: 2026-04-28

## Overview

Regime opcional para pessoas jurídicas com receita bruta anual ≤ R$ 78 milhões (Lei 12.814/2013). A base de cálculo de IRPJ e CSLL é calculada aplicando-se um **percentual de presunção** sobre a receita bruta — independentemente do lucro real. PIS e COFINS são cumulativos (sem créditos), com alíquotas reduzidas (0,65% + 3%).

## Apuração IRPJ/CSLL

### Percentuais de Presunção (Lei 9.249/95, Art. 15)

| Atividade | Presunção IRPJ | Presunção CSLL |
|-----------|----------------|----------------|
| Revenda de combustíveis e gás natural | 1,6% | 12% |
| Comércio em geral, indústria, transporte de cargas | 8% | 12% |
| Serviços hospitalares, transporte de passageiros | 8% (hosp.) / 16% (passag.) | 12% |
| Prestação de serviços em geral (até R$ 120k/ano) | 16% | 32% |
| Serviços profissionais, intermediação, administração | **32%** | **32%** |
| Construção civil (empreitada total) | 8% | 12% |

### Cálculo Trimestral

```text
Base IRPJ = Receita_Bruta_Trimestral × % Presunção_IRPJ + Outras_Receitas
IRPJ = Base × 15% + Adicional 10% sobre o que exceder R$ 60.000/trimestre

Base CSLL = Receita_Bruta_Trimestral × % Presunção_CSLL + Outras_Receitas
CSLL = Base × 9%
```

## PIS/COFINS Cumulativo

| Tributo | Alíquota | Base | Créditos |
|---------|----------|------|----------|
| PIS | 0,65% | Receita bruta (com exclusões legais) | ❌ Não há |
| COFINS | 3,00% | Receita bruta (com exclusões legais) | ❌ Não há |

**Importante:** desde RE 574.706 (STF), o ICMS destacado nas notas é **excluído da base** de PIS/COFINS — ver registro F550 do SPED Contribuições.

## ICMS

Apuração normal (débito × crédito) por estabelecimento, mensal, conforme legislação estadual. Não compõe o lucro presumido.

## INSS Patronal

Sem benefício do regime — recolhimento normal:
- 20% sobre folha (CPP)
- RAT 1%, 2% ou 3% (com Fator Acidentário FAP)
- Terceiros (5,8% comércio/indústria; varia por atividade — Salário-Educação, INCRA, Sebrae, Sesc/Sesi/Senac/Senai)

## Quando o LP é Vantajoso

```text
Se o lucro real efetivo > % presunção × receita:
  → LP paga IRPJ/CSLL menor (sobre presunção, não sobre lucro real)

Se a empresa tem poucos insumos (créditos PIS/COFINS):
  → LP cumulativo (3,65%) pode ser melhor que LR não-cumulativo (9,25% c/ créditos)
```

## Quando o LP é Desvantajoso

- Empresa com prejuízo ou margem baixa (paga sobre presunção mesmo sem lucro)
- Atividade com muitos insumos creditáveis (LR aproveita créditos)
- Empresa que distribui dividendos altos vs. pró-labore (no LP, o lucro presumido pode limitar distribuição isenta)

## Related

- [regimes-tributarios](regimes-tributarios.md)
- [lucro-real](lucro-real.md)
- [sped-contribuicoes](sped-contribuicoes.md)
- Spec: `../specs/presuncao-irpj-csll.yaml`
