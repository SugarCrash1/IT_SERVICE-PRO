"""Esquemas del módulo de Documentos."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentoCreate(BaseModel):
    empresa_id: UUID
    nombre: str = Field(min_length=2, max_length=200)
    categoria: str = "General"
    url_archivo: str = Field(min_length=1, max_length=500)
    tipo_mime: str | None = None
    tamano_bytes: int | None = None
    visible_portal: bool = True


class DocumentoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=200)
    categoria: str | None = None
    visible_portal: bool | None = None


class DocumentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    empresa_nombre: str
    nombre: str
    categoria: str
    url_archivo: str
    tipo_mime: str | None
    tamano_bytes: int | None
    visible_portal: bool
    subido_por_nombre: str | None
    created_at: datetime
