"""Rutas REST del módulo de Tickets (mesa de ayuda) para el equipo interno:
administradores, coordinadores y técnicos."""
import uuid
from datetime import timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.core.constants import CategoriaTicket, EstadoTicket, PrioridadTicket, RolesSistema
from app.core.exceptions import ForbiddenException
from app.core.permissions import require_roles
from app.models.user_model import Usuario
from app.schemas.common_schema import RespuestaExito, RespuestaMensaje, RespuestaPaginada
from app.schemas.ticket_schema import (
    ResumenTicketsResponse,
    TicketActualizarRequest,
    TicketAdjuntoCrearRequest,
    TicketAdjuntoResponse,
    TicketAsignarRequest,
    TicketCambiarEstadoRequest,
    TicketComentarioCrearRequest,
    TicketComentarioResponse,
    TicketCrearRequest,
    TicketHistorialResponse,
    TicketListItemResponse,
    TicketResponse,
    TicketTiempoRequest,
)
from app.services.ticket_service import TicketService, _ahora

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR, RolesSistema.TECNICO))],
)


def _vencido(t) -> bool:
    if t.estado not in EstadoTicket.ABIERTOS:
        return False
    limite = t.fecha_limite_resolucion
    if limite.tzinfo is None:
        limite = limite.replace(tzinfo=timezone.utc)
    return limite < _ahora()


def _list_item(t) -> TicketListItemResponse:
    return TicketListItemResponse(
        id=t.id, codigo=t.codigo, empresa_id=t.empresa_id,
        empresa_nombre=t.empresa.nombre_comercial or t.empresa.razon_social,
        contacto_id=t.contacto_id, contacto_nombre=f"{t.contacto.nombres} {t.contacto.apellidos}" if t.contacto else None,
        tecnico_id=t.asignado_a, tecnico_nombre=t.tecnico.nombre_completo if t.tecnico else None,
        titulo=t.titulo, categoria=t.categoria, prioridad=t.prioridad, estado=t.estado, canal=t.canal,
        fecha_limite_respuesta=t.fecha_limite_respuesta, fecha_limite_resolucion=t.fecha_limite_resolucion,
        fecha_primera_respuesta=t.fecha_primera_respuesta, vencido=_vencido(t),
        created_at=t.created_at, updated_at=t.updated_at,
    )


def _response(t, incluir_internos: bool = True) -> TicketResponse:
    base = _list_item(t).model_dump()
    comentarios = t.comentarios if incluir_internos else [c for c in t.comentarios if not c.es_interno]
    return TicketResponse(
        **base, descripcion=t.descripcion, servicio_id=t.servicio_id,
        servicio_nombre=t.servicio.nombre if t.servicio else None,
        horas_respuesta_sla=t.horas_respuesta_sla, horas_resolucion_sla=t.horas_resolucion_sla,
        fecha_resolucion=t.fecha_resolucion, fecha_cierre=t.fecha_cierre,
        tiempo_invertido_minutos=t.tiempo_invertido_minutos,
        calificacion_satisfaccion=t.calificacion_satisfaccion, comentario_satisfaccion=t.comentario_satisfaccion,
        motivo_cierre=t.motivo_cierre,
        comentarios=[TicketComentarioResponse.model_validate(c) for c in comentarios],
        adjuntos=[TicketAdjuntoResponse.model_validate(a) for a in t.adjuntos],
        historial=[TicketHistorialResponse.model_validate(h) for h in t.historial],
    )


def _empleado_actor(actor: Usuario):
    if actor.rol.nombre != RolesSistema.TECNICO:
        return None
    if not actor.empleado:
        raise ForbiddenException("La cuenta técnica no está vinculada a un empleado")
    return actor.empleado.id


@router.get("", response_model=RespuestaPaginada[TicketListItemResponse])
def listar(
    empresa_id: uuid.UUID | None = Query(None), contacto_id: uuid.UUID | None = Query(None),
    asignado_a: uuid.UUID | None = Query(None), estado: str | None = Query(None),
    prioridad: str | None = Query(None), categoria: str | None = Query(None),
    solo_vencidos: bool = Query(False), solo_mis_tickets: bool = Query(False),
    busqueda: str | None = Query(None), pagina: int = Query(1, ge=1), tamano_pagina: int = Query(20, ge=1, le=100),
    orden_por: str = Query("created_at"), orden_direccion: str = Query("desc", pattern="^(asc|desc)$"),
    actor: Usuario = Depends(get_current_user), db: Session = Depends(get_db),
):
    empleado_propio = _empleado_actor(actor)
    if empleado_propio and solo_mis_tickets:
        asignado_a = empleado_propio
    items, total = TicketService(db).listar(
        empresa_id=empresa_id, contacto_id=contacto_id, asignado_a=asignado_a, estado=estado,
        prioridad=prioridad, categoria=categoria, busqueda=busqueda, solo_vencidos=solo_vencidos,
        pagina=pagina, tamano_pagina=tamano_pagina, orden_por=orden_por, orden_direccion=orden_direccion,
    )
    return RespuestaPaginada.crear([_list_item(x) for x in items], total, pagina, tamano_pagina)


