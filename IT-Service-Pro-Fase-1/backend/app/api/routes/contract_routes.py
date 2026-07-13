"""Rutas REST del módulo de Contratos."""
import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db
from app.core.constants import EstadoContrato, RolesSistema, TipoContrato
from app.core.exceptions import NotFoundException
from app.core.permissions import require_roles
from app.models.contract_model import Contrato
from app.models.itsp_foundation_model import EmpresaCliente
from app.schemas.contract_schema import ContratoCreate, ContratoResponse, ContratoUpdate

router = APIRouter(
    prefix="/contracts", tags=["Contratos"],
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))],
)


def _codigo(db: Session) -> str:
    total = db.query(Contrato.id).count()
    candidato = total + 1
    while True:
        codigo = f"CTR-{candidato:04d}"
        if not db.query(Contrato.id).filter(Contrato.codigo == codigo).first():
            return codigo
        candidato += 1


def _response(c: Contrato) -> ContratoResponse:
    dias = (c.fecha_fin - date.today()).days if c.fecha_fin else None
    return ContratoResponse(
        id=c.id, codigo=c.codigo, empresa_id=c.empresa_id,
        empresa_nombre=c.empresa.nombre_comercial or c.empresa.razon_social,
        nombre=c.nombre, tipo=c.tipo, fecha_inicio=c.fecha_inicio, fecha_fin=c.fecha_fin,
        horas_incluidas_mes=c.horas_incluidas_mes, horas_consumidas_mes=c.horas_consumidas_mes,
        valor_mensual=float(c.valor_mensual) if c.valor_mensual else None, estado=c.estado,
        notas=c.notas, dias_para_vencer=dias, created_at=c.created_at,
    )


def _query(db: Session):
    return db.query(Contrato).options(joinedload(Contrato.empresa))


@router.get("", response_model=list[ContratoResponse])
def listar(empresa_id: uuid.UUID | None = Query(None), estado: str | None = Query(None), db: Session = Depends(get_db)):
    q = _query(db)
    if empresa_id:
        q = q.filter(Contrato.empresa_id == empresa_id)
    if estado:
        q = q.filter(Contrato.estado == estado)
    return [_response(c) for c in q.order_by(Contrato.created_at.desc()).all()]


@router.get("/options", response_model=dict)
def opciones():
    return {"tipos": TipoContrato.TODOS, "estados": EstadoContrato.TODOS}


@router.post("", response_model=ContratoResponse, status_code=201)
def crear(datos: ContratoCreate, db: Session = Depends(get_db)):
    if not db.get(EmpresaCliente, datos.empresa_id):
        raise NotFoundException("Empresa no encontrada")
    item = Contrato(codigo=_codigo(db), **datos.model_dump())
    db.add(item)
    db.commit()
    return _response(_query(db).filter(Contrato.id == item.id).first())


@router.get("/{contrato_id}", response_model=ContratoResponse)
def obtener(contrato_id: uuid.UUID, db: Session = Depends(get_db)):
    item = _query(db).filter(Contrato.id == contrato_id).first()
    if not item:
        raise NotFoundException("Contrato no encontrado")
    return _response(item)


@router.put("/{contrato_id}", response_model=ContratoResponse)
def actualizar(contrato_id: uuid.UUID, datos: ContratoUpdate, db: Session = Depends(get_db)):
    item = db.get(Contrato, contrato_id)
    if not item:
        raise NotFoundException("Contrato no encontrado")
    for k, v in datos.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    return _response(_query(db).filter(Contrato.id == contrato_id).first())


@router.delete("/{contrato_id}", status_code=204, dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR))])
def eliminar(contrato_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.get(Contrato, contrato_id)
    if not item:
        raise NotFoundException("Contrato no encontrado")
    db.delete(item)
    db.commit()
