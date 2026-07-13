"""Esquemas del módulo de Proyectos."""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import EstadoProyecto, EstadoTareaProyecto


class ProyectoCreate(BaseModel):
    empresa_id: UUID
    responsable_id: UUID | None = None
    nombre: str = Field(min_length=2, max_length=180)
    descripcion: str | None = None
    fecha_inicio: date | None = None
    fecha_fin_estimada: date | None = None
    presupuesto: float | None = Field(default=None, ge=0)


class ProyectoUpdate(BaseModel):
    responsable_id: UUID | None = None
    nombre: str | None = Field(default=None, min_length=2, max_length=180)
    descripcion: str | None = None
    fecha_inicio: date | None = None
    fecha_fin_estimada: date | None = None
    fecha_fin_real: date | None = None
    presupuesto: float | None = Field(default=None, ge=0)
    avance_porcentaje: int | None = Field(default=None, ge=0, le=100)
    estado: str | None = None

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v):
        if v is not None and v not in EstadoProyecto.TODOS:
            raise ValueError(f"Estado inválido. Valores permitidos: {', '.join(EstadoProyecto.TODOS)}")
        return v


class TareaCreate(BaseModel):
    titulo: str = Field(min_length=2, max_length=200)
    responsable_id: UUID | None = None
    fecha_limite: date | None = None


class TareaUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=2, max_length=200)
    responsable_id: UUID | None = None
    fecha_limite: date | None = None
    estado: str | None = None

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v):
        if v is not None and v not in EstadoTareaProyecto.TODOS:
            raise ValueError(f"Estado inválido. Valores permitidos: {', '.join(EstadoTareaProyecto.TODOS)}")
        return v


class TareaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    proyecto_id: UUID
    titulo: str
    estado: str
    responsable_id: UUID | None
    responsable_nombre: str | None = None
    fecha_limite: date | None
    created_at: datetime


class ProyectoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    codigo: str
    empresa_id: UUID
    empresa_nombre: str
    responsable_id: UUID | None
    responsable_nombre: str | None
    nombre: str
    descripcion: str | None
    estado: str
    fecha_inicio: date | None
    fecha_fin_estimada: date | None
    fecha_fin_real: date | None
    presupuesto: float | None
    avance_porcentaje: int
    total_tareas: int
    tareas_completadas: int
    created_at: datetime
    updated_at: datetime
    tareas: list[TareaResponse] = []
