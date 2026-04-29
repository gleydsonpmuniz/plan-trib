from datetime import date
from decimal import Decimal

from src.engine import CalculadoraLucroReal
from src.engine.inputs import DadosFiscaisCompetencia


def test_lr_lucro_positivo_paga_irpj() -> None:
    dados = DadosFiscaisCompetencia(
        cnpj="12345678000100",
        competencia=date(2025, 6, 1),
        uf="ES",
        receita_bruta=Decimal("100000"),
        folha_bruta=Decimal("10000"),
        despesas_administrativas=Decimal("5000"),
    )
    r = CalculadoraLucroReal().apurar(dados)
    assert r.regime == "LR"
    assert r.tributos.irpj > 0
    assert r.tributos.csll > 0


def test_lr_prejuizo_zero_irpj() -> None:
    dados = DadosFiscaisCompetencia(
        cnpj="12345678000100",
        competencia=date(2025, 6, 1),
        uf="ES",
        receita_bruta=Decimal("100000"),
        folha_bruta=Decimal("80000"),
        despesas_administrativas=Decimal("50000"),
    )
    r = CalculadoraLucroReal().apurar(dados)
    assert r.tributos.irpj == 0
    assert r.tributos.csll == 0


def test_lr_aliquota_pis_cofins_nao_cumulativa() -> None:
    dados = DadosFiscaisCompetencia(
        cnpj="12345678000100",
        competencia=date(2025, 6, 1),
        uf="ES",
        receita_bruta=Decimal("100000"),
        base_credito_pis_cofins=Decimal(0),
    )
    r = CalculadoraLucroReal().apurar(dados)
    assert r.tributos.pis == Decimal("100000") * Decimal("0.0165")
    assert r.tributos.cofins == Decimal("100000") * Decimal("0.076")
