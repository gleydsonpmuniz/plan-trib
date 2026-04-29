from datetime import date
from pathlib import Path

from sqlalchemy import select

from src.db import SessionLocal
from src.models.credito import CreditoICMS, CreditoPISCOFINS
from src.models.documento import Documento, StatusDocumento, TipoDocumento
from src.models.empresa import Empresa
from src.models.faturamento import FaturamentoMensal
from src.models.folha import FolhaMensal
from src.models.periodo import Periodo
from src.models.pgdas import PgdasDeclaracao


async def _get_or_create_periodo(db, empresa_id: int, dt: date) -> Periodo:  # type: ignore[no-untyped-def]
    p = (await db.execute(
        select(Periodo).where(
            Periodo.empresa_id == empresa_id, Periodo.ano == dt.year, Periodo.mes == dt.month
        )
    )).scalar_one_or_none()
    if not p:
        p = Periodo(empresa_id=empresa_id, ano=dt.year, mes=dt.month)
        db.add(p)
        await db.flush()
    return p


async def processar_documento(documento_id: int) -> None:
    """Processa documento (parser SPED ou extractor LLM) e persiste dados normalizados.

    Roda em BackgroundTask. Marca status PROCESSADO ou ERRO.
    """
    async with SessionLocal() as db:
        doc = (await db.execute(
            select(Documento).where(Documento.id == documento_id)
        )).scalar_one_or_none()
        if not doc:
            return
        empresa = (await db.execute(
            select(Empresa).where(Empresa.id == doc.empresa_id)
        )).scalar_one_or_none()
        if not empresa:
            doc.status = StatusDocumento.ERRO
            doc.erro_msg = "Empresa não encontrada"
            await db.commit()
            return

        doc.status = StatusDocumento.PROCESSANDO
        await db.commit()

        try:
            path = Path(doc.caminho_storage)
            if doc.tipo == TipoDocumento.SPED_FISCAL:
                await _processar_sped_fiscal(db, empresa, path)
            elif doc.tipo == TipoDocumento.SPED_CONTRIBUICOES:
                await _processar_sped_contrib(db, empresa, path)
            elif doc.tipo == TipoDocumento.PDF_FOLHA:
                await _processar_folha(db, empresa, path)
            elif doc.tipo == TipoDocumento.PDF_PGDAS:
                await _processar_pgdas(db, empresa, path)

            doc.status = StatusDocumento.PROCESSADO
            doc.erro_msg = None
        except Exception as e:
            doc.status = StatusDocumento.ERRO
            doc.erro_msg = str(e)[:1000]
        await db.commit()


async def _processar_sped_fiscal(db, empresa, path):  # type: ignore[no-untyped-def]
    from src.parsers.sped_fiscal.parser import parse_efd_icms_ipi

    parsed = parse_efd_icms_ipi(path)
    periodo = await _get_or_create_periodo(db, empresa.id, parsed.dt_ini)

    await db.execute(
        FaturamentoMensal.__table__.delete().where(FaturamentoMensal.periodo_id == periodo.id)
    )
    for row in parsed.faturamento_por_cfop:
        db.add(FaturamentoMensal(
            periodo_id=periodo.id, cfop=row.cfop, cst=row.cst,
            valor_operacao=row.valor_operacao, base_icms=row.base_icms,
            valor_icms=row.valor_icms, valor_ipi=row.valor_ipi,
        ))

    icms = (await db.execute(
        select(CreditoICMS).where(CreditoICMS.periodo_id == periodo.id)
    )).scalar_one_or_none()
    if not icms:
        icms = CreditoICMS(periodo_id=periodo.id)
        db.add(icms)
    icms.debito_total = parsed.apuracao_icms.debito_total  # type: ignore[assignment]
    icms.credito_total = parsed.apuracao_icms.credito_total  # type: ignore[assignment]
    icms.saldo_devedor = parsed.apuracao_icms.saldo_devedor  # type: ignore[assignment]
    icms.saldo_credor = parsed.apuracao_icms.saldo_credor  # type: ignore[assignment]


