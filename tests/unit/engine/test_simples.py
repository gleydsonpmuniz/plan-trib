from datetime import date
from decimal import Decimal

from src.engine import CalculadoraSimples
from src.engine.inputs import DadosFiscaisCompetencia


def _dados_base(**override) -> DadosFiscaisCompetencia:  # type: ignore[no-untyped-def]
    base = dict(
        cnpj="12345678000100",
        competencia=date(2025, 6, 1),
        uf="ES",
        receita_bruta=Decimal("100000"),
        receita_revenda=Decimal("100000"),
        receita_12m=Decimal("1200000"),
    )
    base.update(override)
    return DadosFiscaisCompetencia(**base)


def test_anexo_i_faixa_baixa() -> None:
    dados = _dados_base(receita_bruta=Decimal("10000"), receita_12m=Decimal("100000"))
    resultado = CalculadoraSimples().apurar(dados)
    assert resultado.regime == "SIMPLES"
    assert resultado.detalhamento["anexo"] == "I"
    assert resultado.tributos.total > 0


def test_anexo_ii_industria() -> None:
    dados = _dados_base(
        receita_bruta=Decimal("50000"),
        receita_revenda=Decimal(0),
        receita_industrializacao=Decimal("50000"),
        atividade_descricao="Venda de mercadorias industrializadas pelo contribuinte",
        receita_12m=Decimal("600000"),
    )
    resultado = CalculadoraSimples().apurar(dados)
    assert resultado.detalhamento["anexo"] == "II"
    assert resultado.tributos.ipi > 0


def test_aliquota_efetiva_dentro_da_faixa() -> None:
    dados = _dados_base(receita_bruta=Decimal("100000"), receita_12m=Decimal("1000000"))
    resultado = CalculadoraSimples().apurar(dados)
    aliq = resultado.aliquota_efetiva
    assert Decimal("0") < aliq < Decimal("0.20")


def test_total_igual_soma_tributos() -> None:
    dados = _dados_base()
    resultado = CalculadoraSimples().apurar(dados)
    soma = (
        resultado.tributos.irpj + resultado.tributos.csll
        + resultado.tributos.cofins + resultado.tributos.pis
        + resultado.tributos.inss_cpp + resultado.tributos.icms
        + resultado.tributos.ipi + resultado.tributos.iss
    )
    assert abs(soma - resultado.tributos.total) < Decimal("0.01")
