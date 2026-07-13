"""Modelo de la Base de Conocimiento: artículos técnicos reutilizables."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.itsp_foundation_model import ServicioTI
    from app.models.user_model import Usuario


class ArticuloConocimiento(Base, TimestampMixin):
    """Artículo técnico de la base de conocimiento interna (soluciones,
    procedimientos, guías) que el equipo puede reutilizar al resolver tickets."""

    __tablename__ = "articulos_conocimiento"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    categoria: Mapped[str] = mapped_column(String(80), nullable=False, default="General")
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("servicios_ti.id", ondelete="SET NULL"), nullable=True)
    autor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    publicado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    vistas: Mapped[int] = mapped_column(nullable=False, default=0)

    servicio: Mapped["ServicioTI | None"] = relationship()
    autor: Mapped["Usuario | None"] = relationship()

    def __repr__(self) -> str:
        return f"<ArticuloConocimiento {self.titulo}>"
