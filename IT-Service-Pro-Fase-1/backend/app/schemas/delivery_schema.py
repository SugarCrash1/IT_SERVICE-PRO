"""Esquemas del módulo de Guías de Remisión."""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import EstadoGuia, TipoGuia


class GuiaDetalleCreate(BaseModel):
    producto_id: UUID
    cantidad: int = Field(gt=0)
    descripcion: str | None = None


class GuiaCreate(BaseModel):
    empresa_id: UUID
    ticket_id: UUID | None = None
    tipo: str = TipoGuia.ENTREGA_EQUIPO
    direccion_entrega: str | None = None
    transportista: str | None = None
    observaciones: str | None = None
    detalles: list[GuiaDetalleCreate] = Field(min_length=1)

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v):
        if v not in TipoGuia.TODOS:
            raise ValueError(f"Tipo inválido. Valores permitidos: {', '.join(TipoGuia.TODOS)}")
        return v


class GuiaDetalleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    producto_id: UUID
    producto_nombre: str
    cantidad: int
    descripcion: str | None


class GuiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    numero: str
    empresa_id: UUID
    empresa_nombre: str
    ticket_id: UUID | None
    ticket_codigo: str | None
    usuario_nombre: str
    tipo: str
    estado: str
    direccion_entrega: str | None
    transportista: str | None
    fecha_emision: date
    fecha_entrega: datetime | None
    observaciones: str | None
    detalles: list[GuiaDetalleResponse] = []
    created_at: datetime
