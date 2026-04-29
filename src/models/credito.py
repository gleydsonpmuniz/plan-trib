from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin

NUMERIC = Numeric(18, 6)


class CreditoPISCOFINS(Base, TimestampMixin):
    __tablename__ = "credito_pis_cofins"

    id: Mapped[int] = mapped_column(primary_key=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("periodo.id"), nullable=False, index=True)
    base_credito: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    valor_pis: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    valor_cofins: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)


class CreditoICMS(Base, TimestampMixin):
    __tablename__ = "credito_icms"

    id: Mapped[int] = mapped_column(primary_key=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("periodo.id"), nullable=False, index=True)
    debito_total: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    credito_total: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    saldo_devedor: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    saldo_credor: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
