import hashlib
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.deps import get_current_user, get_db
from src.models.documento import Documento, StatusDocumento, TipoDocumento
from src.models.empresa import Empresa
from src.models.usuario import Usuario
from src.services.audit_service import audit
from src.services.ingestao_service import processar_documento

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload(
    background: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[Usuario, Depends(get_current_user)],
    empresa_id: Annotated[int, Form(...)],
    tipo: Annotated[TipoDocumento, Form(...)],
    arquivo: UploadFile = File(...),
) -> dict:
    empresa = (await db.execute(
        select(Empresa).where(Empresa.id == empresa_id)
    )).scalar_one_or_none()
    if not empresa:
        raise HTTPException(404, "Empresa não encontrada")

    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    dest = settings.uploads_dir / f"{empresa.cnpj}_{arquivo.filename}"
    sha = hashlib.sha256()
    size = 0
    with dest.open("wb") as fout:
        while True:
            chunk = await arquivo.read(64 * 1024)
            if not chunk:
                break
            fout.write(chunk)
            sha.update(chunk)
            size += len(chunk)
            if size > settings.max_upload_size_mb * 1024 * 1024:
                dest.unlink(missing_ok=True)
                raise HTTPException(413, "Arquivo excede o limite")

    documento = Documento(
        empresa_id=empresa_id,
        tipo=tipo,
        nome_original=arquivo.filename or "sem_nome",
        caminho_storage=str(dest),
        tamanho_bytes=size,
        sha256=sha.hexdigest(),
        status=StatusDocumento.PENDENTE,
    )
    db.add(documento)
    await db.flush()
    await audit(db, user.id, "upload", "documento", documento.id, {"tipo": tipo})
    await db.commit()

    background.add_task(processar_documento, documento.id)
    return {"id": documento.id, "status": documento.status, "sha256": documento.sha256}


@router.get("/empresa/{empresa_id}")
async def listar_da_empresa(
    empresa_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
) -> list[dict]:
    rows = (await db.execute(
        select(Documento).where(
            Documento.empresa_id == empresa_id, Documento.deleted_at.is_(None)
        ).order_by(Documento.created_at.desc())
    )).scalars().all()
    return [
        {"id": d.id, "tipo": d.tipo, "nome_original": d.nome_original,
         "status": d.status, "tamanho_bytes": d.tamanho_bytes,
         "criado_em": d.created_at.isoformat()}
        for d in rows
    ]
