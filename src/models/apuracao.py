from decimal import Decimal

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin
from src.models.empresa import RegimeTributario

NUMERIC = Numeric(18, 6)


class Apuracao(Base, TimestampMixin):
    __tablename__ = "apuracao"
    __table_args__ = (
        UniqueConstraint("periodo_id", "regime", "cenario_id", name="uq_apuracao_periodo_regime_cenario"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("periodo.id"), nullable=False, index=True)
    cenario_id: Mapped[int | None] = mapped_column(ForeignKey("cenario.id"), nullable=True, index=True)
    regime: Mapped[RegimeTributario] = mapped_column(SAEnum(RegimeTributario), nullable=False)

    irpj: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    csll: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    pis: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    cofins: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    inss_cpp: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    icms: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    ipi: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    iss: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    total: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)
    aliquota_efetiva: Mapped[Decimal] = mapped_column(NUMERIC, default=Decimal(0), nullable=False)

    detalhamento: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
