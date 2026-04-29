from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin

NUMERIC = Numeric(18, 6)


class DespesaSintetica(Base, TimestampMixin):
    __tablename__ = "despesa_sintetica"
    __table_args__ = (UniqueConstraint("periodo_id", name="uq_despesa_periodo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("periodo.id"), nullable=False, index=True)
    despesas_administrativas: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    despesas_comerciais: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    despesas_tributarias: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
