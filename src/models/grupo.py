from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.empresa import Empresa


class Grupo(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "grupo"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    empresas: Mapped[list["Empresa"]] = relationship(
        back_populates="grupo", cascade="all, delete-orphan"
    )
