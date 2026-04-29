# PGDAS-D (Declaração do Simples Nacional)

> **Purpose**: Programa Gerador do Documento de Arrecadação do Simples Nacional - Declaratório — declaração mensal apresentada por todos os optantes do Simples Nacional, contendo receita, RBT12 e tributos apurados por estabelecimento.
> **Confidence**: 0.95
> **MCP Validated**: 2026-04-28

## Overview

O PGDAS-D é uma aplicação online da Receita Federal onde a empresa do Simples Nacional declara mensalmente sua receita bruta. O sistema calcula automaticamente os tributos do DAS, aplicando a tabela do Anexo correspondente sobre a faixa de RBT12. O extrato gerado em PDF é o documento usado em planejamentos tributários para conhecer a carga tributária "AS IS" da empresa no Simples.

## Estrutura do Extrato (PDF)

| Seção | Conteúdo | Crítico para |
|-------|----------|--------------|
| **1. Identificação** | CNPJ matriz, razão social, optante (Sim/Não), regime (Competência/Caixa), filiais presentes | Cadastro |
| **2.1 Discriminativo** | RPA, RBT12, RBT12p, RBA, RBAA, limite proporcional | **Base de cálculo** |
| **2.2 Receitas Anteriores** | 14 meses históricos (mercado interno + externo) | **Projeção/tendência** |
| **2.3 Folha Anterior** | Histórico de folha mensal (quando aplicável) | **Fator R** |
| **2.4 Fator r** | Cálculo do fator (folha+pró-labore 12m / receita 12m) | **Anexo III × V** |
| **2.5 Valores Fixos** | Tributação por valor fixo (raros casos) | Especial |
| **2.6 Resumo** | Receita do mês + débito total | Síntese |
| **2.7 Por Estabelecimento** | Detalhamento por CNPJ + atividade textual + 8 tributos | **Detalhamento** |
| **2.8 Total Geral** | Consolidado da empresa | Total |
| **3. Recepção** | Recibo, autenticação, data transmissão | Validação |

## Conceitos-Chave

### RBT12 (Receita Bruta dos últimos 12 meses)

```text
RBT12 = soma das receitas brutas dos 12 meses anteriores ao período de apuração
```

Define a **faixa** na tabela do Anexo. Quanto maior a RBT12, maior a alíquota nominal.

### RBT12p (Proporcionalizada)

Aplicada quando a empresa tem menos de 13 meses de existência. Calcula-se proporcionalmente aos meses de atividade.

### RBA (Ano Calendário Corrente) e RBAA (Ano Anterior)

Importantes para verificar se a empresa está dentro do limite anual de R$ 4.800.000 (federal) ou R$ 3.600.000 (sublimite estadual ICMS/ISS).

## Tributos Discriminados (8 colunas)

A seção 2.7 traz os valores apurados por tributo:

| Tributo | Anexo I | Anexo II | Anexo III | Anexo IV | Anexo V |
|---------|---------|----------|-----------|----------|---------|
| IRPJ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CSLL | ✅ | ✅ | ✅ | ✅ | ✅ |
| COFINS | ✅ | ✅ | ✅ | ✅ | ✅ |
| PIS/Pasep | ✅ | ✅ | ✅ | ✅ | ✅ |
| INSS/CPP | ✅ | ✅ | ✅ | ❌ (recolhe à parte) | ✅ |
| ICMS | ✅ | ✅ | ❌ | ❌ | ❌ |
| IPI | ❌ | ✅ | ❌ | ❌ | ❌ |
| ISS | ❌ | ❌ | ✅ | ✅ | ✅ |

## Mapeamento Atividade → Anexo

A seção 2.7 traz a **descrição textual da atividade** (ex.: "Revenda de mercadorias..."). Mapeamento típico:

| Texto frequente no PGDAS | Anexo |
|--------------------------|-------|
| "Revenda de mercadorias..." | I (comércio) |
| "Venda de mercadorias industrializadas pelo contribuinte..." | II (indústria) |
| "Locação de bens móveis" | III |
| "Serviços de construção", "Limpeza", "Vigilância" | IV |
| "Serviços profissionais..." (com Fator R < 28%) | V |

Para o sistema, manter uma **tabela de mapeamento** + **fallback LLM** (categorizar atividades novas).

## Aspectos Críticos para Planejamento

1. **Fonte de "AS IS" para empresas no Simples**: o PGDAS-D já fornece o tributo pago — basta extrair.
2. **14 meses de histórico** na seção 2.2 — base rica para projeções sem precisar de outras fontes.
3. **Sublimite estadual**: campo "Impedido de recolher ICMS/ISS no DAS" sinaliza ultrapassagem.
4. **Empresas sem PGDAS**: para empresas em LP/LR, o sistema precisa **simular** o Simples aplicando tabelas oficiais sobre dados do EFD/folha — não há PGDAS para essas.

## Related

- [simples-nacional](simples-nacional.md)
- [extracao-pdf-llm](../patterns/extracao-pdf-llm.md)
- Fonte oficial: <http://www8.receita.fazenda.gov.br/SimplesNacional/>
