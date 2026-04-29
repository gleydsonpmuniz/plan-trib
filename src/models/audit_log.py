from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"), nullable=True, index=True)
    acao: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    recurso: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    recurso_id: Mapped[int | None] = mapped_column(nullable=True)
    metadados: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
