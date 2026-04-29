from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.deps import get_current_user, get_db
from src.models.usuario import Usuario
from src.schemas.auth import LoginRequest, UsuarioResponse
from src.services.audit_service import audit
from src.services.auth_service import (
    decodificar_token,
    emitir_access_token,
    emitir_refresh_token,
    verificar_senha,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_cookies(response: Response, access: str, refresh: str) -> None:
    response.set_cookie(
        "access_token", access, httponly=True, secure=True, samesite="lax",
        max_age=settings.jwt_access_ttl_minutes * 60,
    )
    response.set_cookie(
        "refresh_token", refresh, httponly=True, secure=True, samesite="lax",
        max_age=settings.jwt_refresh_ttl_days * 86400, path="/api/auth",
    )


@router.post("/login", response_model=UsuarioResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Usuario:
    result = await db.execute(
        select(Usuario).where(Usuario.email == payload.email, Usuario.is_ativo)
    )
    usuario = result.scalar_one_or_none()
    if not usuario or not verificar_senha(payload.senha, usuario.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciais inválidas")

    access = emitir_access_token(usuario.id)
    refresh = emitir_refresh_token(usuario.id)
    _set_cookies(response, access, refresh)

    await audit(db, usuario.id, "login", "auth", usuario.id)
    await db.commit()
    return usuario


@router.post("/refresh")
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
) -> dict:
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh ausente")
    try:
        payload = decodificar_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Tipo de token inválido")
        usuario_id = int(payload["sub"])
    except (ValueError, KeyError) as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e
    access = emitir_access_token(usuario_id)
    new_refresh = emitir_refresh_token(usuario_id)
    _set_cookies(response, access, new_refresh)
    return {"ok": True}


@router.post("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/api/auth")
    return {"ok": True}


@router.get("/me", response_model=UsuarioResponse)
async def me(usuario: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
    return usuario
