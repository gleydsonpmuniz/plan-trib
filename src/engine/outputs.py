from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


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
        return (
            self.irpj
            + self.csll
            + self.pis
            + self.cofins
            + self.inss_cpp
            + self.icms
            + self.ipi
            + self.iss
        )


class ResultadoApuracao(BaseModel):
    regime: Literal["SIMPLES", "LP", "LR"]
    competencia: date
    cnpj: str
    tributos: Tributos
    receita_base: Decimal
    aliquota_efetiva: Decimal = Decimal(0)
    detalhamento: dict = Field(default_factory=dict)
