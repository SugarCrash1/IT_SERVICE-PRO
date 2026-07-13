"""Esquemas del módulo CMDB (activos tecnológicos)."""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import EstadoActivo, TipoActivo


class ActivoCreate(BaseModel):
    empresa_id: UUID
    responsable_id: UUID | None = None
    tipo: str = TipoActivo.OTRO
    nombre: str = Field(min_length=2, max_length=150)
    marca: str | None = None
    modelo: str | None = None
    numero_serie: str | None = None
    ubicacion: str | None = None
    ip_asignada: str | None = None
    fecha_compra: date | None = None
    fecha_garantia_fin: date | None = None
    notas: str | None = None

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v):
        if v not in TipoActivo.TODOS:
            raise ValueError(f"Tipo inválido. Valores permitidos: {', '.join(TipoActivo.TODOS)}")
        return v


class ActivoUpdate(BaseModel):
    responsable_id: UUID | None = None
    tipo: str | None = None
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    marca: str | None = None
    modelo: str | None = None
    numero_serie: str | None = None
    ubicacion: str | None = None
    ip_asignada: str | None = None
    fecha_compra: date | None = None
    fecha_garantia_fin: date | None = None
    notas: str | None = None

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v):
        if v is not None and v not in TipoActivo.TODOS:
            raise ValueError(f"Tipo inválido. Valores permitidos: {', '.join(TipoActivo.TODOS)}")
        return v


class ActivoCambiarEstadoRequest(BaseModel):
    estado: str

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v):
        if v not in EstadoActivo.TODOS:
            raise ValueError(f"Estado inválido. Valores permitidos: {', '.join(EstadoActivo.TODOS)}")
        return v


class ActivoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    codigo: str
    empresa_id: UUID
    empresa_nombre: str
    responsable_id: UUID | None
    responsable_nombre: str | None
    tipo: str
    nombre: str
    marca: str | None
    modelo: str | None
    numero_serie: str | None
    ubicacion: str | None
    ip_asignada: str | None
    fecha_compra: date | None
    fecha_garantia_fin: date | None
    notas: str | None
    estado: str
    garantia_vencida: bool
    created_at: datetime
    updated_at: datetime
