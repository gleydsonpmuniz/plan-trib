from pydantic import BaseModel


class GrupoCreate(BaseModel):
    nome: str
    descricao: str | None = None


class GrupoResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None

    model_config = {"from_attributes": True}
