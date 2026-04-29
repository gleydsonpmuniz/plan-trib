from pydantic import BaseModel, Field, field_validator

from src.models.empresa import RegimeTributario, TipoEmpresa


class EmpresaCreate(BaseModel):
    cnpj: str = Field(..., min_length=14, max_length=14)
    razao_social: str
    grupo_id: int
    tipo: TipoEmpresa
    regime_atual: RegimeTributario
    atividade_principal: str | None = None
    uf: str = Field(..., min_length=2, max_length=2)
    municipio_ibge: str | None = None

    @field_validator("cnpj")
    @classmethod
    def cnpj_apenas_digitos(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("CNPJ deve conter apenas dígitos (sem máscara)")
        return v


class EmpresaResponse(BaseModel):
    id: int
    cnpj: str
    razao_social: str
    grupo_id: int
    tipo: TipoEmpresa
    regime_atual: RegimeTributario
    uf: str

    model_config = {"from_attributes": True}
