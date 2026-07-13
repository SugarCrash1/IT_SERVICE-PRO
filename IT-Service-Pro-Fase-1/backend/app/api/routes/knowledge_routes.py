"""Rutas REST de la Base de Conocimiento."""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db, get_current_user
from app.core.constants import RolesSistema
from app.core.exceptions import NotFoundException
from app.core.permissions import require_roles
from app.models.itsp_foundation_model import ServicioTI
from app.models.knowledge_model import ArticuloConocimiento
from app.models.user_model import Usuario
from app.schemas.knowledge_schema import ArticuloCreate, ArticuloResponse, ArticuloUpdate

router = APIRouter(
    prefix="/knowledge", tags=["Base de conocimiento"],
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR, RolesSistema.TECNICO))],
)


def _response(a: ArticuloConocimiento) -> ArticuloResponse:
    return ArticuloResponse(
        id=a.id, titulo=a.titulo, contenido=a.contenido, categoria=a.categoria, servicio_id=a.servicio_id,
        servicio_nombre=a.servicio.nombre if a.servicio else None,
        autor_nombre=a.autor.nombre_completo if a.autor else None, publicado=a.publicado, vistas=a.vistas,
        created_at=a.created_at, updated_at=a.updated_at,
    )


def _query(db: Session):
    return db.query(ArticuloConocimiento).options(joinedload(ArticuloConocimiento.servicio), joinedload(ArticuloConocimiento.autor))


@router.get("", response_model=list[ArticuloResponse])
def listar(categoria: str | None = Query(None), busqueda: str | None = Query(None), db: Session = Depends(get_db)):
    q = _query(db)
    if categoria:
        q = q.filter(ArticuloConocimiento.categoria == categoria)
    if busqueda:
        term = f"%{busqueda.strip()}%"
        q = q.filter((ArticuloConocimiento.titulo.ilike(term)) | (ArticuloConocimiento.contenido.ilike(term)))
    return [_response(a) for a in q.order_by(ArticuloConocimiento.updated_at.desc()).all()]


@router.post("", response_model=ArticuloResponse, status_code=201)
def crear(datos: ArticuloCreate, db: Session = Depends(get_db), actor: Usuario = Depends(get_current_user)):
    if datos.servicio_id and not db.get(ServicioTI, datos.servicio_id):
        raise NotFoundException("Servicio TI no encontrado")
    item = ArticuloConocimiento(autor_id=actor.id, **datos.model_dump())
    db.add(item)
    db.commit()
    return _response(_query(db).filter(ArticuloConocimiento.id == item.id).first())


@router.get("/{articulo_id}", response_model=ArticuloResponse)
def obtener(articulo_id: uuid.UUID, db: Session = Depends(get_db)):
    item = _query(db).filter(ArticuloConocimiento.id == articulo_id).first()
    if not item:
        raise NotFoundException("Artículo no encontrado")
    item.vistas += 1
    db.commit()
    return _response(item)


@router.put("/{articulo_id}", response_model=ArticuloResponse)
def actualizar(articulo_id: uuid.UUID, datos: ArticuloUpdate, db: Session = Depends(get_db)):
    item = db.get(ArticuloConocimiento, articulo_id)
    if not item:
        raise NotFoundException("Artículo no encontrado")
    for k, v in datos.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    return _response(_query(db).filter(ArticuloConocimiento.id == articulo_id).first())


@router.delete("/{articulo_id}", status_code=204)
def eliminar(articulo_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.get(ArticuloConocimiento, articulo_id)
    if not item:
        raise NotFoundException("Artículo no encontrado")
    db.delete(item)
    db.commit()
