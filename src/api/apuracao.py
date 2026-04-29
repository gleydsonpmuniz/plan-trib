from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.deps import get_current_user, get_db
from src.engine import comparar_regimes
from src.models.empresa import Empresa
from src.models.periodo import Periodo
from src.models.usuario import Usuario
from src.schemas.apuracao import (
    ApuracaoRequest,
    ComparativoMensal,
    ComparativoResponse,
    ResultadoOut,
    TributosOut,
)
from src.services.audit_service import audit
from src.services.comparador_service import montar_dados_competencia

router = APIRouter(prefix="/apuracao", tags=["apuracao"])


def _to_resultado_out(r) -> ResultadoOut:  # type: ignore[no-untyped-def]
    return ResultadoOut(
        regime=r.regime,
        competencia=r.competencia,
        tributos=TributosOut(
            irpj=r.tributos.irpj, csll=r.tributos.csll,
            pis=r.tributos.pis, cofins=r.tributos.cofins,
            inss_cpp=r.tributos.inss_cpp, icms=r.tributos.icms,
            ipi=r.tributos.ipi, iss=r.tributos.iss,
            total=r.tributos.total,
        ),
        receita_base=r.receita_base,
        aliquota_efetiva=r.aliquota_efetiva,
        detalhamento=r.detalhamento,
    )


def _meses_no_intervalo(inicio: date, fim: date) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    a, m = inicio.year, inicio.month
    while (a, m) <= (fim.year, fim.month):
        out.append((a, m))
        m += 1
        if m > 12:
            m = 1
            a += 1
    return out


@router.post("/calcular", response_model=ComparativoResponse)
async def calcular(
    payload: ApuracaoRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[Usuario, Depends(get_current_user)],
) -> ComparativoResponse:
    empresa = (await db.execute(
        select(Empresa).where(Empresa.id == payload.empresa_id, Empresa.deleted_at.is_(None))
    )).scalar_one_or_none()
    if not empresa:
        raise HTTPException(404, "Empresa não encontrada")

    meses_alvo = _meses_no_intervalo(payload.periodo_de, payload.periodo_ate)
    resultados_mensais: list[ComparativoMensal] = []
    total_simples = total_lp = total_lr = Decimal(0)

    for ano, mes in meses_alvo:
        periodo = (await db.execute(
            select(Periodo).where(
                Periodo.empresa_id == empresa.id, Periodo.ano == ano, Periodo.mes == mes
            )
        )).scalar_one_or_none()
        if not periodo:
            continue
        dados = await montar_dados_competencia(db, empresa, periodo)
        regimes = comparar_regimes(dados)

        total_simples += regimes["SIMPLES"].tributos.total
        total_lp += regimes["LP"].tributos.total
        total_lr += regimes["LR"].tributos.total

        recomendado = min(regimes.items(), key=lambda kv: kv[1].tributos.total)[0]
        resultados_mensais.append(
            ComparativoMensal(
                competencia=date(ano, mes, 1),
                simples=_to_resultado_out(regimes["SIMPLES"]),
                lp=_to_resultado_out(regimes["LP"]),
                lr=_to_resultado_out(regimes["LR"]),
                regime_recomendado=recomendado,
            )
        )

    totais = {"SIMPLES": total_simples, "LP": total_lp, "LR": total_lr}
    recomendacao_periodo = min(totais, key=lambda k: totais[k])

    await audit(db, user.id, "calcular", "apuracao", empresa.id, {"meses": len(meses_alvo)})
    await db.commit()

    return ComparativoResponse(
        empresa_id=empresa.id,
        cnpj=empresa.cnpj,
        razao_social=empresa.razao_social,
        meses=resultados_mensais,
        total_simples=total_simples,
        total_lp=total_lp,
        total_lr=total_lr,
        recomendacao_periodo=recomendacao_periodo,
    )
