# SPED Contribuições (EFD-Contribuições)

> **Purpose**: Escrituração Fiscal Digital das Contribuições (PIS, COFINS, CPRB) — arquivo TXT pipe-delimited com apuração mensal de PIS/COFINS, suportando regimes cumulativo e não-cumulativo.
> **Confidence**: 0.95
> **MCP Validated**: 2026-04-28

## Overview

A EFD-Contribuições, instituída pela IN RFB 1.252/2012, é entregue mensalmente por todas as PJs sujeitas ao recolhimento de PIS/COFINS (exceto Simples). Suporta os regimes cumulativo (Lucro Presumido — alíquotas 0,65%/3%) e não-cumulativo (Lucro Real — alíquotas 1,65%/7,6% com créditos), além da Contribuição Previdenciária sobre Receita Bruta (CPRB). **Leiaute atual: v006** (vigência 2024+).

## Estrutura do Arquivo

```text
Arquivo .txt (separador "|", certificado digital ICP-Brasil ao final)
└── Registros agrupados em blocos
    └── Cada registro: |TIPO|campo1|campo2|...|

Exemplo:
|0000|006|0|||01012025|31012025|EMPRESA LTDA|12345678000100|SP|3550308||00|9|
```

## Blocos

| Bloco | Conteúdo |
|-------|----------|
| **0** | Identificação, contador, estabelecimentos, plano de contas |
| **A** | Documentos fiscais — serviços (NFS-e, etc.) |
| **C** | Documentos fiscais — mercadorias (espelho do EFD ICMS/IPI) |
| **D** | Documentos fiscais — serviços de transporte |
| **F** | Demais documentos e operações (consolidações, créditos especiais) |
| **I** | Operações de instituições financeiras |
| **M** | Apuração consolidada de PIS e COFINS |
| **P** | CPRB (Contribuição Previdenciária sobre Receita Bruta — desoneração da folha) |
| **1** | Controle e ajustes (1900: receita por estabelecimento) |
| **9** | Encerramento e controle de registros |

## Registros-Chave

| Registro | Conteúdo | Crítico para |
|----------|----------|--------------|
| `0000` | Identificação, leiaute, período | Cabeçalho |
| `0110` | **Indicador de Regime de Apuração** (cumul./não-cumul.) | **Define LP × LR** |
| `0140` | Tabela de estabelecimentos (multi-CNPJ no mesmo arquivo) | Multi-empresa |
| `A100/C100/D100` | Documentos individuais (regime não-cumulativo) | Detalhamento |
| `F550` | **Consolidação por CST/CFOP** (regime cumulativo) | **Apuração LP** |
| `M200/M210` | **Apuração consolidada PIS** | **Total PIS devido** |
| `M600/M610` | **Apuração consolidada COFINS** | **Total COFINS devido** |
| `1900` | Receita bruta por estabelecimento | Multi-CNPJ |

## Indicador de Regime (`0110.COD_INC_TRIB`)

| Valor | Significado | Aplica-se a |
|-------|-------------|-------------|
| `1` | Regime **não-cumulativo** | Lucro Real |
| `2` | Regime **cumulativo** | Lucro Presumido |
| `3` | Regimes não-cumulativo **e** cumulativo (atividades mistas) | Atividades mistas |

## CSTs (Código de Situação Tributária) PIS/COFINS

Os CSTs principais — campo presente em F550, C170 etc.:

| CST | Tributação |
|-----|------------|
| `01` | Tributação alíquota básica (cumulativo: 0,65% PIS / 3% COFINS) |
| `02` | Tributação alíquota diferenciada |
| `03` | Tributação por unidade de medida (monofásico) |
| `04` | Tributação monofásica revenda |
| `06` | Alíquota zero |
| `07` | Isento |
| `08` | Sem incidência |
| `49` | Outras saídas tributadas |

## Exclusão do ICMS da Base (RE 574.706/STF)

Desde 2017, o ICMS destacado nas notas é excluído da base de cálculo de PIS/COFINS. Nos arquivos SPED, isso aparece em F550 com observação textual: **"Valor X referente à exclusão do ICMS destacado"**.

## Aspectos Críticos para Planejamento

1. **Identificação de regime**: o registro 0110 confirma se a empresa está em LP (cumulativo) ou LR (não-cumulativo).
2. **Multi-CNPJ no mesmo arquivo**: diferentemente do EFD ICMS/IPI, a EFD-Contribuições agrupa todos os estabelecimentos em um arquivo único (registros F010 separam blocos por CNPJ).
3. **Créditos de PIS/COFINS (LR)**: bloco M e registros C170/A170 detalham os créditos sobre insumos.
4. **Comparação automática**: somando F550 (cumulativo) vs. C170 (não-cumulativo) é possível simular a outra apuração.

## Related

- [sped-fiscal-efd](sped-fiscal-efd.md)
- [lucro-presumido](lucro-presumido.md)
- [lucro-real](lucro-real.md)
- [parsing-sped-pipe](../patterns/parsing-sped-pipe.md)
- Fonte oficial: <http://sped.rfb.gov.br/projeto/show/2>
