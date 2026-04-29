from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin

NUMERIC = Numeric(18, 6)


class FolhaMensal(Base, TimestampMixin):
    __tablename__ = "folha_mensal"
    __table_args__ = (UniqueConstraint("periodo_id", name="uq_folha_periodo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("periodo.id"), nullable=False, index=True)

    salario_contribuicao_empregados: Mapped[Decimal] = mapped_column(
        NUMERIC, default=Decimal(0), nullable=False
    )
    base_total_inss: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    inss_segurados: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    inss_empresa: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    inss_rat: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    inss_terceiros: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    inss_total: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)

    base_fgts: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    valor_fgts: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)

    base_irrf_mensal: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    valor_irrf_mensal: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)

    pro_labore: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    folha_bruta: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)

    qtd_empregados: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
