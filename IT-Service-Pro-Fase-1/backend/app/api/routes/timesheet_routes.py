"""Rutas REST del Timesheet: registro de horas por técnico, ticket o proyecto."""
import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db, get_current_user
from app.core.constants import RolesSistema
from app.core.exceptions import NotFoundException
from app.core.permissions import require_roles
from app.models.employee_model import Empleado
from app.models.project_model import Proyecto
from app.models.ticket_model import Ticket
from app.models.timesheet_model import RegistroTiempo
from app.models.user_model import Usuario
from app.schemas.timesheet_schema import RegistroTiempoCreate, RegistroTiempoResponse, ResumenTimesheetResponse

router = APIRouter(
    prefix="/timesheet", tags=["Timesheet"],
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR, RolesSistema.TECNICO))],
)


def _response(r: RegistroTiempo) -> RegistroTiempoResponse:
    return RegistroTiempoResponse(
        id=r.id, empleado_id=r.empleado_id, empleado_nombre=r.empleado.nombre_completo,
        ticket_id=r.ticket_id, ticket_codigo=r.ticket.codigo if r.ticket else None,
        proyecto_id=r.proyecto_id, proyecto_nombre=r.proyecto.nombre if r.proyecto else None,
        fecha=r.fecha, minutos=r.minutos, descripcion=r.descripcion, facturable=r.facturable,
    )


def _query(db: Session):
    return db.query(RegistroTiempo).options(joinedload(RegistroTiempo.empleado), joinedload(RegistroTiempo.ticket), joinedload(RegistroTiempo.proyecto))


def _propio_empleado(actor: Usuario):
    if actor.rol.nombre == RolesSistema.TECNICO:
        return actor.empleado.id if actor.empleado else None
    return None


@router.get("", response_model=list[RegistroTiempoResponse])
def listar(
    empleado_id: uuid.UUID | None = Query(None), fecha_desde: date | None = Query(None), fecha_hasta: date | None = Query(None),
    proyecto_id: uuid.UUID | None = Query(None), db: Session = Depends(get_db), actor: Usuario = Depends(get_current_user),
):
    propio = _propio_empleado(actor)
    q = _query(db)
    if propio:
        q = q.filter(RegistroTiempo.empleado_id == propio)
    elif empleado_id:
        q = q.filter(RegistroTiempo.empleado_id == empleado_id)
    if proyecto_id:
        q = q.filter(RegistroTiempo.proyecto_id == proyecto_id)
    if fecha_desde:
        q = q.filter(RegistroTiempo.fecha >= fecha_desde)
    if fecha_hasta:
        q = q.filter(RegistroTiempo.fecha <= fecha_hasta)
    return [_response(r) for r in q.order_by(RegistroTiempo.fecha.desc()).all()]


@router.get("/summary", response_model=ResumenTimesheetResponse)
def resumen(
    fecha_desde: date | None = Query(None), fecha_hasta: date | None = Query(None),
    db: Session = Depends(get_db), actor: Usuario = Depends(get_current_user),
):
    propio = _propio_empleado(actor)
    q = _query(db)
    if propio:
        q = q.filter(RegistroTiempo.empleado_id == propio)
    if fecha_desde:
        q = q.filter(RegistroTiempo.fecha >= fecha_desde)
    if fecha_hasta:
        q = q.filter(RegistroTiempo.fecha <= fecha_hasta)
    registros = q.all()
    total = sum(r.minutos for r in registros) / 60
    facturable = sum(r.minutos for r in registros if r.facturable) / 60
    por_empleado: dict[str, float] = {}
    for r in registros:
        nombre = r.empleado.nombre_completo
        por_empleado[nombre] = round(por_empleado.get(nombre, 0) + r.minutos / 60, 2)
    return ResumenTimesheetResponse(
        total_horas=round(total, 2), horas_facturables=round(facturable, 2),
        horas_no_facturables=round(total - facturable, 2), por_empleado=por_empleado,
    )


@router.post("", response_model=RegistroTiempoResponse, status_code=201)
def crear(datos: RegistroTiempoCreate, db: Session = Depends(get_db), actor: Usuario = Depends(get_current_user)):
    propio = _propio_empleado(actor)
    empleado_id = propio or datos.empleado_id
    if not empleado_id:
        raise NotFoundException("Debe indicar el técnico responsable del registro")
    if not db.get(Empleado, empleado_id):
        raise NotFoundException("Técnico no encontrado")
    if datos.ticket_id and not db.get(Ticket, datos.ticket_id):
        raise NotFoundException("Ticket no encontrado")
    if datos.proyecto_id and not db.get(Proyecto, datos.proyecto_id):
        raise NotFoundException("Proyecto no encontrado")
    item = RegistroTiempo(
        empleado_id=empleado_id, ticket_id=datos.ticket_id, proyecto_id=datos.proyecto_id,
        fecha=datos.fecha, minutos=datos.minutos, descripcion=datos.descripcion, facturable=datos.facturable,
    )
    db.add(item)
    if datos.ticket_id:
        ticket = db.get(Ticket, datos.ticket_id)
        ticket.tiempo_invertido_minutos += datos.minutos
    db.commit()
    return _response(_query(db).filter(RegistroTiempo.id == item.id).first())


@router.delete("/{registro_id}", status_code=204)
def eliminar(registro_id: uuid.UUID, db: Session = Depends(get_db), actor: Usuario = Depends(get_current_user)):
    item = db.get(RegistroTiempo, registro_id)
    if not item:
        raise NotFoundException("Registro no encontrado")
    propio = _propio_empleado(actor)
    if propio and item.empleado_id != propio:
        raise NotFoundException("Registro no encontrado")
    db.delete(item)
    db.commit()
