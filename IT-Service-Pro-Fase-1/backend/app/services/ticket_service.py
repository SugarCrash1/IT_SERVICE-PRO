"""Lógica de negocio del módulo de Tickets (mesa de ayuda): cálculo de SLA,
transición de estados, asignación a técnicos, comentarios y adjuntos."""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.constants import (
    AccionAuditoria,
    EstadoGenerico,
    EstadoTicket,
    NivelSLA,
    PrioridadTicket,
)
from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException
from app.models.employee_model import Empleado
from app.models.itsp_foundation_model import ContactoEmpresa, EmpresaCliente, ServicioTI
from app.models.ticket_model import SLAPolitica, Ticket, TicketAdjunto, TicketComentario, TicketHistorial
from app.models.user_model import Usuario
from app.repositories.implementations.ticket_repository import TicketRepository
from app.services.audit_service import registrar_auditoria

# SLA por defecto (horas) si no hay política configurada para el nivel/prioridad.
SLA_DEFECTO = {
    PrioridadTicket.CRITICA: (1, 4),
    PrioridadTicket.ALTA: (2, 8),
    PrioridadTicket.MEDIA: (8, 24),
    PrioridadTicket.BAJA: (24, 72),
}

TRANSICIONES = {
    EstadoTicket.ABIERTO: {
        EstadoTicket.EN_PROGRESO, EstadoTicket.EN_ESPERA_CLIENTE,
        EstadoTicket.EN_ESPERA_TERCERO, EstadoTicket.CANCELADO,
    },
    EstadoTicket.EN_PROGRESO: {
        EstadoTicket.EN_ESPERA_CLIENTE, EstadoTicket.EN_ESPERA_TERCERO,
        EstadoTicket.RESUELTO, EstadoTicket.CANCELADO,
    },
    EstadoTicket.EN_ESPERA_CLIENTE: {EstadoTicket.EN_PROGRESO, EstadoTicket.RESUELTO, EstadoTicket.CANCELADO},
    EstadoTicket.EN_ESPERA_TERCERO: {EstadoTicket.EN_PROGRESO, EstadoTicket.RESUELTO, EstadoTicket.CANCELADO},
    EstadoTicket.RESUELTO: {EstadoTicket.CERRADO, EstadoTicket.EN_PROGRESO},
    EstadoTicket.CERRADO: set(),
    EstadoTicket.CANCELADO: set(),
}


