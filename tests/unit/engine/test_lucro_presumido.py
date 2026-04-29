from datetime import date
from decimal import Decimal

from src.engine import CalculadoraLucroPresumido
from src.engine.inputs import DadosFiscaisCompetencia


def test_lp_comercio_aliquota_basica() -> None:
    dados = DadosFiscaisCompetencia(
        cnpj="12345678000100",
        competencia=date(2025, 6, 1),
        uf="ES",
        receita_bruta=Decimal("100000"),
        receita_revenda=Decimal("100000"),
    )
    r = CalculadoraLucroPresumido().apurar(dados)
    assert r.regime == "LP"
    assert r.tributos.pis == Decimal("100000") * Decimal("0.0065")
    assert r.tributos.cofins == Decimal("100000") * Decimal("0.03")


def test_lp_servicos_presuncao_alta() -> None:
    dados = DadosFiscaisCompetencia(
        cnpj="12345678000100",
        competencia=date(2025, 6, 1),
        uf="ES",
        receita_bruta=Decimal("50000"),
        receita_servicos=Decimal("50000"),
    )
    r = CalculadoraLucroPresumido().apurar(dados)
    base_irpj = Decimal("50000") * Decimal("0.32")
    assert r.detalhamento["base_irpj"] == str(base_irpj)
