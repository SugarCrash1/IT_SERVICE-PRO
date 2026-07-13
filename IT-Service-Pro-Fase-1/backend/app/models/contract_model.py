"""Modelo del módulo de Contratos: acuerdos de servicio por empresa cliente."""
import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import EstadoContrato, TipoContrato
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.itsp_foundation_model import EmpresaCliente


class Contrato(Base, TimestampMixin):
    """Contrato de servicios TI vigente (o histórico) con una empresa cliente."""

    __tablename__ = "contratos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    empresa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("empresas_cliente.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(180), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default=TipoContrato.SOPORTE)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    horas_incluidas_mes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    horas_consumidas_mes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valor_mensual: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default=EstadoContrato.VIGENTE)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

    empresa: Mapped["EmpresaCliente"] = relationship()

    def __repr__(self) -> str:
        return f"<Contrato {self.codigo} {self.nombre}>"
