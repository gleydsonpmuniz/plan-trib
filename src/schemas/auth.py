from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class UsuarioResponse(BaseModel):
    id: int
    email: str
    nome: str
    is_admin: bool

    model_config = {"from_attributes": True}
