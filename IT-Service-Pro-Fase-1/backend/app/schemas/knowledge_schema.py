"""Esquemas de la Base de Conocimiento."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ArticuloCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=200)
    contenido: str = Field(min_length=10)
    categoria: str = "General"
    servicio_id: UUID | None = None
    publicado: bool = True


class ArticuloUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=200)
    contenido: str | None = Field(default=None, min_length=10)
    categoria: str | None = None
    servicio_id: UUID | None = None
    publicado: bool | None = None


class ArticuloResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    titulo: str
    contenido: str
    categoria: str
    servicio_id: UUID | None
    servicio_nombre: str | None
    autor_nombre: str | None
    publicado: bool
    vistas: int
    created_at: datetime
    updated_at: datetime
