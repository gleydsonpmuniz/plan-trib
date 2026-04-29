from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.deps import get_current_user, get_db
from src.models.empresa import Empresa
from src.models.usuario import Usuario
from src.schemas.empresa import EmpresaCreate, EmpresaResponse
from src.services.audit_service import audit

router = APIRouter(prefix="/empresas", tags=["empresas"])


@router.get("", response_model=list[EmpresaResponse])
async def listar(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
    grupo_id: int | None = None,
) -> list[Empresa]:
    stmt = select(Empresa).where(Empresa.deleted_at.is_(None))
    if grupo_id:
        stmt = stmt.where(Empresa.grupo_id == grupo_id)
    result = await db.execute(stmt.order_by(Empresa.razao_social))
    return list(result.scalars().all())


@router.post("", response_model=EmpresaResponse, status_code=201)
async def criar(
    payload: EmpresaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[Usuario, Depends(get_current_user)],
) -> Empresa:
    empresa = Empresa(**payload.model_dump())
    db.add(empresa)
    try:
        await db.flush()
    except Exception as e:
        raise HTTPException(409, f"CNPJ duplicado ou inválido: {e}") from e
    await audit(db, user.id, "create", "empresa", empresa.id)
    await db.commit()
    await db.refresh(empresa)
    return empresa
