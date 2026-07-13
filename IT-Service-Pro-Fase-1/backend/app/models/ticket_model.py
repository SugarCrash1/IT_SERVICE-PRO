"""Modelos del módulo de Tickets (mesa de ayuda): tickets, comentarios,
adjuntos, historial de cambios y políticas de SLA por nivel de servicio."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CanalTicket, CategoriaTicket, EstadoTicket, PrioridadTicket
from app.database.base import AuditUserMixin, Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.employee_model import Empleado
    from app.models.itsp_foundation_model import ContactoEmpresa, EmpresaCliente, ServicioTI
    from app.models.user_model import Usuario


class SLAPolitica(Base, TimestampMixin):
    """Define, por nivel de SLA contratado y prioridad, en cuántas horas se
    debe dar primera respuesta y resolución a un ticket."""

    __tablename__ = "sla_politicas"
    __table_args__ = (UniqueConstraint("nivel_sla", "prioridad", name="uq_sla_nivel_prioridad"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nivel_sla: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    prioridad: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    horas_respuesta: Mapped[int] = mapped_column(Integer, nullable=False)
    horas_resolucion: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<SLAPolitica {self.nivel_sla}/{self.prioridad}>"


class Ticket(Base, TimestampMixin, AuditUserMixin):
    """Representa un ticket de soporte (incidente, requerimiento, consulta,
    cambio o problema) levantado por una empresa cliente."""

    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    empresa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas_cliente.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    contacto_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("contactos_empresa.id", ondelete="SET NULL"), nullable=True, index=True
    )
    servicio_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("servicios_ti.id", ondelete="SET NULL"), nullable=True, index=True
    )
    asignado_a: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True
    )

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    categoria: Mapped[str] = mapped_column(String(30), nullable=False, default=CategoriaTicket.INCIDENTE)
    prioridad: Mapped[str] = mapped_column(String(20), nullable=False, default=PrioridadTicket.MEDIA)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default=EstadoTicket.ABIERTO, index=True)
    canal: Mapped[str] = mapped_column(String(20), nullable=False, default=CanalTicket.PORTAL)

    horas_respuesta_sla: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    horas_resolucion_sla: Mapped[int] = mapped_column(Integer, nullable=False, default=48)
    fecha_limite_respuesta: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_limite_resolucion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_primera_respuesta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_resolucion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tiempo_invertido_minutos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    calificacion_satisfaccion: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comentario_satisfaccion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    motivo_cierre: Mapped[str | None] = mapped_column(String(500), nullable=True)

    empresa: Mapped["EmpresaCliente"] = relationship()
    contacto: Mapped["ContactoEmpresa | None"] = relationship()
    servicio: Mapped["ServicioTI | None"] = relationship()
    tecnico: Mapped["Empleado | None"] = relationship()

    comentarios: Mapped[list["TicketComentario"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", order_by="TicketComentario.created_at"
    )
    adjuntos: Mapped[list["TicketAdjunto"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", order_by="TicketAdjunto.created_at"
    )
    historial: Mapped[list["TicketHistorial"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", order_by="TicketHistorial.created_at"
    )

    def __repr__(self) -> str:
        return f"<Ticket {self.codigo} estado={self.estado}>"


class TicketComentario(Base, TimestampMixin):
    """Comentario o respuesta dentro de la conversación de un ticket.
    Puede ser una nota interna (solo visible al equipo técnico) o una
    respuesta visible para el contacto de la empresa cliente."""

    __tablename__ = "ticket_comentarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    autor_usuario_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    autor_nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    es_interno: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    es_del_cliente: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    ticket: Mapped["Ticket"] = relationship(back_populates="comentarios")
    autor: Mapped["Usuario | None"] = relationship()
    adjuntos: Mapped[list["TicketAdjunto"]] = relationship(back_populates="comentario")

    def __repr__(self) -> str:
        return f"<TicketComentario ticket={self.ticket_id}>"


class TicketAdjunto(Base, TimestampMixin):
    """Archivo adjunto a un ticket o a uno de sus comentarios."""

    __tablename__ = "ticket_adjuntos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    comentario_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ticket_comentarios.id", ondelete="CASCADE"), nullable=True
    )
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    url_archivo: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_mime: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tamano_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subido_por_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    ticket: Mapped["Ticket"] = relationship(back_populates="adjuntos")
    comentario: Mapped["TicketComentario | None"] = relationship(back_populates="adjuntos")

    def __repr__(self) -> str:
        return f"<TicketAdjunto {self.nombre_archivo}>"


class TicketHistorial(Base):
    """Línea de tiempo de cambios relevantes de un ticket (estado, prioridad,
    asignación), usada para reconstruir el timeline en la interfaz."""

    __tablename__ = "ticket_historial"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    actor_nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    evento: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    ticket: Mapped["Ticket"] = relationship(back_populates="historial")

    def __repr__(self) -> str:
        return f"<TicketHistorial {self.evento} ticket={self.ticket_id}>"
