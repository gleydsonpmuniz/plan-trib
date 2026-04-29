from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin

NUMERIC = Numeric(18, 6)


class FaturamentoMensal(Base, TimestampMixin):
    __tablename__ = "faturamento_mensal"

    id: Mapped[int] = mapped_column(primary_key=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("periodo.id"), nullable=False, index=True)
    cfop: Mapped[str] = mapped_column(String(4), nullable=False)
    cst: Mapped[str | None] = mapped_column(String(3), nullable=True)
    valor_operacao: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    base_icms: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    valor_icms: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    valor_ipi: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
