from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import SessionLocal
from src.models.usuario import Usuario
from src.services.auth_service import decodificar_token


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: str | None = Cookie(default=None),
) -> Usuario:
    if not access_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Não autenticado")
    try:
        payload = decodificar_token(access_token)
        if payload.get("type") != "access":
            raise ValueError("Tipo de token inválido")
        usuario_id = int(payload["sub"])
    except (ValueError, KeyError) as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e

    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id, Usuario.is_ativo))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário inválido")
    return usuario
