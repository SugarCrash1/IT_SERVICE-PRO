"""Modelos de Guías de Remisión: despacho de equipos/materiales hacia una
empresa cliente, con detalle de productos y afectación al Kardex al
confirmarse la entrega."""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import EstadoGuia, TipoGuia
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.itsp_foundation_model import EmpresaCliente
    from app.models.product_model import Producto
    from app.models.ticket_model import Ticket
    from app.models.user_model import Usuario


class GuiaRemision(Base, TimestampMixin):
    """Cabecera de una guía de remisión / despacho hacia una empresa cliente."""

    __tablename__ = "guias_remision"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    empresa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("empresas_cliente.id", ondelete="RESTRICT"), nullable=False, index=True)
    ticket_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True)
    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default=TipoGuia.ENTREGA_EQUIPO)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default=EstadoGuia.EMITIDA)
    direccion_entrega: Mapped[str | None] = mapped_column(String(250), nullable=True)
    transportista: Mapped[str | None] = mapped_column(String(150), nullable=True)
    fecha_emision: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    fecha_entrega: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    empresa: Mapped["EmpresaCliente"] = relationship()
    ticket: Mapped["Ticket | None"] = relationship()
    usuario: Mapped["Usuario"] = relationship()
    detalles: Mapped[list["GuiaDetalle"]] = relationship(back_populates="guia", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<GuiaRemision {self.numero}>"


class GuiaDetalle(Base):
    """Línea de producto dentro de una guía de remisión."""

    __tablename__ = "guia_detalles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    guia_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("guias_remision.id", ondelete="CASCADE"), nullable=False)
    producto_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(250), nullable=True)

    guia: Mapped["GuiaRemision"] = relationship(back_populates="detalles")
    producto: Mapped["Producto"] = relationship()
