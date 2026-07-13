"""Modelo del CMDB: activos tecnológicos propiedad o en gestión de cada
empresa cliente (servidores, laptops, licencias, etc.)."""
import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import EstadoActivo, TipoActivo
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.itsp_foundation_model import ContactoEmpresa, EmpresaCliente


class Activo(Base, TimestampMixin):
    """Representa un activo de TI (hardware, software o licencia) que la
    consultora administra o da soporte para una empresa cliente."""

    __tablename__ = "activos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas_cliente.id", ondelete="CASCADE"), nullable=False, index=True
    )
    responsable_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("contactos_empresa.id", ondelete="SET NULL"), nullable=True
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default=TipoActivo.OTRO)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    marca: Mapped[str | None] = mapped_column(String(100), nullable=True)
    modelo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    numero_serie: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ubicacion: Mapped[str | None] = mapped_column(String(150), nullable=True)
    ip_asignada: Mapped[str | None] = mapped_column(String(60), nullable=True)
    fecha_compra: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_garantia_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default=EstadoActivo.ACTIVO)

    empresa: Mapped["EmpresaCliente"] = relationship()
    responsable: Mapped["ContactoEmpresa | None"] = relationship()

    def __repr__(self) -> str:
        return f"<Activo {self.codigo} {self.nombre}>"
