from pathlib import Path

import pytest

from src.parsers.sped_fiscal.parser import parse_efd_icms_ipi


def test_parsing_returns_valid_object(sample_sped_fiscal: Path) -> None:
    result = parse_efd_icms_ipi(sample_sped_fiscal)
    assert result.cnpj
    assert len(result.cnpj) == 14
    assert result.cod_ver in {"016", "017", "018", "019"}
    assert result.dt_ini.year >= 2024


def test_apuracao_icms_present(sample_sped_fiscal: Path) -> None:
    result = parse_efd_icms_ipi(sample_sped_fiscal)
    apur = result.apuracao_icms
    assert apur.debito_total >= 0
    assert apur.credito_total >= 0


def test_unsupported_layout_raises(tmp_path: Path) -> None:
    fake = tmp_path / "fake.txt"
    fake.write_text("|0000|999|0|01012025|31012025|FAKE|12345678000100||SP|123||0|||A|1|\n",
                    encoding="iso-8859-1")
    from src.parsers.base import UnsupportedLayoutError
    with pytest.raises(UnsupportedLayoutError):
        parse_efd_icms_ipi(fake)
