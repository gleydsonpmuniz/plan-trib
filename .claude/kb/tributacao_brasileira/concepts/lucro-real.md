# Lucro Real

> **Purpose**: Regime tributário onde IRPJ/CSLL incidem sobre o lucro líquido contábil ajustado (adições/exclusões), e PIS/COFINS são não-cumulativos com direito a créditos.
> **Confidence**: 0.95
> **MCP Validated**: 2026-04-28

## Overview

Regime obrigatório para PJs com receita bruta anual > R$ 78 milhões e para atividades específicas (bancos, factoring, empresas com lucro/rendimento do exterior, etc. — Lei 9.718/98 art. 14). Opcional para as demais. A base de IRPJ/CSLL é o **lucro líquido contábil ajustado** por adições e exclusões previstas na legislação. PIS e COFINS são **não-cumulativos**, com direito a créditos sobre insumos.

## Apuração IRPJ/CSLL

### Sequência de Cálculo

```text
1. Lucro líquido contábil (DRE) — antes do IRPJ/CSLL
2. (+) Adições (multas indedutíveis, brindes, doações fora do limite, etc.)
3. (−) Exclusões (dividendos recebidos, equivalência patrimonial positiva, etc.)
4. (+) Compensação de prejuízos fiscais (limite 30% do LALUR positivo)
5. = Lucro Real (LALUR Parte A)

IRPJ = Lucro Real × 15% + Adicional 10% sobre o que exceder R$ 20.000/mês (R$ 60.000/trimestre)
CSLL = Lucro Real × 9%
```

### Periodicidade

| Modalidade | Quando | Apuração |
|-----------|--------|----------|
| **Trimestral** | Apuração definitiva trimestre a trimestre | Lucro real do trimestre |
| **Anual com estimativas** | Pagamento mensal por estimativa + balanço de suspensão/redução; ajuste anual em 31/dez | Lucro real anual |

A modalidade trimestral simplifica mas pode ser desvantajosa pois trimestres com prejuízo só compensam até 30% nos seguintes.

## PIS/COFINS Não-Cumulativo

| Tributo | Alíquota | Base | Créditos |
|---------|----------|------|----------|
| PIS | 1,65% | Receita bruta | ✅ Sobre insumos, energia, aluguéis, depreciação, etc. |
| COFINS | 7,60% | Receita bruta | ✅ Sobre os mesmos itens |

### Lista (resumida) de itens que geram crédito

- Bens adquiridos para revenda
- Bens e serviços usados como **insumo** (Lei 10.637/02 e 10.833/03)
- Energia elétrica e térmica
- Aluguéis de prédios, máquinas e equipamentos pagos a PJ
- Depreciação de máquinas, equipamentos e edificações
- Devoluções de vendas
- Vale-transporte, vale-refeição (com limites)

**Critério "insumo" — STJ e RFB**: bem ou serviço **essencial ou relevante** ao processo produtivo (REsp 1.221.170/PR; PN COSIT 5/2018).

## Quando o LR é Vantajoso

```text
Se lucro real efetivo < % presunção × receita:
  → LR paga IRPJ/CSLL sobre o lucro efetivo, menor que sobre presunção

Se a empresa tem muitos insumos creditáveis:
  → Créditos de PIS/COFINS reduzem a carga total (efetivo pode ficar < 9,25%)

Se prejuízo no exercício:
  → LR não paga IRPJ/CSLL; ainda gera prejuízo fiscal compensável
```

## Quando o LR é Desvantajoso

- Margens altas (paga sobre lucro real, maior que presunção)
- Poucos insumos (créditos de PIS/COFINS pequenos)
- Complexidade contábil-fiscal alta (ECD obrigatório, ECF, Bloco K, etc.)
- Risco fiscal (mais escriturações sujeitas a fiscalização)

## Documentos Obrigatórios

- **ECD** (SPED Contábil) — escrituração contábil completa
- **ECF** (Escrituração Contábil Fiscal) — apuração IRPJ/CSLL
- **EFD-Contribuições** — apuração PIS/COFINS não-cumulativo
- **EFD ICMS/IPI** — quando há essas operações

## Related

- [regimes-tributarios](regimes-tributarios.md)
- [lucro-presumido](lucro-presumido.md)
- [sped-contribuicoes](sped-contribuicoes.md)
