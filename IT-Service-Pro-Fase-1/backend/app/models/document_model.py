"""Modelo de Documentos: repositorio de archivos por empresa (contratos
firmados, manuales, facturas escaneadas) compartidos opcionalmente con el
portal del cliente."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.itsp_foundation_model import EmpresaCliente
    from app.models.user_model import Usuario


class Documento(Base, TimestampMixin):
    """Archivo almacenado y asociado a una empresa cliente."""

    __tablename__ = "documentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("empresas_cliente.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    categoria: Mapped[str] = mapped_column(String(60), nullable=False, default="General")
    url_archivo: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_mime: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tamano_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    visible_portal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    subido_por_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    empresa: Mapped["EmpresaCliente"] = relationship()
    subido_por: Mapped["Usuario | None"] = relationship()

    def __repr__(self) -> str:
        return f"<Documento {self.nombre}>"
