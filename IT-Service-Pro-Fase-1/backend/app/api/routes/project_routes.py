"""Rutas REST del módulo de Proyectos."""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db
from app.core.constants import EstadoProyecto, EstadoTareaProyecto, RolesSistema
from app.core.exceptions import NotFoundException
from app.core.permissions import require_roles
from app.models.employee_model import Empleado
from app.models.itsp_foundation_model import EmpresaCliente
from app.models.project_model import Proyecto, ProyectoTarea
from app.schemas.project_schema import (
    ProyectoCreate, ProyectoResponse, ProyectoUpdate, TareaCreate, TareaResponse, TareaUpdate,
)

router = APIRouter(
    prefix="/projects", tags=["Proyectos"],
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR, RolesSistema.TECNICO))],
)


def _codigo(db: Session) -> str:
    total = db.query(Proyecto.id).count()
    candidato = total + 1
    while True:
        codigo = f"PRY-{candidato:04d}"
        if not db.query(Proyecto.id).filter(Proyecto.codigo == codigo).first():
            return codigo
        candidato += 1


def _tarea_response(t: ProyectoTarea) -> TareaResponse:
    return TareaResponse(
        id=t.id, proyecto_id=t.proyecto_id, titulo=t.titulo, estado=t.estado, responsable_id=t.responsable_id,
        responsable_nombre=t.responsable.nombre_completo if t.responsable else None,
        fecha_limite=t.fecha_limite, created_at=t.created_at,
    )


def _response(p: Proyecto) -> ProyectoResponse:
    total = len(p.tareas)
    completadas = sum(1 for t in p.tareas if t.estado == EstadoTareaProyecto.COMPLETADA)
    return ProyectoResponse(
        id=p.id, codigo=p.codigo, empresa_id=p.empresa_id,
        empresa_nombre=p.empresa.nombre_comercial or p.empresa.razon_social,
        responsable_id=p.responsable_id, responsable_nombre=p.responsable.nombre_completo if p.responsable else None,
        nombre=p.nombre, descripcion=p.descripcion, estado=p.estado, fecha_inicio=p.fecha_inicio,
        fecha_fin_estimada=p.fecha_fin_estimada, fecha_fin_real=p.fecha_fin_real, presupuesto=float(p.presupuesto) if p.presupuesto else None,
        avance_porcentaje=p.avance_porcentaje, total_tareas=total, tareas_completadas=completadas,
        created_at=p.created_at, updated_at=p.updated_at, tareas=[_tarea_response(t) for t in p.tareas],
    )


def _query(db: Session):
    return db.query(Proyecto).options(joinedload(Proyecto.empresa), joinedload(Proyecto.responsable), joinedload(Proyecto.tareas).joinedload(ProyectoTarea.responsable))


@router.get("", response_model=list[ProyectoResponse])
def listar(empresa_id: uuid.UUID | None = Query(None), estado: str | None = Query(None), db: Session = Depends(get_db)):
    q = _query(db)
    if empresa_id:
        q = q.filter(Proyecto.empresa_id == empresa_id)
    if estado:
        q = q.filter(Proyecto.estado == estado)
    return [_response(p) for p in q.order_by(Proyecto.created_at.desc()).all()]


@router.get("/options", response_model=dict)
def opciones():
    return {"estados": EstadoProyecto.TODOS, "estados_tarea": EstadoTareaProyecto.TODOS}


@router.post("", response_model=ProyectoResponse, status_code=201,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def crear(datos: ProyectoCreate, db: Session = Depends(get_db)):
    if not db.get(EmpresaCliente, datos.empresa_id):
        raise NotFoundException("Empresa no encontrada")
    if datos.responsable_id and not db.get(Empleado, datos.responsable_id):
        raise NotFoundException("Responsable no encontrado")
    item = Proyecto(codigo=_codigo(db), **datos.model_dump())
    db.add(item)
    db.commit()
    return _response(_query(db).filter(Proyecto.id == item.id).first())


@router.get("/{proyecto_id}", response_model=ProyectoResponse)
def obtener(proyecto_id: uuid.UUID, db: Session = Depends(get_db)):
    item = _query(db).filter(Proyecto.id == proyecto_id).first()
    if not item:
        raise NotFoundException("Proyecto no encontrado")
    return _response(item)


@router.put("/{proyecto_id}", response_model=ProyectoResponse,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def actualizar(proyecto_id: uuid.UUID, datos: ProyectoUpdate, db: Session = Depends(get_db)):
    item = db.get(Proyecto, proyecto_id)
    if not item:
        raise NotFoundException("Proyecto no encontrado")
    for k, v in datos.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    return _response(_query(db).filter(Proyecto.id == proyecto_id).first())


@router.delete("/{proyecto_id}", status_code=204, dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR))])
def eliminar(proyecto_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.get(Proyecto, proyecto_id)
    if not item:
        raise NotFoundException("Proyecto no encontrado")
    db.delete(item)
    db.commit()


@router.post("/{proyecto_id}/tasks", response_model=ProyectoResponse, status_code=201)
def crear_tarea(proyecto_id: uuid.UUID, datos: TareaCreate, db: Session = Depends(get_db)):
    proyecto = db.get(Proyecto, proyecto_id)
    if not proyecto:
        raise NotFoundException("Proyecto no encontrado")
    if datos.responsable_id and not db.get(Empleado, datos.responsable_id):
        raise NotFoundException("Responsable no encontrado")
    db.add(ProyectoTarea(proyecto_id=proyecto_id, **datos.model_dump()))
    db.commit()
    return _response(_query(db).filter(Proyecto.id == proyecto_id).first())


@router.put("/{proyecto_id}/tasks/{tarea_id}", response_model=ProyectoResponse)
def actualizar_tarea(proyecto_id: uuid.UUID, tarea_id: uuid.UUID, datos: TareaUpdate, db: Session = Depends(get_db)):
    tarea = db.query(ProyectoTarea).filter(ProyectoTarea.id == tarea_id, ProyectoTarea.proyecto_id == proyecto_id).first()
    if not tarea:
        raise NotFoundException("Tarea no encontrada")
    for k, v in datos.model_dump(exclude_unset=True).items():
        setattr(tarea, k, v)
    db.commit()
    return _response(_query(db).filter(Proyecto.id == proyecto_id).first())


@router.delete("/{proyecto_id}/tasks/{tarea_id}", response_model=ProyectoResponse)
def eliminar_tarea(proyecto_id: uuid.UUID, tarea_id: uuid.UUID, db: Session = Depends(get_db)):
    tarea = db.query(ProyectoTarea).filter(ProyectoTarea.id == tarea_id, ProyectoTarea.proyecto_id == proyecto_id).first()
    if not tarea:
        raise NotFoundException("Tarea no encontrada")
    db.delete(tarea)
    db.commit()
    return _response(_query(db).filter(Proyecto.id == proyecto_id).first())
