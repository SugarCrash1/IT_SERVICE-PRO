"""Esquemas del módulo de Timesheet (registro de horas)."""
from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RegistroTiempoCreate(BaseModel):
    empleado_id: UUID | None = None
    ticket_id: UUID | None = None
    proyecto_id: UUID | None = None
    fecha: date
    minutos: int = Field(gt=0, le=1440)
    descripcion: str = Field(min_length=2, max_length=300)
    facturable: bool = True


class RegistroTiempoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empleado_id: UUID
    empleado_nombre: str
    ticket_id: UUID | None
    ticket_codigo: str | None
    proyecto_id: UUID | None
    proyecto_nombre: str | None
    fecha: date
    minutos: int
    descripcion: str
    facturable: bool


class ResumenTimesheetResponse(BaseModel):
    total_horas: float
    horas_facturables: float
    horas_no_facturables: float
    por_empleado: dict[str, float]
