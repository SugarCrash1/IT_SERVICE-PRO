"""Esquemas de la Fase 1 de IT Service Pro."""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmpresaCreate(BaseModel):
    razon_social: str = Field(min_length=2, max_length=180)
    nombre_comercial: str | None = None
    ruc: str = Field(min_length=8, max_length=20)
    sector: str | None = None
    sitio_web: str | None = None
    correo: EmailStr | None = None
    telefono: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    pais: str = "Perú"
    nivel_sla: str = "STANDARD"
    contrato_inicio: date | None = None
    contrato_fin: date | None = None
    logo_url: str | None = None


class EmpresaResponse(EmpresaCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    estado: str
    created_at: datetime


class ContactoCreate(BaseModel):
    empresa_id: UUID
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    cargo: str | None = None
    area: str | None = None
    correo: EmailStr
    telefono: str | None = None
    puede_crear_tickets: bool = True
    es_contacto_principal: bool = False


class ContactoResponse(ContactoCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    estado: str
    created_at: datetime


class ServicioTICreate(BaseModel):
    codigo: str = Field(min_length=2, max_length=30)
    nombre: str = Field(min_length=2, max_length=150)
    categoria: str = Field(min_length=2, max_length=80)
    descripcion: str | None = None
    tecnologia: str | None = None
    tiempo_respuesta_horas: int = Field(default=8, ge=1, le=720)
    precio_base: float = Field(default=0, ge=0)
    imagen_url: str | None = None
    destacado: bool = False


class ServicioTIResponse(ServicioTICreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    estado: str
    created_at: datetime


class EmpresaUpdate(BaseModel):
    razon_social: str | None = Field(default=None, min_length=2, max_length=180)
    nombre_comercial: str | None = None
    sector: str | None = None
    sitio_web: str | None = None
    correo: EmailStr | None = None
    telefono: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    nivel_sla: str | None = None
    contrato_inicio: date | None = None
    contrato_fin: date | None = None
    logo_url: str | None = None


class ContactoUpdate(BaseModel):
    nombres: str | None = Field(default=None, min_length=2, max_length=100)
    apellidos: str | None = Field(default=None, min_length=2, max_length=100)
    cargo: str | None = None
    area: str | None = None
    correo: EmailStr | None = None
    telefono: str | None = None
    puede_crear_tickets: bool | None = None
    es_contacto_principal: bool | None = None


class ServicioTIUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    categoria: str | None = Field(default=None, min_length=2, max_length=80)
    descripcion: str | None = None
    tecnologia: str | None = None
    tiempo_respuesta_horas: int | None = Field(default=None, ge=1, le=720)
    precio_base: float | None = Field(default=None, ge=0)
    imagen_url: str | None = None
    destacado: bool | None = None


class CambiarEstadoRequest(BaseModel):
    estado: str = Field(pattern="^(ACTIVO|INACTIVO)$")
