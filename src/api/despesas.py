from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.deps import get_current_user, get_db
from src.models.despesa import DespesaSintetica
from src.models.empresa import Empresa
from src.models.periodo import Periodo
from src.models.usuario import Usuario
from src.schemas.despesa import DespesaInput, DespesaResponse, ReplicarDespesa
from src.services.audit_service import audit

router = APIRouter(prefix="/despesas", tags=["despesas"])


async def _get_or_create_periodo(
    db: AsyncSession, empresa_id: int, ano: int, mes: int
) -> Periodo:
    periodo = (await db.execute(
        select(Periodo).where(
            Periodo.empresa_id == empresa_id, Periodo.ano == ano, Periodo.mes == mes
        )
    )).scalar_one_or_none()
    if not periodo:
        periodo = Periodo(empresa_id=empresa_id, ano=ano, mes=mes)
        db.add(periodo)
        await db.flush()
    return periodo


async def _upsert_despesa(
    db: AsyncSession, periodo_id: int, adm: float, com: float, trib: float
) -> DespesaSintetica:
    desp = (await db.execute(
        select(DespesaSintetica).where(DespesaSintetica.periodo_id == periodo_id)
    )).scalar_one_or_none()
    if desp:
        desp.despesas_administrativas = adm  # type: ignore[assignment]
        desp.despesas_comerciais = com  # type: ignore[assignment]
        desp.despesas_tributarias = trib  # type: ignore[assignment]
    else:
        desp = DespesaSintetica(
            periodo_id=periodo_id,
            despesas_administrativas=adm,  # type: ignore[arg-type]
            despesas_comerciais=com,  # type: ignore[arg-type]
            despesas_tributarias=trib,  # type: ignore[arg-type]
        )
        db.add(desp)
    return desp


@router.put("", response_model=DespesaResponse)
async def upsert(
    payload: DespesaInput,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[Usuario, Depends(get_current_user)],
) -> DespesaSintetica:
    empresa = (await db.execute(
        select(Empresa).where(Empresa.id == payload.empresa_id)
    )).scalar_one_or_none()
    if not empresa:
        raise HTTPException(404, "Empresa não encontrada")
    periodo = await _get_or_create_periodo(db, payload.empresa_id, payload.ano, payload.mes)
    desp = await _upsert_despesa(
        db, periodo.id,
        payload.despesas_administrativas,  # type: ignore[arg-type]
        payload.despesas_comerciais,  # type: ignore[arg-type]
        payload.despesas_tributarias,  # type: ignore[arg-type]
    )
    await db.flush()
    await audit(db, user.id, "upsert", "despesa", desp.id)
    await db.commit()
    await db.refresh(desp)
    return desp


@router.post("/replicar", response_model=list[DespesaResponse])
async def replicar(
    payload: ReplicarDespesa,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[Usuario, Depends(get_current_user)],
) -> list[DespesaSintetica]:
    """Replica os valores informados para todos os 12 meses do ano informado."""
    out: list[DespesaSintetica] = []
    for mes in range(1, 13):
        periodo = await _get_or_create_periodo(db, payload.empresa_id, payload.ano, mes)
        desp = await _upsert_despesa(
            db, periodo.id,
            payload.despesas_administrativas,  # type: ignore[arg-type]
            payload.despesas_comerciais,  # type: ignore[arg-type]
            payload.despesas_tributarias,  # type: ignore[arg-type]
        )
        out.append(desp)
    await db.flush()
    await audit(db, user.id, "replicar", "despesa", payload.empresa_id, {"ano": payload.ano})
    await db.commit()
    return out
