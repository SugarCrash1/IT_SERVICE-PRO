"""Rutas REST del módulo de Documentos."""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db, get_current_user
from app.core.constants import RolesSistema
from app.core.exceptions import NotFoundException
from app.core.permissions import require_roles
from app.models.document_model import Documento
from app.models.itsp_foundation_model import EmpresaCliente
from app.models.user_model import Usuario
from app.schemas.document_schema import DocumentoCreate, DocumentoResponse, DocumentoUpdate

router = APIRouter(
    prefix="/documents", tags=["Documentos"],
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR, RolesSistema.TECNICO))],
)


def _response(d: Documento) -> DocumentoResponse:
    return DocumentoResponse(
        id=d.id, empresa_id=d.empresa_id, empresa_nombre=d.empresa.nombre_comercial or d.empresa.razon_social,
        nombre=d.nombre, categoria=d.categoria, url_archivo=d.url_archivo, tipo_mime=d.tipo_mime,
        tamano_bytes=d.tamano_bytes, visible_portal=d.visible_portal,
        subido_por_nombre=d.subido_por.nombre_completo if d.subido_por else None, created_at=d.created_at,
    )


def _query(db: Session):
    return db.query(Documento).options(joinedload(Documento.empresa), joinedload(Documento.subido_por))


@router.get("", response_model=list[DocumentoResponse])
def listar(empresa_id: uuid.UUID | None = Query(None), categoria: str | None = Query(None), db: Session = Depends(get_db)):
    q = _query(db)
    if empresa_id:
        q = q.filter(Documento.empresa_id == empresa_id)
    if categoria:
        q = q.filter(Documento.categoria == categoria)
    return [_response(d) for d in q.order_by(Documento.created_at.desc()).all()]


@router.post("", response_model=DocumentoResponse, status_code=201,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def crear(datos: DocumentoCreate, db: Session = Depends(get_db), actor: Usuario = Depends(get_current_user)):
    if not db.get(EmpresaCliente, datos.empresa_id):
        raise NotFoundException("Empresa no encontrada")
    item = Documento(subido_por_id=actor.id, **datos.model_dump())
    db.add(item)
    db.commit()
    return _response(_query(db).filter(Documento.id == item.id).first())


@router.put("/{documento_id}", response_model=DocumentoResponse,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def actualizar(documento_id: uuid.UUID, datos: DocumentoUpdate, db: Session = Depends(get_db)):
    item = db.get(Documento, documento_id)
    if not item:
        raise NotFoundException("Documento no encontrado")
    for k, v in datos.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    return _response(_query(db).filter(Documento.id == documento_id).first())


@router.delete("/{documento_id}", status_code=204,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def eliminar(documento_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.get(Documento, documento_id)
    if not item:
        raise NotFoundException("Documento no encontrado")
    db.delete(item)
    db.commit()
