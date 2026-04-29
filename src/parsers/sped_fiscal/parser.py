from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, Field

from src.parsers.base import UnsupportedLayoutError, stream_lines
from src.utils.decimal_utils import parse_brl_decimal, parse_sped_date

SUPPORTED_VERSIONS = {"016", "017", "018", "019"}


class FaturamentoRow(BaseModel):
    cfop: str
    cst: str | None = None
    valor_operacao: Decimal = Decimal(0)
    base_icms: Decimal = Decimal(0)
    valor_icms: Decimal = Decimal(0)
    valor_ipi: Decimal = Decimal(0)


class ApuracaoIcmsRow(BaseModel):
    debito_total: Decimal = Decimal(0)
    credito_total: Decimal = Decimal(0)
    saldo_devedor: Decimal = Decimal(0)
    saldo_credor: Decimal = Decimal(0)


class ParsedSpedFiscal(BaseModel):
    cnpj: str
    uf: str
    cod_ver: str
    dt_ini: date
    dt_fin: date
    razao_social: str
    ind_ativ: str
    faturamento_por_cfop: list[FaturamentoRow] = Field(default_factory=list)
    apuracao_icms: ApuracaoIcmsRow = Field(default_factory=ApuracaoIcmsRow)


def parse_efd_icms_ipi(path: Path) -> ParsedSpedFiscal:
    cnpj = uf = razao_social = cod_ver = ind_ativ = ""
    dt_ini = dt_fin = date(1970, 1, 1)
    faturamento_acc: dict[tuple[str, str | None], FaturamentoRow] = {}
    apuracao = ApuracaoIcmsRow()

    for parts in stream_lines(path):
        reg = parts[0]
        if reg == "0000":
            cod_ver = parts[1]
            if cod_ver not in SUPPORTED_VERSIONS:
                raise UnsupportedLayoutError(
                    f"EFD ICMS/IPI versão '{cod_ver}' não suportada. "
                    f"Suportadas: {sorted(SUPPORTED_VERSIONS)}"
                )
            dt_ini = parse_sped_date(parts[3])
            dt_fin = parse_sped_date(parts[4])
            razao_social = parts[5]
            cnpj = parts[6] or ""
            uf = parts[8] if len(parts) > 8 else ""
            ind_ativ = parts[14] if len(parts) > 14 else ""
        elif reg == "C190":
            cst = parts[1] if parts[1] else None
            cfop = parts[2]
            valor_op = parse_brl_decimal(parts[4]) or Decimal(0)
            base_icms = parse_brl_decimal(parts[5]) or Decimal(0)
            valor_icms = parse_brl_decimal(parts[6]) or Decimal(0)
            valor_ipi = parse_brl_decimal(parts[8]) if len(parts) > 8 else Decimal(0)
            valor_ipi = valor_ipi or Decimal(0)
            key = (cfop, cst)
            if key in faturamento_acc:
                row = faturamento_acc[key]
                row.valor_operacao += valor_op
                row.base_icms += base_icms
                row.valor_icms += valor_icms
                row.valor_ipi += valor_ipi
            else:
                faturamento_acc[key] = FaturamentoRow(
                    cfop=cfop, cst=cst, valor_operacao=valor_op,
                    base_icms=base_icms, valor_icms=valor_icms, valor_ipi=valor_ipi,
                )
        elif reg == "E110":
            apuracao.debito_total = parse_brl_decimal(parts[1]) or Decimal(0)
            apuracao.credito_total = parse_brl_decimal(parts[5]) or Decimal(0)
            apuracao.saldo_devedor = parse_brl_decimal(parts[10]) or Decimal(0)
            apuracao.saldo_credor = parse_brl_decimal(parts[13]) or Decimal(0)

    return ParsedSpedFiscal(
        cnpj=cnpj, uf=uf, cod_ver=cod_ver,
        dt_ini=dt_ini, dt_fin=dt_fin,
        razao_social=razao_social, ind_ativ=ind_ativ,
        faturamento_por_cfop=list(faturamento_acc.values()),
        apuracao_icms=apuracao,
    )
