"""Rutas REST del CMDB: inventario de activos tecnológicos por empresa cliente."""
import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db, get_current_user
from app.core.constants import RolesSistema, TipoActivo, EstadoActivo
from app.core.exceptions import NotFoundException
from app.core.permissions import require_roles
from app.models.asset_model import Activo
from app.models.itsp_foundation_model import ContactoEmpresa, EmpresaCliente
from app.models.user_model import Usuario
from app.schemas.asset_schema import ActivoCambiarEstadoRequest, ActivoCreate, ActivoResponse, ActivoUpdate

router = APIRouter(
    prefix="/assets", tags=["CMDB"],
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR, RolesSistema.TECNICO))],
)


def _codigo(db: Session) -> str:
    total = db.query(Activo.id).count()
    candidato = total + 1
    while True:
        codigo = f"AST-{candidato:05d}"
        if not db.query(Activo.id).filter(Activo.codigo == codigo).first():
            return codigo
        candidato += 1


def _response(a: Activo) -> ActivoResponse:
    vencida = bool(a.fecha_garantia_fin and a.fecha_garantia_fin < date.today())
    return ActivoResponse(
        id=a.id, codigo=a.codigo, empresa_id=a.empresa_id,
        empresa_nombre=a.empresa.nombre_comercial or a.empresa.razon_social,
        responsable_id=a.responsable_id,
        responsable_nombre=f"{a.responsable.nombres} {a.responsable.apellidos}" if a.responsable else None,
        tipo=a.tipo, nombre=a.nombre, marca=a.marca, modelo=a.modelo, numero_serie=a.numero_serie,
        ubicacion=a.ubicacion, ip_asignada=a.ip_asignada, fecha_compra=a.fecha_compra,
        fecha_garantia_fin=a.fecha_garantia_fin, notas=a.notas, estado=a.estado,
        garantia_vencida=vencida, created_at=a.created_at, updated_at=a.updated_at,
    )


def _query(db: Session):
    return db.query(Activo).options(joinedload(Activo.empresa), joinedload(Activo.responsable))


@router.get("", response_model=list[ActivoResponse])
def listar(
    empresa_id: uuid.UUID | None = Query(None), tipo: str | None = Query(None),
    estado: str | None = Query(None), busqueda: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = _query(db).join(EmpresaCliente)
    if empresa_id:
        q = q.filter(Activo.empresa_id == empresa_id)
    if tipo:
        q = q.filter(Activo.tipo == tipo)
    if estado:
        q = q.filter(Activo.estado == estado)
    if busqueda:
        term = f"%{busqueda.strip()}%"
        q = q.filter(
            (Activo.nombre.ilike(term)) | (Activo.codigo.ilike(term)) | (Activo.numero_serie.ilike(term))
            | (EmpresaCliente.razon_social.ilike(term)) | (EmpresaCliente.nombre_comercial.ilike(term))
        )
    return [_response(a) for a in q.order_by(Activo.created_at.desc()).all()]


@router.get("/options", response_model=dict)
def opciones():
    return {"tipos": TipoActivo.TODOS, "estados": EstadoActivo.TODOS}


@router.post("", response_model=ActivoResponse, status_code=201,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def crear(datos: ActivoCreate, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    if not db.get(EmpresaCliente, datos.empresa_id):
        raise NotFoundException("Empresa no encontrada")
    if datos.responsable_id and not db.get(ContactoEmpresa, datos.responsable_id):
        raise NotFoundException("Contacto responsable no encontrado")
    item = Activo(codigo=_codigo(db), **datos.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _response(_query(db).filter(Activo.id == item.id).first())


@router.get("/{activo_id}", response_model=ActivoResponse)
def obtener(activo_id: uuid.UUID, db: Session = Depends(get_db)):
    item = _query(db).filter(Activo.id == activo_id).first()
    if not item:
        raise NotFoundException("Activo no encontrado")
    return _response(item)


@router.put("/{activo_id}", response_model=ActivoResponse,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def actualizar(activo_id: uuid.UUID, datos: ActivoUpdate, db: Session = Depends(get_db)):
    item = db.get(Activo, activo_id)
    if not item:
        raise NotFoundException("Activo no encontrado")
    if datos.responsable_id and not db.get(ContactoEmpresa, datos.responsable_id):
        raise NotFoundException("Contacto responsable no encontrado")
    for k, v in datos.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    return _response(_query(db).filter(Activo.id == activo_id).first())


@router.patch("/{activo_id}/status", response_model=ActivoResponse)
def cambiar_estado(activo_id: uuid.UUID, datos: ActivoCambiarEstadoRequest, db: Session = Depends(get_db)):
    item = db.get(Activo, activo_id)
    if not item:
        raise NotFoundException("Activo no encontrado")
    item.estado = datos.estado
    db.commit()
    return _response(_query(db).filter(Activo.id == activo_id).first())


@router.delete("/{activo_id}", status_code=204,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR))])
def eliminar(activo_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.get(Activo, activo_id)
    if not item:
        raise NotFoundException("Activo no encontrado")
    db.delete(item)
    db.commit()
