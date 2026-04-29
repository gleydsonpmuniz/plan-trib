from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from src.parsers.base import UnsupportedLayoutError, stream_lines
from src.utils.decimal_utils import parse_brl_decimal, parse_sped_date

SUPPORTED_VERSIONS = {"004", "005", "006"}


class Estabelecimento(BaseModel):
    cnpj: str
    nome: str
    uf: str | None = None


class ApuracaoContribuicao(BaseModel):
    base: Decimal = Decimal(0)
    aliquota: Decimal = Decimal(0)
    valor_devido: Decimal = Decimal(0)


class ParsedSpedContrib(BaseModel):
    cnpj_titular: str
    cod_ver: str
    dt_ini: date
    dt_fin: date
    razao_social: str
    regime: Literal["cumulativo", "nao_cumulativo", "misto"]
    estabelecimentos: list[Estabelecimento] = Field(default_factory=list)
    receita_bruta_total: Decimal = Decimal(0)
    base_credito_pis_cofins: Decimal = Decimal(0)
    apuracao_pis: ApuracaoContribuicao = Field(default_factory=ApuracaoContribuicao)
    apuracao_cofins: ApuracaoContribuicao = Field(default_factory=ApuracaoContribuicao)


_REGIME_MAP = {"1": "nao_cumulativo", "2": "cumulativo", "3": "misto"}


def parse_efd_contribuicoes(path: Path) -> ParsedSpedContrib:
    cnpj = razao_social = cod_ver = ""
    dt_ini = dt_fin = date(1970, 1, 1)
    regime: Literal["cumulativo", "nao_cumulativo", "misto"] = "cumulativo"
    estabelecimentos: list[Estabelecimento] = []
    receita_total = Decimal(0)
    apuracao_pis = ApuracaoContribuicao()
    apuracao_cofins = ApuracaoContribuicao()

    for parts in stream_lines(path):
        reg = parts[0]
        if reg == "0000":
            cod_ver = parts[1]
            if cod_ver not in SUPPORTED_VERSIONS:
                raise UnsupportedLayoutError(
                    f"EFD-Contribuições versão '{cod_ver}' não suportada. "
                    f"Suportadas: {sorted(SUPPORTED_VERSIONS)}"
                )
            dt_ini = parse_sped_date(parts[5])
            dt_fin = parse_sped_date(parts[6])
            razao_social = parts[7]
            cnpj = parts[8]
        elif reg == "0110":
            cod = parts[1] if len(parts) > 1 else "2"
            regime = _REGIME_MAP.get(cod, "cumulativo")  # type: ignore[assignment]
        elif reg == "0140":
            estabelecimentos.append(
                Estabelecimento(
                    cnpj=parts[3] if len(parts) > 3 else "",
                    nome=parts[2] if len(parts) > 2 else "",
                    uf=parts[4] if len(parts) > 4 else None,
                )
            )
        elif reg == "F550":
            valor = parse_brl_decimal(parts[1]) or Decimal(0)
            receita_total += valor
        elif reg == "M210":
            base = parse_brl_decimal(parts[6]) or Decimal(0)
            aliq = parse_brl_decimal(parts[7]) or Decimal(0)
            valor = parse_brl_decimal(parts[10]) or Decimal(0)
            apuracao_pis.base += base
            apuracao_pis.aliquota = aliq
            apuracao_pis.valor_devido += valor
        elif reg == "M610":
            base = parse_brl_decimal(parts[6]) or Decimal(0)
            aliq = parse_brl_decimal(parts[7]) or Decimal(0)
            valor = parse_brl_decimal(parts[10]) or Decimal(0)
            apuracao_cofins.base += base
            apuracao_cofins.aliquota = aliq
            apuracao_cofins.valor_devido += valor

    return ParsedSpedContrib(
        cnpj_titular=cnpj,
        cod_ver=cod_ver,
        dt_ini=dt_ini,
        dt_fin=dt_fin,
        razao_social=razao_social,
        regime=regime,
        estabelecimentos=estabelecimentos,
        receita_bruta_total=receita_total,
        apuracao_pis=apuracao_pis,
        apuracao_cofins=apuracao_cofins,
    )
