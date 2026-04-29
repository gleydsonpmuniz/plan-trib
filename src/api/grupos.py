from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.deps import get_current_user, get_db
from src.models.grupo import Grupo
from src.models.usuario import Usuario
from src.schemas.grupo import GrupoCreate, GrupoResponse
from src.services.audit_service import audit

router = APIRouter(prefix="/grupos", tags=["grupos"])


@router.get("", response_model=list[GrupoResponse])
async def listar(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
) -> list[Grupo]:
    result = await db.execute(select(Grupo).where(Grupo.deleted_at.is_(None)).order_by(Grupo.nome))
    return list(result.scalars().all())


@router.post("", response_model=GrupoResponse, status_code=201)
async def criar(
    payload: GrupoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[Usuario, Depends(get_current_user)],
) -> Grupo:
    grupo = Grupo(**payload.model_dump())
    db.add(grupo)
    await db.flush()
    await audit(db, user.id, "create", "grupo", grupo.id)
    await db.commit()
    await db.refresh(grupo)
    return grupo
