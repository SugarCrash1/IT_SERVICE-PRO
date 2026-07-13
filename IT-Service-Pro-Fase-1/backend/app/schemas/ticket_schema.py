"""Esquemas del módulo de tickets (mesa de ayuda)."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.core.constants import CanalTicket, CategoriaTicket, EstadoTicket, PrioridadTicket


class TicketCrearRequest(BaseModel):
    empresa_id: uuid.UUID
    contacto_id: Optional[uuid.UUID] = None
    servicio_id: Optional[uuid.UUID] = None
    titulo: str = Field(min_length=4, max_length=200)
    descripcion: str = Field(min_length=4, max_length=8000)
    categoria: str = CategoriaTicket.INCIDENTE
    prioridad: str = PrioridadTicket.MEDIA
    canal: str = CanalTicket.INTERNO
    asignado_a: Optional[uuid.UUID] = None

    @field_validator("categoria")
    @classmethod
    def categoria_valida(cls, v):
        if v not in CategoriaTicket.TODOS:
            raise ValueError(f"Categoría inválida. Valores permitidos: {', '.join(CategoriaTicket.TODOS)}")
        return v

    @field_validator("prioridad")
    @classmethod
    def prioridad_valida(cls, v):
        if v not in PrioridadTicket.TODOS:
            raise ValueError(f"Prioridad inválida. Valores permitidos: {', '.join(PrioridadTicket.TODOS)}")
        return v

    @field_validator("canal")
    @classmethod
    def canal_valido(cls, v):
        if v not in CanalTicket.TODOS:
            raise ValueError(f"Canal inválido. Valores permitidos: {', '.join(CanalTicket.TODOS)}")
        return v


class TicketPortalCrearRequest(BaseModel):
    """Creación de un ticket desde el portal del cliente (empresa/contacto se
    infieren de la sesión autenticada, no se reciben del cliente)."""

    servicio_id: Optional[uuid.UUID] = None
    titulo: str = Field(min_length=4, max_length=200)
    descripcion: str = Field(min_length=4, max_length=8000)
    categoria: str = CategoriaTicket.INCIDENTE
    prioridad: str = PrioridadTicket.MEDIA

    @field_validator("categoria")
    @classmethod
    def categoria_valida(cls, v):
        if v not in CategoriaTicket.TODOS:
            raise ValueError(f"Categoría inválida. Valores permitidos: {', '.join(CategoriaTicket.TODOS)}")
        return v

    @field_validator("prioridad")
    @classmethod
    def prioridad_valida(cls, v):
        if v not in PrioridadTicket.TODOS:
            raise ValueError(f"Prioridad inválida. Valores permitidos: {', '.join(PrioridadTicket.TODOS)}")
        return v


class TicketActualizarRequest(BaseModel):
    titulo: Optional[str] = Field(default=None, min_length=4, max_length=200)
    descripcion: Optional[str] = Field(default=None, min_length=4, max_length=8000)
    servicio_id: Optional[uuid.UUID] = None
    categoria: Optional[str] = None
    prioridad: Optional[str] = None

    @field_validator("categoria")
    @classmethod
    def categoria_valida(cls, v):
        if v is not None and v not in CategoriaTicket.TODOS:
            raise ValueError(f"Categoría inválida. Valores permitidos: {', '.join(CategoriaTicket.TODOS)}")
        return v

    @field_validator("prioridad")
    @classmethod
    def prioridad_valida(cls, v):
        if v is not None and v not in PrioridadTicket.TODOS:
            raise ValueError(f"Prioridad inválida. Valores permitidos: {', '.join(PrioridadTicket.TODOS)}")
        return v


class TicketCambiarEstadoRequest(BaseModel):
    estado: str
    motivo_cierre: Optional[str] = Field(default=None, max_length=500)

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v):
        if v not in EstadoTicket.TODOS:
            raise ValueError(f"Estado inválido. Valores permitidos: {', '.join(EstadoTicket.TODOS)}")
        return v


class TicketAsignarRequest(BaseModel):
    empleado_id: uuid.UUID


class TicketComentarioCrearRequest(BaseModel):
    contenido: str = Field(min_length=1, max_length=8000)
    es_interno: bool = False


class TicketAdjuntoCrearRequest(BaseModel):
    comentario_id: Optional[uuid.UUID] = None
    nombre_archivo: str = Field(min_length=1, max_length=255)
    url_archivo: str = Field(min_length=1)
    tipo_mime: Optional[str] = None
    tamano_bytes: Optional[int] = None


class TicketSatisfaccionRequest(BaseModel):
    calificacion: int = Field(ge=1, le=5)
    comentario: Optional[str] = Field(default=None, max_length=500)


class TicketTiempoRequest(BaseModel):
    minutos: int = Field(gt=0, le=1440)
    nota: Optional[str] = Field(default=None, max_length=300)


# ---- Respuestas -----------------------------------------------------------

class TicketAdjuntoResponse(BaseModel):
    id: uuid.UUID
    comentario_id: Optional[uuid.UUID]
    nombre_archivo: str
    url_archivo: str
    tipo_mime: Optional[str]
    tamano_bytes: Optional[int]
    created_at: datetime
    model_config = {"from_attributes": True}


class TicketComentarioResponse(BaseModel):
    id: uuid.UUID
    autor_nombre: str
    contenido: str
    es_interno: bool
    es_del_cliente: bool
    created_at: datetime
    adjuntos: list[TicketAdjuntoResponse] = []
    model_config = {"from_attributes": True}


class TicketHistorialResponse(BaseModel):
    id: uuid.UUID
    actor_nombre: str
    evento: str
    descripcion: str
    created_at: datetime
    model_config = {"from_attributes": True}


class TicketListItemResponse(BaseModel):
    id: uuid.UUID
    codigo: str
    empresa_id: uuid.UUID
    empresa_nombre: str
    contacto_id: Optional[uuid.UUID]
    contacto_nombre: Optional[str]
    tecnico_id: Optional[uuid.UUID]
    tecnico_nombre: Optional[str]
    titulo: str
    categoria: str
    prioridad: str
    estado: str
    canal: str
    fecha_limite_respuesta: datetime
    fecha_limite_resolucion: datetime
    fecha_primera_respuesta: Optional[datetime]
    vencido: bool
    created_at: datetime
    updated_at: datetime


class TicketResponse(TicketListItemResponse):
    descripcion: str
    servicio_id: Optional[uuid.UUID]
    servicio_nombre: Optional[str]
    horas_respuesta_sla: int
    horas_resolucion_sla: int
    fecha_resolucion: Optional[datetime]
    fecha_cierre: Optional[datetime]
    tiempo_invertido_minutos: int
    calificacion_satisfaccion: Optional[int]
    comentario_satisfaccion: Optional[str]
    motivo_cierre: Optional[str]
    comentarios: list[TicketComentarioResponse] = []
    adjuntos: list[TicketAdjuntoResponse] = []
    historial: list[TicketHistorialResponse] = []


class ResumenTicketsResponse(BaseModel):
    total: int
    por_estado: dict[str, int]
    por_prioridad: dict[str, int]
    vencidos: int
    sin_asignar: int
    resueltos_mes: int
    tiempo_promedio_resolucion_horas: float | None