def _ahora():
    return datetime.now(timezone.utc)


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TicketRepository(db)

    # ---- helpers de validación -------------------------------------------------

    def _empresa(self, empresa_id) -> EmpresaCliente:
        empresa = self.db.query(EmpresaCliente).filter(
            EmpresaCliente.id == empresa_id, EmpresaCliente.estado == EstadoGenerico.ACTIVO
        ).first()
        if not empresa:
            raise NotFoundException("La empresa cliente no existe o está inactiva")
        return empresa

    def _contacto(self, contacto_id, empresa_id) -> ContactoEmpresa:
        contacto = self.db.query(ContactoEmpresa).filter(ContactoEmpresa.id == contacto_id).first()
        if not contacto:
            raise NotFoundException("El contacto no existe")
        if str(contacto.empresa_id) != str(empresa_id):
            raise ValidationException("El contacto seleccionado no pertenece a la empresa indicada")
        return contacto

    def _servicio(self, servicio_id) -> ServicioTI:
        servicio = self.db.query(ServicioTI).filter(ServicioTI.id == servicio_id).first()
        if not servicio:
            raise NotFoundException("El servicio TI no existe")
        return servicio

    def _tecnico(self, empleado_id) -> Empleado:
        empleado = self.db.query(Empleado).filter(
            Empleado.id == empleado_id, Empleado.estado == EstadoGenerico.ACTIVO
        ).first()
        if not empleado:
            raise NotFoundException("El técnico no existe o está inactivo")
        return empleado

    def _calcular_sla(self, empresa: EmpresaCliente, prioridad: str):
        politica = self.db.query(SLAPolitica).filter(
            SLAPolitica.nivel_sla == empresa.nivel_sla, SLAPolitica.prioridad == prioridad
        ).first()
        if politica:
            return politica.horas_respuesta, politica.horas_resolucion
        return SLA_DEFECTO.get(prioridad, SLA_DEFECTO[PrioridadTicket.MEDIA])

    def _historial(self, ticket: Ticket, actor_nombre: str, evento: str, descripcion: str, actor_id=None):
        self.db.add(TicketHistorial(
            ticket_id=ticket.id, actor_id=actor_id, actor_nombre=actor_nombre,
            evento=evento, descripcion=descripcion,
        ))

    # ---- consultas ---------------------------------------------------------

    def listar(self, *args, **kwargs):
        return self.repo.listar(*args, **kwargs)

    def obtener(self, ticket_id) -> Ticket:
        ticket = self.repo.obtener_por_id(ticket_id)
        if not ticket:
            raise NotFoundException("El ticket solicitado no existe")
        return ticket

    def resumen(self, empleado_id=None):
        query = self.db.query(Ticket)
        if empleado_id:
            query = query.filter(Ticket.asignado_a == empleado_id)
        tickets = query.all()
        ahora = _ahora()
        por_estado = {e: 0 for e in EstadoTicket.TODOS}
        por_prioridad = {p: 0 for p in PrioridadTicket.TODOS}
        vencidos = 0
        sin_asignar = 0
        resueltos_mes = 0
        tiempos = []
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        for t in tickets:
            por_estado[t.estado] = por_estado.get(t.estado, 0) + 1
            por_prioridad[t.prioridad] = por_prioridad.get(t.prioridad, 0) + 1
            if not t.asignado_a and t.estado in EstadoTicket.ABIERTOS:
                sin_asignar += 1
            if t.estado in EstadoTicket.ABIERTOS and (
                t.fecha_limite_resolucion.replace(tzinfo=timezone.utc) < ahora
                if t.fecha_limite_resolucion.tzinfo is None else t.fecha_limite_resolucion < ahora
            ):
                vencidos += 1
            if t.fecha_resolucion:
                fecha_res = t.fecha_resolucion.replace(tzinfo=timezone.utc) if t.fecha_resolucion.tzinfo is None else t.fecha_resolucion
                if fecha_res >= inicio_mes:
                    resueltos_mes += 1
                creado = t.created_at.replace(tzinfo=timezone.utc) if t.created_at.tzinfo is None else t.created_at
                tiempos.append((fecha_res - creado).total_seconds() / 3600)
        promedio = round(sum(tiempos) / len(tiempos), 1) if tiempos else None
        return {
            "total": len(tickets), "por_estado": por_estado, "por_prioridad": por_prioridad,
            "vencidos": vencidos, "sin_asignar": sin_asignar, "resueltos_mes": resueltos_mes,
            "tiempo_promedio_resolucion_horas": promedio,
        }

    # ---- comandos ------------------------------------------------------------

    def crear(self, datos, actor: Usuario | None) -> Ticket:
        empresa = self._empresa(datos.empresa_id)
        contacto = self._contacto(datos.contacto_id, empresa.id) if datos.contacto_id else None
        servicio = self._servicio(datos.servicio_id) if datos.servicio_id else None
        tecnico = self._tecnico(datos.asignado_a) if datos.asignado_a else None
        horas_resp, horas_res = self._calcular_sla(empresa, datos.prioridad)
        ahora = _ahora()
        ticket = Ticket(
            codigo=self.repo.siguiente_codigo(), empresa_id=empresa.id,
            contacto_id=contacto.id if contacto else None, servicio_id=servicio.id if servicio else None,
            asignado_a=tecnico.id if tecnico else None, titulo=datos.titulo, descripcion=datos.descripcion,
            categoria=datos.categoria, prioridad=datos.prioridad, canal=datos.canal,
            estado=EstadoTicket.ABIERTO, horas_respuesta_sla=horas_resp, horas_resolucion_sla=horas_res,
            fecha_limite_respuesta=ahora + timedelta(hours=horas_resp),
            fecha_limite_resolucion=ahora + timedelta(hours=horas_res),
            created_by=actor.id if actor else None, updated_by=actor.id if actor else None,
        )
        self.repo.guardar(ticket)
        self._historial(ticket, actor.nombre_completo if actor else "Sistema", "CREACION",
                         f"Ticket creado con prioridad {datos.prioridad}", actor.id if actor else None)
        if tecnico:
            self._historial(ticket, actor.nombre_completo if actor else "Sistema", "ASIGNACION",
                             f"Asignado a {tecnico.nombre_completo}", actor.id if actor else None)
        registrar_auditoria(self.db, actor.id if actor else None, AccionAuditoria.CREAR, "TICKETS",
                             "Ticket", str(ticket.id), valor_nuevo={"codigo": ticket.codigo, "prioridad": ticket.prioridad})
        self.db.commit()
        return self.obtener(ticket.id)

    def crear_desde_portal(self, datos, contacto: ContactoEmpresa) -> Ticket:
        if not contacto.puede_crear_tickets:
            raise ForbiddenException("Este contacto no está habilitado para crear tickets")
        empresa = self._empresa(contacto.empresa_id)
        servicio = self._servicio(datos.servicio_id) if datos.servicio_id else None
        horas_resp, horas_res = self._calcular_sla(empresa, datos.prioridad)
        ahora = _ahora()
        ticket = Ticket(
            codigo=self.repo.siguiente_codigo(), empresa_id=empresa.id, contacto_id=contacto.id,
            servicio_id=servicio.id if servicio else None, titulo=datos.titulo, descripcion=datos.descripcion,
            categoria=datos.categoria, prioridad=datos.prioridad, canal="PORTAL", estado=EstadoTicket.ABIERTO,
            horas_respuesta_sla=horas_resp, horas_resolucion_sla=horas_res,
            fecha_limite_respuesta=ahora + timedelta(hours=horas_resp),
            fecha_limite_resolucion=ahora + timedelta(hours=horas_res),
        )
        self.repo.guardar(ticket)
        self._historial(ticket, f"{contacto.nombres} {contacto.apellidos}", "CREACION",
                         f"Ticket creado desde el portal empresarial con prioridad {datos.prioridad}")
        registrar_auditoria(self.db, None, AccionAuditoria.CREAR, "TICKETS", "Ticket", str(ticket.id),
                             valor_nuevo={"codigo": ticket.codigo, "origen": "portal"})
        self.db.commit()
        return self.obtener(ticket.id)

    def actualizar(self, ticket_id, datos, actor: Usuario) -> Ticket:
        ticket = self.obtener(ticket_id)
        if ticket.estado in EstadoTicket.FINALES:
            raise ConflictException("No se puede editar un ticket cerrado o cancelado")
        cambios = datos.model_dump(exclude_unset=True)
        recalcular_sla = "prioridad" in cambios and cambios["prioridad"] != ticket.prioridad
        if "servicio_id" in cambios and cambios["servicio_id"]:
            self._servicio(cambios["servicio_id"])
        for campo in ("titulo", "descripcion", "servicio_id", "categoria", "prioridad"):
            if campo in cambios:
                setattr(ticket, campo, cambios[campo])
        if recalcular_sla:
            empresa = self._empresa(ticket.empresa_id)
            horas_resp, horas_res = self._calcular_sla(empresa, ticket.prioridad)
            ticket.horas_respuesta_sla, ticket.horas_resolucion_sla = horas_resp, horas_res
            base = ticket.created_at
            ticket.fecha_limite_respuesta = base + timedelta(hours=horas_resp)
            ticket.fecha_limite_resolucion = base + timedelta(hours=horas_res)
            self._historial(ticket, actor.nombre_completo, "PRIORIDAD",
                             f"Prioridad actualizada a {ticket.prioridad}, SLA recalculado", actor.id)
        ticket.updated_by = actor.id
        registrar_auditoria(self.db, actor.id, AccionAuditoria.EDITAR, "TICKETS", "Ticket", str(ticket.id), valor_nuevo=cambios)
        self.db.commit()
        return self.obtener(ticket.id)

    def asignar(self, ticket_id, empleado_id, actor: Usuario) -> Ticket:
        ticket = self.obtener(ticket_id)
        if ticket.estado in EstadoTicket.FINALES:
            raise ConflictException("No se puede reasignar un ticket cerrado o cancelado")
        tecnico = self._tecnico(empleado_id)
        ticket.asignado_a = tecnico.id
        ticket.updated_by = actor.id
        if ticket.estado == EstadoTicket.ABIERTO:
            ticket.estado = EstadoTicket.EN_PROGRESO
        self._historial(ticket, actor.nombre_completo, "ASIGNACION", f"Asignado a {tecnico.nombre_completo}", actor.id)
        registrar_auditoria(self.db, actor.id, AccionAuditoria.EDITAR, "TICKETS", "Ticket", str(ticket.id),
                             valor_nuevo={"asignado_a": str(tecnico.id)})
        self.db.commit()
        return self.obtener(ticket.id)

    def cambiar_estado(self, ticket_id, estado, motivo_cierre, actor: Usuario) -> Ticket:
        ticket = self.obtener(ticket_id)
        if estado == ticket.estado:
            return ticket
        if estado not in TRANSICIONES.get(ticket.estado, set()):
            raise ConflictException(f"No se puede cambiar un ticket de {ticket.estado} a {estado}")
        if estado == EstadoTicket.CANCELADO and not motivo_cierre:
            raise ValidationException("Debe indicar el motivo de cancelación")
        anterior = ticket.estado
        ahora = _ahora()
        ticket.estado = estado
        ticket.updated_by = actor.id
        if estado == EstadoTicket.EN_PROGRESO and not ticket.fecha_primera_respuesta:
            ticket.fecha_primera_respuesta = ahora
        if estado == EstadoTicket.RESUELTO:
            ticket.fecha_resolucion = ahora
        if estado == EstadoTicket.CERRADO:
            ticket.fecha_cierre = ahora
        if estado in (EstadoTicket.CANCELADO, EstadoTicket.CERRADO) and motivo_cierre:
            ticket.motivo_cierre = motivo_cierre
        accion = AccionAuditoria.CANCELAR if estado == EstadoTicket.CANCELADO else AccionAuditoria.EDITAR
        self._historial(ticket, actor.nombre_completo, "ESTADO", f"Estado cambiado de {anterior} a {estado}", actor.id)
        registrar_auditoria(self.db, actor.id, accion, "TICKETS", "Ticket", str(ticket.id),
                             {"estado": anterior}, {"estado": estado})
        self.db.commit()
        return self.obtener(ticket.id)

    def comentar(self, ticket_id, datos, actor: Usuario | None = None, contacto: ContactoEmpresa | None = None) -> Ticket:
        ticket = self.obtener(ticket_id)
        if ticket.estado in (EstadoTicket.CERRADO, EstadoTicket.CANCELADO):
            raise ConflictException("No se puede comentar un ticket cerrado o cancelado")
        es_del_cliente = contacto is not None
        autor_nombre = f"{contacto.nombres} {contacto.apellidos}" if contacto else actor.nombre_completo
        comentario = TicketComentario(
            ticket_id=ticket.id, autor_usuario_id=actor.id if actor else None, autor_nombre=autor_nombre,
            contenido=datos.contenido, es_interno=False if es_del_cliente else datos.es_interno,
            es_del_cliente=es_del_cliente,
        )
        self.db.add(comentario)
        self.db.flush()
        if es_del_cliente and ticket.estado == EstadoTicket.EN_ESPERA_CLIENTE:
            ticket.estado = EstadoTicket.EN_PROGRESO
            self._historial(ticket, autor_nombre, "ESTADO", "El cliente respondió: vuelve a EN_PROGRESO")
        elif not es_del_cliente and not datos.es_interno and not ticket.fecha_primera_respuesta:
            ticket.fecha_primera_respuesta = _ahora()
            self._historial(ticket, autor_nombre, "PRIMERA_RESPUESTA", "Primera respuesta registrada", actor.id if actor else None)
        self._historial(ticket, autor_nombre, "COMENTARIO",
                         "Nota interna agregada" if comentario.es_interno else "Comentario agregado",
                         actor.id if actor else None)
        registrar_auditoria(self.db, actor.id if actor else None, AccionAuditoria.EDITAR, "TICKETS",
                             "TicketComentario", str(comentario.id))
        self.db.commit()
        return self.obtener(ticket.id)

    def adjuntar(self, ticket_id, datos, actor: Usuario | None = None) -> Ticket:
        ticket = self.obtener(ticket_id)
        adjunto = TicketAdjunto(
            ticket_id=ticket.id, comentario_id=datos.comentario_id, nombre_archivo=datos.nombre_archivo,
            url_archivo=datos.url_archivo, tipo_mime=datos.tipo_mime, tamano_bytes=datos.tamano_bytes,
            subido_por_id=actor.id if actor else None,
        )
        self.db.add(adjunto)
        self._historial(ticket, actor.nombre_completo if actor else "Cliente", "ADJUNTO",
                         f"Archivo adjuntado: {datos.nombre_archivo}", actor.id if actor else None)
        self.db.commit()
        return self.obtener(ticket.id)

    def registrar_tiempo(self, ticket_id, minutos, nota, actor: Usuario) -> Ticket:
        ticket = self.obtener(ticket_id)
        ticket.tiempo_invertido_minutos += minutos
        ticket.updated_by = actor.id
        descripcion = f"{minutos} min registrados" + (f" — {nota}" if nota else "")
        self._historial(ticket, actor.nombre_completo, "TIEMPO", descripcion, actor.id)
        self.db.commit()
        return self.obtener(ticket.id)

    def calificar(self, ticket_id, datos, contacto: ContactoEmpresa) -> Ticket:
        ticket = self.obtener(ticket_id)
        if str(ticket.empresa_id) != str(contacto.empresa_id):
            raise ForbiddenException("No puede calificar un ticket de otra empresa")
        if ticket.estado not in (EstadoTicket.RESUELTO, EstadoTicket.CERRADO):
            raise ConflictException("Solo se puede calificar un ticket resuelto o cerrado")
        ticket.calificacion_satisfaccion = datos.calificacion
        ticket.comentario_satisfaccion = datos.comentario
        self._historial(ticket, f"{contacto.nombres} {contacto.apellidos}", "SATISFACCION",
                         f"Calificación registrada: {datos.calificacion}/5")
        self.db.commit()
        return self.obtener(ticket.id)

    def eliminar(self, ticket_id, actor: Usuario):
        ticket = self.obtener(ticket_id)
        self.db.delete(ticket)
        registrar_auditoria(self.db, actor.id, AccionAuditoria.ELIMINAR, "TICKETS", "Ticket", str(ticket_id))
        self.db.commit()
