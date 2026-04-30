import enum

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, SoftDeleteMixin, TimestampMixin


class TipoDocumento(str, enum.Enum):
    SPED_FISCAL = "SPED_FISCAL"
    SPED_CONTRIBUICOES = "SPED_CONTRIBUICOES"
    PDF_FOLHA = "PDF_FOLHA"
    PDF_PGDAS = "PDF_PGDAS"


class StatusDocumento(str, enum.Enum):
    PENDENTE = "PENDENTE"
    PROCESSANDO = "PROCESSANDO"
    PROCESSADO = "PROCESSADO"
    ERRO = "ERRO"


class Documento(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "documento"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresa.id"), nullable=False, index=True)
    tipo: Mapped[TipoDocumento] = mapped_column(SAEnum(TipoDocumento), nullable=False)
    nome_original: Mapped[str] = mapped_column(String(500), nullable=False)
    caminho_storage: Mapped[str] = mapped_column(String(1000), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[StatusDocumento] = mapped_column(
        SAEnum(StatusDocumento), default=StatusDocumento.PENDENTE, nullable=False
    )
    erro_msg: Mapped[str | None] = mapped_column(Text, nullable=True)
