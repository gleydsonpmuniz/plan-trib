from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ApuracaoRequest(BaseModel):
    empresa_id: int
    periodo_de: date  # primeiro dia do mês inicial
    periodo_ate: date  # primeiro dia do mês final


class TributosOut(BaseModel):
    irpj: Decimal
    csll: Decimal
    pis: Decimal
    cofins: Decimal
    inss_cpp: Decimal
    icms: Decimal
    ipi: Decimal
    iss: Decimal
    total: Decimal


class ResultadoOut(BaseModel):
    regime: str
    competencia: date
    tributos: TributosOut
    receita_base: Decimal
    aliquota_efetiva: Decimal
    detalhamento: dict


class ComparativoMensal(BaseModel):
    competencia: date
    simples: ResultadoOut
    lp: ResultadoOut
    lr: ResultadoOut
    regime_recomendado: str


class ComparativoResponse(BaseModel):
    empresa_id: int
    cnpj: str
    razao_social: str
    meses: list[ComparativoMensal]
    total_simples: Decimal
    total_lp: Decimal
    total_lr: Decimal
    recomendacao_periodo: str