async def _processar_sped_contrib(db, empresa, path):  # type: ignore[no-untyped-def]
    from src.parsers.sped_contribuicoes.parser import parse_efd_contribuicoes

    parsed = parse_efd_contribuicoes(path)
    periodo = await _get_or_create_periodo(db, empresa.id, parsed.dt_ini)

    pc = (await db.execute(
        select(CreditoPISCOFINS).where(CreditoPISCOFINS.periodo_id == periodo.id)
    )).scalar_one_or_none()
    if not pc:
        pc = CreditoPISCOFINS(periodo_id=periodo.id)
        db.add(pc)
    pc.valor_pis = parsed.apuracao_pis.valor_devido  # type: ignore[assignment]
    pc.valor_cofins = parsed.apuracao_cofins.valor_devido  # type: ignore[assignment]
    pc.base_credito = parsed.apuracao_pis.base  # type: ignore[assignment]


async def _processar_folha(db, empresa, path):  # type: ignore[no-untyped-def]
    from src.extractors.folha_extractor import extract_folha

    folha = await extract_folha(path)
    periodo = await _get_or_create_periodo(db, empresa.id, folha.competencia)
    f = (await db.execute(
        select(FolhaMensal).where(FolhaMensal.periodo_id == periodo.id)
    )).scalar_one_or_none()
    if not f:
        f = FolhaMensal(periodo_id=periodo.id)
        db.add(f)
    f.salario_contribuicao_empregados = folha.salario_contribuicao_empregados  # type: ignore[assignment]
    f.base_total_inss = folha.base_total_inss  # type: ignore[assignment]
    f.inss_segurados = folha.inss_segurados  # type: ignore[assignment]
    f.inss_empresa = folha.inss_empresa  # type: ignore[assignment]
    f.inss_rat = folha.inss_rat  # type: ignore[assignment]
    f.inss_terceiros = folha.inss_terceiros  # type: ignore[assignment]
    f.inss_total = folha.inss_total  # type: ignore[assignment]
    f.base_fgts = folha.base_fgts  # type: ignore[assignment]
    f.valor_fgts = folha.valor_fgts  # type: ignore[assignment]
    f.base_irrf_mensal = folha.base_irrf_mensal  # type: ignore[assignment]
    f.valor_irrf_mensal = folha.valor_irrf_mensal  # type: ignore[assignment]
    f.folha_bruta = folha.folha_bruta  # type: ignore[assignment]
    f.pro_labore = folha.pro_labore  # type: ignore[assignment]
    f.qtd_empregados = folha.qtd_empregados  # type: ignore[assignment]


async def _processar_pgdas(db, empresa, path):  # type: ignore[no-untyped-def]
    from src.extractors.pgdas_extractor import extract_pgdas

    pgd = await extract_pgdas(path)
    periodo = await _get_or_create_periodo(db, empresa.id, pgd.periodo_apuracao)

    p = (await db.execute(
        select(PgdasDeclaracao).where(PgdasDeclaracao.periodo_id == periodo.id)
    )).scalar_one_or_none()
    if not p:
        p = PgdasDeclaracao(periodo_id=periodo.id)
        db.add(p)
    p.rpa = pgd.rpa  # type: ignore[assignment]
    p.rbt12 = pgd.rbt12  # type: ignore[assignment]
    p.rba = pgd.rba  # type: ignore[assignment]
    p.rbaa = pgd.rbaa  # type: ignore[assignment]
    p.fator_r = pgd.fator_r  # type: ignore[assignment]

    if pgd.estabelecimentos:
        primeiro = pgd.estabelecimentos[0]
        p.anexo_inferido = primeiro.anexo_inferido  # type: ignore[assignment]
        p.atividade_descricao = primeiro.descricao  # type: ignore[assignment]
        p.irpj = primeiro.irpj  # type: ignore[assignment]
        p.csll = primeiro.csll  # type: ignore[assignment]
        p.cofins = primeiro.cofins  # type: ignore[assignment]
        p.pis = primeiro.pis  # type: ignore[assignment]
        p.inss_cpp = primeiro.inss_cpp  # type: ignore[assignment]
        p.icms = primeiro.icms  # type: ignore[assignment]
        p.ipi = primeiro.ipi  # type: ignore[assignment]
        p.iss = primeiro.iss  # type: ignore[assignment]
        p.total_das = primeiro.total  # type: ignore[assignment]
    p.receitas_14m = {k: str(v) for k, v in pgd.receitas_anteriores_mercado_interno.items()}  # type: ignore[assignment]
