"""Modelo de Timesheet: registro de horas facturables y no facturables por
técnico, asociado opcionalmente a un ticket o a un proyecto."""
import uuid
from datetime import date as date_type
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.employee_model import Empleado
    from app.models.project_model import Proyecto
    from app.models.ticket_model import Ticket


class RegistroTiempo(Base, TimestampMixin):
    """Entrada individual de horas trabajadas por un técnico."""

    __tablename__ = "registros_tiempo"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empleado_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True, index=True)
    proyecto_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("proyectos.id", ondelete="SET NULL"), nullable=True, index=True)
    fecha: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    minutos: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(300), nullable=False)
    facturable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    empleado: Mapped["Empleado"] = relationship()
    ticket: Mapped["Ticket | None"] = relationship()
    proyecto: Mapped["Proyecto | None"] = relationship()

    def __repr__(self) -> str:
        return f"<RegistroTiempo {self.empleado_id} {self.fecha} {self.minutos}min>"
