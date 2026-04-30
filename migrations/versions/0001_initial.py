"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("is_admin", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "grupo",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False, index=True),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # create_type=False: criamos explicitamente abaixo (idempotente).
    # O op.create_table referencia esses ENUMs sem tentar recriá-los.
    tipo_emp = postgresql.ENUM("matriz", "filial", "independente", name="tipoempresa", create_type=False)
    regime = postgresql.ENUM("SIMPLES", "LP", "LR", name="regimetributario", create_type=False)
    tipo_emp.create(op.get_bind(), checkfirst=True)
    regime.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "empresa",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cnpj", sa.String(14), unique=True, nullable=False, index=True),
        sa.Column("razao_social", sa.String(255), nullable=False),
        sa.Column("grupo_id", sa.Integer, sa.ForeignKey("grupo.id"), nullable=False, index=True),
        sa.Column("tipo", tipo_emp, nullable=False),
        sa.Column("regime_atual", regime, nullable=False),
        sa.Column("atividade_principal", sa.String(255), nullable=True),
        sa.Column("uf", sa.String(2), nullable=False),
        sa.Column("municipio_ibge", sa.String(7), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "periodo",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("empresa_id", sa.Integer, sa.ForeignKey("empresa.id"), nullable=False, index=True),
        sa.Column("ano", sa.Integer, nullable=False),
        sa.Column("mes", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("empresa_id", "ano", "mes", name="uq_periodo_empresa_competencia"),
    )

    tipo_doc = postgresql.ENUM(
        "SPED_FISCAL", "SPED_CONTRIBUICOES", "PDF_FOLHA", "PDF_PGDAS",
        name="tipodocumento", create_type=False,
    )
    status_doc = postgresql.ENUM(
        "PENDENTE", "PROCESSANDO", "PROCESSADO", "ERRO",
        name="statusdocumento", create_type=False,
    )
    tipo_doc.create(op.get_bind(), checkfirst=True)
    status_doc.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "documento",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("empresa_id", sa.Integer, sa.ForeignKey("empresa.id"), nullable=False, index=True),
        sa.Column("tipo", tipo_doc, nullable=False),
        sa.Column("nome_original", sa.String(500), nullable=False),
        sa.Column("caminho_storage", sa.String(1000), nullable=False),
        sa.Column("tamanho_bytes", sa.BigInteger, nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False, index=True),
        sa.Column("status", status_doc, nullable=False, server_default="PENDENTE"),
        sa.Column("erro_msg", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    NUMERIC = sa.Numeric(18, 6)

    op.create_table(
        "faturamento_mensal",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("periodo_id", sa.Integer, sa.ForeignKey("periodo.id"), nullable=False, index=True),
        sa.Column("cfop", sa.String(4), nullable=False),
        sa.Column("cst", sa.String(3), nullable=True),
        sa.Column("valor_operacao", NUMERIC, nullable=False, server_default="0"),
        sa.Column("base_icms", NUMERIC, nullable=False, server_default="0"),
        sa.Column("valor_icms", NUMERIC, nullable=False, server_default="0"),
        sa.Column("valor_ipi", NUMERIC, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "credito_pis_cofins",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("periodo_id", sa.Integer, sa.ForeignKey("periodo.id"), nullable=False, index=True),
        sa.Column("base_credito", NUMERIC, nullable=False, server_default="0"),
        sa.Column("valor_pis", NUMERIC, nullable=False, server_default="0"),
        sa.Column("valor_cofins", NUMERIC, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "credito_icms",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("periodo_id", sa.Integer, sa.ForeignKey("periodo.id"), nullable=False, index=True),
        sa.Column("debito_total", NUMERIC, nullable=False, server_default="0"),
        sa.Column("credito_total", NUMERIC, nullable=False, server_default="0"),
        sa.Column("saldo_devedor", NUMERIC, nullable=False, server_default="0"),
        sa.Column("saldo_credor", NUMERIC, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "folha_mensal",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("periodo_id", sa.Integer, sa.ForeignKey("periodo.id"), nullable=False, index=True),
        sa.Column("salario_contribuicao_empregados", NUMERIC, nullable=False, server_default="0"),
        sa.Column("base_total_inss", NUMERIC, nullable=False, server_default="0"),
        sa.Column("inss_segurados", NUMERIC, nullable=False, server_default="0"),
        sa.Column("inss_empresa", NUMERIC, nullable=False, server_default="0"),
        sa.Column("inss_rat", NUMERIC, nullable=False, server_default="0"),
        sa.Column("inss_terceiros", NUMERIC, nullable=False, server_default="0"),
        sa.Column("inss_total", NUMERIC, nullable=False, server_default="0"),
        sa.Column("base_fgts", NUMERIC, nullable=False, server_default="0"),
        sa.Column("valor_fgts", NUMERIC, nullable=False, server_default="0"),
        sa.Column("base_irrf_mensal", NUMERIC, nullable=False, server_default="0"),
        sa.Column("valor_irrf_mensal", NUMERIC, nullable=False, server_default="0"),
        sa.Column("pro_labore", NUMERIC, nullable=False, server_default="0"),
        sa.Column("folha_bruta", NUMERIC, nullable=False, server_default="0"),
        sa.Column("qtd_empregados", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("periodo_id", name="uq_folha_periodo"),
    )

    op.create_table(
        "pgdas_declaracao",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("periodo_id", sa.Integer, sa.ForeignKey("periodo.id"), nullable=False, index=True),
        sa.Column("rpa", NUMERIC, nullable=False, server_default="0"),
        sa.Column("rbt12", NUMERIC, nullable=False, server_default="0"),
        sa.Column("rba", NUMERIC, nullable=False, server_default="0"),
        sa.Column("rbaa", NUMERIC, nullable=False, server_default="0"),
        sa.Column("fator_r", NUMERIC, nullable=True),
        sa.Column("anexo_inferido", sa.String(2), nullable=True),
        sa.Column("atividade_descricao", sa.String(500), nullable=True),
        sa.Column("irpj", NUMERIC, nullable=False, server_default="0"),
        sa.Column("csll", NUMERIC, nullable=False, server_default="0"),
        sa.Column("cofins", NUMERIC, nullable=False, server_default="0"),
        sa.Column("pis", NUMERIC, nullable=False, server_default="0"),
        sa.Column("inss_cpp", NUMERIC, nullable=False, server_default="0"),
        sa.Column("icms", NUMERIC, nullable=False, server_default="0"),
        sa.Column("ipi", NUMERIC, nullable=False, server_default="0"),
        sa.Column("iss", NUMERIC, nullable=False, server_default="0"),
        sa.Column("total_das", NUMERIC, nullable=False, server_default="0"),
        sa.Column("receitas_14m", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("periodo_id", name="uq_pgdas_periodo"),
    )

    op.create_table(
        "despesa_sintetica",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("periodo_id", sa.Integer, sa.ForeignKey("periodo.id"), nullable=False, index=True),
        sa.Column("despesas_administrativas", NUMERIC, nullable=False, server_default="0"),
        sa.Column("despesas_comerciais", NUMERIC, nullable=False, server_default="0"),
        sa.Column("despesas_tributarias", NUMERIC, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("periodo_id", name="uq_despesa_periodo"),
    )

    op.create_table(
        "cenario",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("empresa_id", sa.Integer, sa.ForeignKey("empresa.id"), nullable=False, index=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("overrides", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("criado_por", sa.Integer, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "apuracao",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("periodo_id", sa.Integer, sa.ForeignKey("periodo.id"), nullable=False, index=True),
        sa.Column("cenario_id", sa.Integer, sa.ForeignKey("cenario.id"), nullable=True, index=True),
        sa.Column("regime", regime, nullable=False),
        sa.Column("irpj", NUMERIC, nullable=False, server_default="0"),
        sa.Column("csll", NUMERIC, nullable=False, server_default="0"),
        sa.Column("pis", NUMERIC, nullable=False, server_default="0"),
        sa.Column("cofins", NUMERIC, nullable=False, server_default="0"),
        sa.Column("inss_cpp", NUMERIC, nullable=False, server_default="0"),
        sa.Column("icms", NUMERIC, nullable=False, server_default="0"),
        sa.Column("ipi", NUMERIC, nullable=False, server_default="0"),
        sa.Column("iss", NUMERIC, nullable=False, server_default="0"),
        sa.Column("total", NUMERIC, nullable=False, server_default="0"),
        sa.Column("aliquota_efetiva", NUMERIC, nullable=False, server_default="0"),
        sa.Column("detalhamento", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("periodo_id", "regime", "cenario_id", name="uq_apuracao_periodo_regime_cenario"),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuario.id"), nullable=True, index=True),
        sa.Column("acao", sa.String(50), nullable=False, index=True),
        sa.Column("recurso", sa.String(50), nullable=False, index=True),
        sa.Column("recurso_id", sa.Integer, nullable=True),
        sa.Column("metadados", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "audit_log", "apuracao", "cenario", "despesa_sintetica", "pgdas_declaracao",
        "folha_mensal", "credito_icms", "credito_pis_cofins", "faturamento_mensal",
        "documento", "periodo", "empresa", "grupo", "usuario",
    ]:
        op.drop_table(table)
    for enum_name in ["statusdocumento", "tipodocumento", "regimetributario", "tipoempresa"]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
