from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class Periodo(Base, TimestampMixin):
    __tablename__ = "periodo"
    __table_args__ = (UniqueConstraint("empresa_id", "ano", "mes", name="uq_periodo_empresa_competencia"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresa.id"), nullable=False, index=True)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)

    @property
    def competencia(self) -> str:
        return f"{self.ano:04d}-{self.mes:02d}"
