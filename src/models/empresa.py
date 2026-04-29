import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.grupo import Grupo


class TipoEmpresa(str, enum.Enum):
    MATRIZ = "matriz"
    FILIAL = "filial"
    INDEPENDENTE = "independente"


class RegimeTributario(str, enum.Enum):
    SIMPLES = "SIMPLES"
    LUCRO_PRESUMIDO = "LP"
    LUCRO_REAL = "LR"


class Empresa(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "empresa"

    id: Mapped[int] = mapped_column(primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, index=True, nullable=False)
    razao_social: Mapped[str] = mapped_column(String(255), nullable=False)
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupo.id"), nullable=False, index=True)
    tipo: Mapped[TipoEmpresa] = mapped_column(SAEnum(TipoEmpresa), nullable=False)
    regime_atual: Mapped[RegimeTributario] = mapped_column(
        SAEnum(RegimeTributario), nullable=False
    )
    atividade_principal: Mapped[str | None] = mapped_column(String(255), nullable=True)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    municipio_ibge: Mapped[str | None] = mapped_column(String(7), nullable=True)

    grupo: Mapped["Grupo"] = relationship(back_populates="empresas")
