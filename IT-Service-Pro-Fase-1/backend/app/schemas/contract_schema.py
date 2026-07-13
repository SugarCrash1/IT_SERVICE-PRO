"""Esquemas del módulo de Contratos."""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import EstadoContrato, TipoContrato


class ContratoCreate(BaseModel):
    empresa_id: UUID
    nombre: str = Field(min_length=2, max_length=180)
    tipo: str = TipoContrato.SOPORTE
    fecha_inicio: date
    fecha_fin: date | None = None
    horas_incluidas_mes: int | None = Field(default=None, ge=0)
    valor_mensual: float | None = Field(default=None, ge=0)
    notas: str | None = None

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v):
        if v not in TipoContrato.TODOS:
            raise ValueError(f"Tipo inválido. Valores permitidos: {', '.join(TipoContrato.TODOS)}")
        return v


class ContratoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=180)
    tipo: str | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    horas_incluidas_mes: int | None = Field(default=None, ge=0)
    horas_consumidas_mes: int | None = Field(default=None, ge=0)
    valor_mensual: float | None = Field(default=None, ge=0)
    estado: str | None = None
    notas: str | None = None

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v):
        if v is not None and v not in TipoContrato.TODOS:
            raise ValueError(f"Tipo inválido. Valores permitidos: {', '.join(TipoContrato.TODOS)}")
        return v

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v):
        if v is not None and v not in EstadoContrato.TODOS:
            raise ValueError(f"Estado inválido. Valores permitidos: {', '.join(EstadoContrato.TODOS)}")
        return v


class ContratoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    codigo: str
    empresa_id: UUID
    empresa_nombre: str
    nombre: str
    tipo: str
    fecha_inicio: date
    fecha_fin: date | None
    horas_incluidas_mes: int | None
    horas_consumidas_mes: int
    valor_mensual: float | None
    estado: str
    notas: str | None
    dias_para_vencer: int | None
    created_at: datetime
