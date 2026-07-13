"""Modelos base de IT Service Pro: empresas, contactos y servicios TI."""
import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class EmpresaCliente(Base, TimestampMixin):
    __tablename__ = "empresas_cliente"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    razon_social: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    nombre_comercial: Mapped[str | None] = mapped_column(String(150))
    ruc: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    sector: Mapped[str | None] = mapped_column(String(100))
    sitio_web: Mapped[str | None] = mapped_column(String(255))
    correo: Mapped[str | None] = mapped_column(String(180))
    telefono: Mapped[str | None] = mapped_column(String(40))
    direccion: Mapped[str | None] = mapped_column(String(255))
    ciudad: Mapped[str | None] = mapped_column(String(100))
    pais: Mapped[str] = mapped_column(String(80), default="Perú", nullable=False)
    nivel_sla: Mapped[str] = mapped_column(String(30), default="STANDARD", nullable=False)
    contrato_inicio: Mapped[date | None] = mapped_column(Date)
    contrato_fin: Mapped[date | None] = mapped_column(Date)
    logo_url: Mapped[str | None] = mapped_column(String(500))
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVO", nullable=False, index=True)

    contactos: Mapped[list["ContactoEmpresa"]] = relationship(back_populates="empresa", cascade="all, delete-orphan")


class ContactoEmpresa(Base, TimestampMixin):
    __tablename__ = "contactos_empresa"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("empresas_cliente.id", ondelete="CASCADE"), nullable=False, index=True)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    cargo: Mapped[str | None] = mapped_column(String(120))
    area: Mapped[str | None] = mapped_column(String(100))
    correo: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    telefono: Mapped[str | None] = mapped_column(String(40))
    puede_crear_tickets: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    es_contacto_principal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVO", nullable=False)

    empresa: Mapped[EmpresaCliente] = relationship(back_populates="contactos")


class ServicioTI(Base, TimestampMixin):
    __tablename__ = "servicios_ti"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    categoria: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(Text)
    tecnologia: Mapped[str | None] = mapped_column(String(180))
    tiempo_respuesta_horas: Mapped[int] = mapped_column(default=8, nullable=False)
    precio_base: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    imagen_url: Mapped[str | None] = mapped_column(String(500))
    destacado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVO", nullable=False)
