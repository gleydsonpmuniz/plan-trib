from pathlib import Path

from src.parsers.sped_contribuicoes.parser import parse_efd_contribuicoes


def test_parsing_returns_valid_object(sample_sped_contrib: Path) -> None:
    result = parse_efd_contribuicoes(sample_sped_contrib)
    assert result.cnpj_titular
    assert len(result.cnpj_titular) == 14
    assert result.regime in {"cumulativo", "nao_cumulativo", "misto"}


def test_estabelecimentos_loaded(sample_sped_contrib: Path) -> None:
    result = parse_efd_contribuicoes(sample_sped_contrib)
    if result.estabelecimentos:
        assert all(len(e.cnpj) == 14 for e in result.estabelecimentos)


def test_apuracao_pis_cofins_present(sample_sped_contrib: Path) -> None:
    result = parse_efd_contribuicoes(sample_sped_contrib)
    assert result.apuracao_pis.valor_devido >= 0
    assert result.apuracao_cofins.valor_devido >= 0
