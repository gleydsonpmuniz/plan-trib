# SPED Fiscal (EFD ICMS/IPI)

> **Purpose**: Escrituração Fiscal Digital de ICMS e IPI — arquivo TXT pipe-delimited com movimento fiscal mensal por estabelecimento.
> **Confidence**: 0.95
> **MCP Validated**: 2026-04-28

## Overview

A EFD ICMS/IPI é uma obrigação acessória mensal entregue por contribuintes do ICMS e/ou IPI à Sefaz/RFB. Contém todas as notas fiscais (entrada/saída), inventário, apuração de impostos e dados auxiliares. É um arquivo texto com registros separados por blocos hierárquicos. **Leiaute atual: v019** (vigência 2024+).

## Estrutura do Arquivo

```text
Arquivo .txt (separador "|", sem cabeçalho/rodapé especial)
└── Registros, um por linha
    └── Cada registro: |TIPO|campo1|campo2|...|

Exemplo:
|0000|019|0|01012025|31012025|EMPRESA LTDA|12345678000100||SP|123456789|3550308|||A|1|
```

## Blocos

| Bloco | Conteúdo | Obrigatoriedade |
|-------|----------|-----------------|
| **0** | Cadastros (empresa, contador, participantes, itens, plano de contas) | Sempre |
| **B** | ISS — apuração de serviços (DF apenas) | Condicional |
| **C** | Documentos fiscais — mercadorias (NF-e, NFC-e, ECF) | Sempre |
| **D** | Documentos fiscais — serviços (CT-e, transporte) | Condicional |
| **E** | Apuração ICMS e IPI | Sempre |
| **G** | Controle do Crédito de ICMS do Ativo Permanente (CIAP) | Condicional |
| **H** | Inventário | Sempre (anualmente, comp. fevereiro) |
| **K** | Controle de Produção e Estoque (Bloco K) | Indústrias |
| **1** | Outras informações (DIFAL, ressarcimento, etc.) | Condicional |
| **9** | Controle e encerramento (totalizador de registros) | Sempre |

## Registros-Chave

| Registro | Conteúdo | Crítico para |
|----------|----------|--------------|
| `0000` | Identificação (CNPJ, IE, perfil, atividade A/I/O) | Cabeçalho |
| `0150` | Tabela de participantes (clientes, fornecedores) | Cruzamento |
| `0200` | Tabela de itens (produtos/mercadorias) | Análise por SKU |
| `C100` | Nota fiscal (capa: emitente, dest., valores totais, ICMS, IPI) | **Faturamento** |
| `C170` | Itens da nota fiscal (UM, qtd, valor unit., CFOP, CST, base ICMS) | **Detalhamento** |
| `C190` | Análise consolidada de C100 por CST/CFOP/alíquota | **Apuração** |
| `E100` | Período da apuração ICMS | Apuração |
| `E110` | Apuração ICMS — débitos, créditos, saldos | **Apuração ICMS** |
| `E200/E210` | Apuração IPI | Indústrias |
| `H010` | Inventário por item | Lucro Real |

## Indicador de Atividade (campo `0000.IND_ATIV`)

| Valor | Significado |
|-------|-------------|
| `0` | Industrial ou equiparado |
| `1` | Outros (comércio, serviços) |

## Perfil (campo `0000.COD_FIN`)

| Valor | Significado |
|-------|-------------|
| `0` | Original |
| `1` | Substituto (retificação) |

## Aspectos Críticos para Planejamento

1. **Faturamento por CFOP**: bloco C190 consolida vendas por CFOP — base para análise de origem de receita (interno × interestadual × exterior).
2. **Saldo credor de ICMS**: registro E110 traz o saldo a transportar — empresa com saldo credor crônico é candidata a revisão de regime.
3. **Multi-CNPJ**: cada estabelecimento tem seu próprio arquivo SPED Fiscal (não é consolidado).
4. **Versionamento**: a RFB publica novo leiaute anualmente; o parser deve detectar e tratar a versão.

## Validação Cruzada

- Soma de C190 (por CST/CFOP) deve bater com totalizadores em E110
- Inventário H010 (anual) deve ser compatível com movimento C100/C170 ao longo do exercício
- Item de C170 deve existir na tabela 0200

## Related

- [sped-contribuicoes](sped-contribuicoes.md)
- [parsing-sped-pipe](../patterns/parsing-sped-pipe.md)
- Spec: `../specs/leiautes-sped-versoes.yaml`
- Fonte oficial: <http://sped.rfb.gov.br/projeto/show/1>
