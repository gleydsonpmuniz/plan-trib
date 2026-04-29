# Pattern: Engine de Cálculo Multi-Regime

> **Purpose**: Arquitetura desacoplada para calcular Simples Nacional, Lucro Presumido e Lucro Real a partir do mesmo conjunto normalizado de dados, permitindo comparação determinística e simulação what-if.
> **MCP Validated**: 2026-04-28

## When to Use

- Sistemas de planejamento tributário comparativo
- Necessidade de testes determinísticos por regime (TDD)
- Simulação de cenários (what-if) sem reprocessar ingestão
- Evolução futura para novos regimes (ex.: CBS/IBS pós-reforma)

## Implementation

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import date
from typing import Protocol
from pydantic import BaseModel


# ─────────────────────── Modelo Normalizado (input) ───────────────────────

class DadosFiscaisCompetencia(BaseModel):
    """Snapshot mensal normalizado, alimentando QUALQUER calculadora."""
    cnpj: str
    competencia: date
    receita_bruta: Decimal
    receita_servicos: Decimal           # subset de receita
    receita_revenda: Decimal            # subset de receita
    receita_industrializacao: Decimal   # subset de receita

    # Insumos (créditos potenciais para LR)
    compras_com_credito: Decimal
    energia_eletrica: Decimal
    aluguel_pj: Decimal
    depreciacao: Decimal

    # Folha (de Folha PDF)
    folha_bruta: Decimal
    pro_labore: Decimal
    inss_patronal_total: Decimal
    fgts: Decimal

    # Despesas adicionais (formulário manual — só LR)
    despesas_administrativas: Decimal
    despesas_comerciais: Decimal
    despesas_tributarias: Decimal

    # Histórico para Fator R / RBT12
    receita_12m: Decimal
    folha_12m: Decimal


# ─────────────────────── Resultado (output uniforme) ───────────────────────

class Tributos(BaseModel):
    irpj: Decimal = Decimal(0)
    csll: Decimal = Decimal(0)
    pis: Decimal = Decimal(0)
    cofins: Decimal = Decimal(0)
    inss_cpp: Decimal = Decimal(0)
    icms: Decimal = Decimal(0)
    ipi: Decimal = Decimal(0)
    iss: Decimal = Decimal(0)

    @property
    def total(self) -> Decimal:
        return (self.irpj + self.csll + self.pis + self.cofins
                + self.inss_cpp + self.icms + self.ipi + self.iss)


class ResultadoApuracao(BaseModel):
    regime: str  # "SIMPLES" | "LP" | "LR"
    competencia: date
    tributos: Tributos
    aliquota_efetiva: Decimal           # tributos.total / receita_bruta
    detalhamento: dict[str, Decimal]     # bases, parcelas, etc. (auditoria)


# ─────────────────────── Interface comum ───────────────────────

class Calculadora(Protocol):
    def apurar(self, dados: DadosFiscaisCompetencia) -> ResultadoApuracao: ...


# ─────────────────────── Implementações ───────────────────────

class CalculadoraSimples:
    def __init__(self, tabelas_anexos: dict, fator_r_threshold: Decimal = Decimal("0.28")):
        self.tabelas = tabelas_anexos
        self.fator_r_threshold = fator_r_threshold

    def apurar(self, dados: DadosFiscaisCompetencia) -> ResultadoApuracao:
        anexo = self._mapear_anexo(dados)
        rbt12 = dados.receita_12m
        aliq_nominal, parcela_deduzir = self._buscar_faixa(anexo, rbt12)
        aliq_efetiva = (rbt12 * aliq_nominal - parcela_deduzir) / rbt12
        valor_total = dados.receita_bruta * aliq_efetiva
        tributos = self._distribuir_tributos(valor_total, anexo)
        return ResultadoApuracao(regime="SIMPLES", competencia=dados.competencia,
                                 tributos=tributos, aliquota_efetiva=aliq_efetiva,
                                 detalhamento={"anexo": Decimal(anexo), "rbt12": rbt12})

    def _mapear_anexo(self, dados: DadosFiscaisCompetencia) -> str: ...
    def _buscar_faixa(self, anexo: str, rbt12: Decimal) -> tuple[Decimal, Decimal]: ...
    def _distribuir_tributos(self, valor: Decimal, anexo: str) -> Tributos: ...


class CalculadoraLucroPresumido:
    def apurar(self, dados: DadosFiscaisCompetencia) -> ResultadoApuracao: ...


class CalculadoraLucroReal:
    def apurar(self, dados: DadosFiscaisCompetencia) -> ResultadoApuracao: ...


# ─────────────────────── Comparador ───────────────────────

def comparar_regimes(dados: DadosFiscaisCompetencia) -> dict[str, ResultadoApuracao]:
    return {
        "SIMPLES": CalculadoraSimples(...).apurar(dados),
        "LP": CalculadoraLucroPresumido().apurar(dados),
        "LR": CalculadoraLucroReal().apurar(dados),
    }
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `decimal_precision` | 6 | `Decimal` com 6 casas internamente; arredondar para 2 só na apresentação |
| `rounding` | `ROUND_HALF_EVEN` | Padrão tributário brasileiro (banker's rounding) |
| `tabelas_simples` | YAML versionado | Carregar de `specs/tabelas-simples-anexos.yaml` |
| `presuncao_lp` | YAML versionado | Carregar de `specs/presuncao-irpj-csll.yaml` |

## Princípios de Design

1. **Separação dados × cálculo**: `DadosFiscaisCompetencia` é puro modelo; calculadoras são puras funções.
2. **Saída uniforme**: as 3 calculadoras retornam `ResultadoApuracao` para comparação trivial.
3. **Tabelas versionadas em YAML**: alíquotas e percentuais não vivem no código.
4. **Determinístico**: mesmas entradas → mesmas saídas. Necessário para TDD com fixtures reais.
5. **Auditável**: `detalhamento` traz bases e parcelas — necessário para explicar resultado ao cliente.

## Simulação What-If

```python
def simular_cenario(base: DadosFiscaisCompetencia, overrides: dict) -> dict:
    cenario = base.model_copy(update=overrides)
    return comparar_regimes(cenario)

# Exemplo: "e se folha aumentar 20%?"
simular_cenario(dados_atual, {"folha_bruta": dados_atual.folha_bruta * Decimal("1.2")})
```

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Acoplar parser SPED ao cálculo | Normalizar primeiro em `DadosFiscaisCompetencia` |
| Hard-codar tabelas no Python | YAML versionado em `specs/` |
| `float` em qualquer ponto | `Decimal` end-to-end |
| Lógica condicional gigante por regime | Polimorfismo via Protocol/ABC |

## See Also

- [regimes-tributarios](../concepts/regimes-tributarios.md)
- [simples-nacional](../concepts/simples-nacional.md)
- Specs: `../specs/tabelas-simples-anexos.yaml`, `../specs/presuncao-irpj-csll.yaml`
