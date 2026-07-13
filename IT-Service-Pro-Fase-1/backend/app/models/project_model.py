"""Modelos del módulo de Proyectos: proyecto y sus tareas, por empresa cliente."""
import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import EstadoProyecto, EstadoTareaProyecto
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.employee_model import Empleado
    from app.models.itsp_foundation_model import EmpresaCliente


class Proyecto(Base, TimestampMixin):
    """Proyecto de implementación o consultoría entregado a una empresa cliente."""

    __tablename__ = "proyectos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    empresa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("empresas_cliente.id", ondelete="CASCADE"), nullable=False, index=True)
    responsable_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True)
    nombre: Mapped[str] = mapped_column(String(180), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default=EstadoProyecto.PLANIFICACION)
    fecha_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_fin_estimada: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_fin_real: Mapped[date | None] = mapped_column(Date, nullable=True)
    presupuesto: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    avance_porcentaje: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    empresa: Mapped["EmpresaCliente"] = relationship()
    responsable: Mapped["Empleado | None"] = relationship()
    tareas: Mapped[list["ProyectoTarea"]] = relationship(back_populates="proyecto", cascade="all, delete-orphan", order_by="ProyectoTarea.created_at")

    def __repr__(self) -> str:
        return f"<Proyecto {self.codigo} {self.nombre}>"


class ProyectoTarea(Base, TimestampMixin):
    """Tarea o hito dentro de un proyecto."""

    __tablename__ = "proyecto_tareas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proyecto_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("proyectos.id", ondelete="CASCADE"), nullable=False, index=True)
    responsable_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default=EstadoTareaProyecto.PENDIENTE)
    fecha_limite: Mapped[date | None] = mapped_column(Date, nullable=True)

    proyecto: Mapped["Proyecto"] = relationship(back_populates="tareas")
    responsable: Mapped["Empleado | None"] = relationship()

    def __repr__(self) -> str:
        return f"<ProyectoTarea {self.titulo}>"
