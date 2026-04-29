from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_log import AuditLog


async def audit(
    db: AsyncSession,
    usuario_id: int | None,
    acao: str,
    recurso: str,
    recurso_id: int | None = None,
    metadados: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            usuario_id=usuario_id,
            acao=acao,
            recurso=recurso,
            recurso_id=recurso_id,
            metadados=metadados or {},
        )
    )
