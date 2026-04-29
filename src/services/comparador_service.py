from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.engine import comparar_regimes
from src.engine.inputs import DadosFiscaisCompetencia
from src.models.apuracao import Apuracao
from src.models.credito import CreditoICMS, CreditoPISCOFINS
from src.models.despesa import DespesaSintetica
from src.models.empresa import Empresa, RegimeTributario
from src.models.faturamento import FaturamentoMensal
from src.models.folha import FolhaMensal
from src.models.periodo import Periodo


async def montar_dados_competencia(
    db: AsyncSession, empresa: Empresa, periodo: Periodo
) -> DadosFiscaisCompetencia:
    """Lê todas as fontes (faturamento, créditos, folha, despesas) e monta o input do engine."""
    fat_total = Decimal(0)
    fat_revenda = Decimal(0)
    fat_industr = Decimal(0)
    fat_servicos = Decimal(0)
    cfops: list[str] = []

    rows = (await db.execute(
        select(FaturamentoMensal).where(FaturamentoMensal.periodo_id == periodo.id)
    )).scalars().all()
    for row in rows:
        fat_total += row.valor_operacao
        cfops.append(row.cfop)
        if row.cfop.startswith(("51", "61")):
            fat_revenda += row.valor_operacao
        if row.cfop.startswith(("5101", "6101", "5102", "6102", "5108", "6108")):
            fat_industr += row.valor_operacao  # usado por indústria também
        if row.cfop.startswith(("59", "69")):
            fat_servicos += row.valor_operacao

    cred_pc = (await db.execute(
        select(CreditoPISCOFINS).where(CreditoPISCOFINS.periodo_id == periodo.id)
    )).scalar_one_or_none()
    cred_icms = (await db.execute(
        select(CreditoICMS).where(CreditoICMS.periodo_id == periodo.id)
    )).scalar_one_or_none()
    folha = (await db.execute(
        select(FolhaMensal).where(FolhaMensal.periodo_id == periodo.id)
    )).scalar_one_or_none()
    desp = (await db.execute(
        select(DespesaSintetica).where(DespesaSintetica.periodo_id == periodo.id)
    )).scalar_one_or_none()

    return DadosFiscaisCompetencia(
        cnpj=empresa.cnpj,
        competencia=date(periodo.ano, periodo.mes, 1),
        uf=empresa.uf,
        receita_bruta=fat_total,
        receita_servicos=fat_servicos,
        receita_revenda=fat_revenda,
        receita_industrializacao=fat_industr,
        base_credito_pis_cofins=cred_pc.base_credito if cred_pc else Decimal(0),
        debito_icms=cred_icms.debito_total if cred_icms else Decimal(0),
        credito_icms=cred_icms.credito_total if cred_icms else Decimal(0),
        folha_bruta=folha.folha_bruta if folha else Decimal(0),
        pro_labore=folha.pro_labore if folha else Decimal(0),
        inss_patronal_total=folha.inss_total if folha else Decimal(0),
        fgts=folha.valor_fgts if folha else Decimal(0),
        despesas_administrativas=desp.despesas_administrativas if desp else Decimal(0),
        despesas_comerciais=desp.despesas_comerciais if desp else Decimal(0),
        despesas_tributarias=desp.despesas_tributarias if desp else Decimal(0),
        atividade_descricao=empresa.atividade_principal,
        cfops_uso=list(set(cfops)),
    )


async def calcular_e_persistir(
    db: AsyncSession, empresa: Empresa, periodo: Periodo
) -> dict[str, Apuracao]:
    """Calcula 3 regimes para um período e persiste como Apuracao registros."""
    dados = await montar_dados_competencia(db, empresa, periodo)
    resultados = comparar_regimes(dados)
    apuracoes: dict[str, Apuracao] = {}
    for regime_key, resultado in resultados.items():
        regime_enum = {
            "SIMPLES": RegimeTributario.SIMPLES,
            "LP": RegimeTributario.LUCRO_PRESUMIDO,
            "LR": RegimeTributario.LUCRO_REAL,
        }[regime_key]
        apuracao = Apuracao(
            periodo_id=periodo.id,
            cenario_id=None,
            regime=regime_enum,
            irpj=resultado.tributos.irpj,
            csll=resultado.tributos.csll,
            pis=resultado.tributos.pis,
            cofins=resultado.tributos.cofins,
            inss_cpp=resultado.tributos.inss_cpp,
            icms=resultado.tributos.icms,
            ipi=resultado.tributos.ipi,
            iss=resultado.tributos.iss,
            total=resultado.tributos.total,
            aliquota_efetiva=resultado.aliquota_efetiva,
            detalhamento=resultado.detalhamento,
        )
        db.add(apuracao)
        apuracoes[regime_key] = apuracao
    await db.flush()
    return apuracoes
