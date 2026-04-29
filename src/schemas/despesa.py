from decimal import Decimal

from pydantic import BaseModel


class DespesaInput(BaseModel):
    empresa_id: int
    ano: int
    mes: int
    despesas_administrativas: Decimal = Decimal(0)
    despesas_comerciais: Decimal = Decimal(0)
    despesas_tributarias: Decimal = Decimal(0)


class ReplicarDespesa(BaseModel):
    empresa_id: int
    ano: int
    mes_origem: int
    despesas_administrativas: Decimal
    despesas_comerciais: Decimal
    despesas_tributarias: Decimal


class DespesaResponse(BaseModel):
    id: int
    periodo_id: int
    despesas_administrativas: Decimal
    despesas_comerciais: Decimal
    despesas_tributarias: Decimal

    model_config = {"from_attributes": True}
