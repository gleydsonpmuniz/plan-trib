from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, SoftDeleteMixin, TimestampMixin


class Cenario(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "cenario"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresa.id"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    overrides: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    criado_por: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