@router.get("/summary", response_model=RespuestaExito[ResumenTicketsResponse])
def resumen(
    solo_mis_tickets: bool = Query(False), actor: Usuario = Depends(get_current_user), db: Session = Depends(get_db),
):
    empleado_propio = _empleado_actor(actor)
    empleado_id = empleado_propio if (empleado_propio and solo_mis_tickets) else None
    return RespuestaExito(data=TicketService(db).resumen(empleado_id))


@router.get("/options", response_model=RespuestaExito[dict])
def opciones():
    return RespuestaExito(data={
        "estados": EstadoTicket.TODOS, "prioridades": PrioridadTicket.TODOS, "categorias": CategoriaTicket.TODOS,
    })


@router.post("", response_model=RespuestaExito[TicketResponse], status_code=201,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def crear(datos: TicketCrearRequest, actor: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = TicketService(db).crear(datos, actor)
    return RespuestaExito(data=_response(ticket), message=f"Ticket {ticket.codigo} creado correctamente")


@router.get("/{ticket_id}", response_model=RespuestaExito[TicketResponse])
def obtener(ticket_id: uuid.UUID, actor: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = TicketService(db)
    ticket = svc.obtener(ticket_id)
    empleado_propio = _empleado_actor(actor)
    if empleado_propio and ticket.asignado_a != empleado_propio:
        raise ForbiddenException("El técnico solo puede consultar tickets asignados a él")
    return RespuestaExito(data=_response(ticket))


@router.put("/{ticket_id}", response_model=RespuestaExito[TicketResponse],
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def actualizar(ticket_id: uuid.UUID, datos: TicketActualizarRequest,
    actor: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = TicketService(db).actualizar(ticket_id, datos, actor)
    return RespuestaExito(data=_response(ticket), message="Ticket actualizado correctamente")


@router.patch("/{ticket_id}/assign", response_model=RespuestaExito[TicketResponse],
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def asignar(ticket_id: uuid.UUID, datos: TicketAsignarRequest,
    actor: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = TicketService(db).asignar(ticket_id, datos.empleado_id, actor)
    return RespuestaExito(data=_response(ticket), message="Ticket asignado correctamente")


@router.patch("/{ticket_id}/status", response_model=RespuestaExito[TicketResponse])
def cambiar_estado(ticket_id: uuid.UUID, datos: TicketCambiarEstadoRequest,
    actor: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = TicketService(db)
    ticket = svc.obtener(ticket_id)
    empleado_propio = _empleado_actor(actor)
    if empleado_propio and ticket.asignado_a != empleado_propio:
        raise ForbiddenException("El técnico solo puede modificar tickets asignados a él")
    ticket = svc.cambiar_estado(ticket_id, datos.estado, datos.motivo_cierre, actor)
    return RespuestaExito(data=_response(ticket), message="Estado actualizado")


@router.post("/{ticket_id}/comments", response_model=RespuestaExito[TicketResponse], status_code=201)
def comentar(ticket_id: uuid.UUID, datos: TicketComentarioCrearRequest,
    actor: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = TicketService(db)
    ticket = svc.obtener(ticket_id)
    empleado_propio = _empleado_actor(actor)
    if empleado_propio and ticket.asignado_a != empleado_propio:
        raise ForbiddenException("El técnico solo puede comentar tickets asignados a él")
    ticket = svc.comentar(ticket_id, datos, actor=actor)
    return RespuestaExito(data=_response(ticket), message="Comentario agregado")


@router.post("/{ticket_id}/attachments", response_model=RespuestaExito[TicketResponse], status_code=201)
def adjuntar(ticket_id: uuid.UUID, datos: TicketAdjuntoCrearRequest,
    actor: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = TicketService(db).adjuntar(ticket_id, datos, actor=actor)
    return RespuestaExito(data=_response(ticket), message="Adjunto agregado")


@router.post("/{ticket_id}/time-log", response_model=RespuestaExito[TicketResponse])
def registrar_tiempo(ticket_id: uuid.UUID, datos: TicketTiempoRequest,
    actor: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = TicketService(db).registrar_tiempo(ticket_id, datos.minutos, datos.nota, actor)
    return RespuestaExito(data=_response(ticket), message="Tiempo registrado")


@router.delete("/{ticket_id}", response_model=RespuestaMensaje,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR))])
def eliminar(ticket_id: uuid.UUID, actor: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    TicketService(db).eliminar(ticket_id, actor)
    return RespuestaMensaje(message="Ticket eliminado correctamente")
