from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin

NUMERIC = Numeric(18, 6)


class PgdasDeclaracao(Base, TimestampMixin):
    __tablename__ = "pgdas_declaracao"
    __table_args__ = (UniqueConstraint("periodo_id", name="uq_pgdas_periodo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("periodo.id"), nullable=False, index=True)

    rpa: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    rbt12: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    rba: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    rbaa: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    fator_r: Mapped[Decimal | None] = mapped_column(NUMERIC, nullable=True)

    anexo_inferido: Mapped[str | None] = mapped_column(String(2), nullable=True)
    atividade_descricao: Mapped[str | None] = mapped_column(String(500), nullable=True)

    irpj: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    csll: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    cofins: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    pis: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    inss_cpp: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    icms: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    ipi: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    iss: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    total_das: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)

    receitas_14m: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
