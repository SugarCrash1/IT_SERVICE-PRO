"""Implementación SQLAlchemy del repositorio de tickets."""
from datetime import datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.core.constants import EstadoTicket
from app.models.employee_model import Empleado
from app.models.itsp_foundation_model import ContactoEmpresa, EmpresaCliente
from app.models.ticket_model import Ticket
from app.repositories.interfaces.ticket_repository_interface import ITicketRepository
from app.utils.pagination import paginar_query


class TicketRepository(ITicketRepository):
    def __init__(self, db: Session):
        self.db = db

    def _options(self, query):
        return query.options(
            joinedload(Ticket.empresa),
            joinedload(Ticket.contacto),
            joinedload(Ticket.servicio),
            joinedload(Ticket.tecnico),
        )

    def obtener_por_id(self, ticket_id):
        return self._options(self.db.query(Ticket)).filter(Ticket.id == ticket_id).first()

    def listar(
        self,
        empresa_id=None,
        contacto_id=None,
        asignado_a=None,
        estado=None,
        estados=None,
        prioridad=None,
        categoria=None,
        busqueda=None,
        solo_vencidos=False,
        pagina=1,
        tamano_pagina=20,
        orden_por="created_at",
        orden_direccion="desc",
    ):
        query = self._options(self.db.query(Ticket)).join(EmpresaCliente).outerjoin(
            ContactoEmpresa, Ticket.contacto_id == ContactoEmpresa.id
        )
        if empresa_id:
            query = query.filter(Ticket.empresa_id == empresa_id)
        if contacto_id:
            query = query.filter(Ticket.contacto_id == contacto_id)
        if asignado_a:
            query = query.filter(Ticket.asignado_a == asignado_a)
        if estado:
            query = query.filter(Ticket.estado == estado)
        if estados:
            query = query.filter(Ticket.estado.in_(estados))
        if prioridad:
            query = query.filter(Ticket.prioridad == prioridad)
        if categoria:
            query = query.filter(Ticket.categoria == categoria)
        if solo_vencidos:
            ahora = datetime.now(timezone.utc)
            query = query.filter(
                Ticket.estado.in_(EstadoTicket.ABIERTOS),
                or_(Ticket.fecha_limite_resolucion < ahora, Ticket.fecha_limite_respuesta < ahora),
            )
        if busqueda:
            term = f"%{busqueda.strip()}%"
            query = query.filter(
                or_(
                    Ticket.codigo.ilike(term),
                    Ticket.titulo.ilike(term),
                    EmpresaCliente.razon_social.ilike(term),
                    EmpresaCliente.nombre_comercial.ilike(term),
                    ContactoEmpresa.nombres.ilike(term),
                    ContactoEmpresa.apellidos.ilike(term),
                )
            )
        return paginar_query(query, pagina, tamano_pagina, orden_por, orden_direccion, Ticket)

    def guardar(self, ticket):
        self.db.add(ticket)
        self.db.flush()
        return ticket

    def siguiente_codigo(self) -> str:
        total = self.db.query(func.count(Ticket.id)).scalar() or 0
        candidato = total + 1
        while True:
            codigo = f"TK-{candidato:06d}"
            if not self.db.query(Ticket.id).filter(Ticket.codigo == codigo).first():
                return codigo
            candidato += 1

    def resumen_por_tecnico(self, empleado_id):
        return (
            self.db.query(Ticket.estado, func.count(Ticket.id))
            .filter(Ticket.asignado_a == empleado_id)
            .group_by(Ticket.estado)
            .all()
        )
