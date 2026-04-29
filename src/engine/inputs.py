from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DadosFiscaisCompetencia(BaseModel):
    model_config = ConfigDict(frozen=False)

    cnpj: str
    competencia: date
    uf: str

    receita_bruta: Decimal = Decimal(0)
    receita_servicos: Decimal = Decimal(0)
    receita_revenda: Decimal = Decimal(0)
    receita_industrializacao: Decimal = Decimal(0)

    base_credito_pis_cofins: Decimal = Decimal(0)

    debito_icms: Decimal = Decimal(0)
    credito_icms: Decimal = Decimal(0)

    folha_bruta: Decimal = Decimal(0)
    pro_labore: Decimal = Decimal(0)
    inss_patronal_total: Decimal = Decimal(0)
    fgts: Decimal = Decimal(0)

    despesas_administrativas: Decimal = Decimal(0)
    despesas_comerciais: Decimal = Decimal(0)
    despesas_tributarias: Decimal = Decimal(0)

    receita_12m: Decimal = Decimal(0)
    folha_12m: Decimal = Decimal(0)
    pro_labore_12m: Decimal = Decimal(0)

    atividade_descricao: str | None = None
    cfops_uso: list[str] = Field(default_factory=list)
