"""Datos de ejemplo del módulo de Tickets: vincula al técnico con un
registro de Empleado, crea un usuario de portal para un contacto de empresa
y genera tickets de muestra en distintos estados y prioridades."""
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.constants import CanalTicket, CategoriaTicket, EstadoTicket, PrioridadTicket, RolesSistema
from app.core.security import hash_password
from app.models.employee_model import Empleado
from app.models.itsp_foundation_model import ContactoEmpresa, EmpresaCliente, ServicioTI
from app.models.role_model import Rol
from app.models.ticket_model import Ticket, TicketComentario, TicketHistorial
from app.models.user_model import Usuario
from app.services.ticket_service import TicketService
from app.schemas.ticket_schema import TicketCrearRequest


def seed_tickets(db: Session) -> None:
    # 1) Vincular al usuario técnico sembrado en admin_seed con un Empleado real,
    #    necesario para poder asignarle tickets.
    usuario_tecnico = db.query(Usuario).filter(Usuario.correo == "tecnico@itservicepro.com").first()
    empleado_tecnico = None
    if usuario_tecnico:
        empleado_tecnico = db.query(Empleado).filter(Empleado.usuario_id == usuario_tecnico.id).first()
        if not empleado_tecnico:
            empleado_tecnico = Empleado(
                usuario_id=usuario_tecnico.id, nombres="Técnico de", apellidos="Soporte",
                documento="TEC-000001", correo=usuario_tecnico.correo, cargo="Técnico de Soporte TI",
                especialidad="Soporte nivel 2, redes y Microsoft 365", fecha_ingreso=date.today(),
            )
            db.add(empleado_tecnico)
            db.flush()

    # 2) Crear un segundo técnico de ejemplo, para poder mostrar reasignación en la UI.
    segundo_tecnico = db.query(Empleado).filter(Empleado.documento == "TEC-000002").first()
    if not segundo_tecnico:
        rol_tecnico = db.query(Rol).filter(Rol.nombre == RolesSistema.TECNICO).first()
        usuario2 = db.query(Usuario).filter(Usuario.correo == "tecnico2@itservicepro.com").first()
        if not usuario2 and rol_tecnico:
            usuario2 = Usuario(
                nombre_completo="Renzo Salazar", correo="tecnico2@itservicepro.com",
                password_hash=hash_password("Tecnico123*"), rol_id=rol_tecnico.id,
            )
            db.add(usuario2)
            db.flush()
        segundo_tecnico = Empleado(
            usuario_id=usuario2.id if usuario2 else None, nombres="Renzo", apellidos="Salazar",
            documento="TEC-000002", correo="tecnico2@itservicepro.com", cargo="Técnico de Soporte TI",
            especialidad="Cloud, Azure y ciberseguridad", fecha_ingreso=date.today(),
        )
        db.add(segundo_tecnico)
        db.flush()

    # 3) Crear un usuario de portal para el contacto principal de la primera empresa,
    #    para poder probar el flujo completo "cliente crea ticket -> técnico responde".
    primer_contacto = db.query(ContactoEmpresa).filter(ContactoEmpresa.es_contacto_principal.is_(True)).order_by(ContactoEmpresa.created_at).first()
    if primer_contacto:
        ya_vinculado = db.query(Usuario).filter(Usuario.contacto_empresa_id == primer_contacto.id).first()
        if not ya_vinculado:
            rol_cliente = db.query(Rol).filter(Rol.nombre == RolesSistema.CLIENTE).first()
            correo_portal = primer_contacto.correo
            if rol_cliente and not db.query(Usuario).filter(Usuario.correo == correo_portal).first():
                db.add(Usuario(
                    nombre_completo=f"{primer_contacto.nombres} {primer_contacto.apellidos}",
                    correo=correo_portal, password_hash=hash_password("Portal123*"),
                    rol_id=rol_cliente.id, contacto_empresa_id=primer_contacto.id,
                ))
                db.flush()

    db.commit()

    empresas = db.query(EmpresaCliente).order_by(EmpresaCliente.created_at).all()
    servicios = db.query(ServicioTI).all()
    if not empresas:
        return

    # 5) Activos de ejemplo (CMDB), uno por empresa. Independiente de los
    #    tickets: corre incluso si ya habías sembrado tickets antes.
    from app.models.asset_model import Activo
    from app.core.constants import TipoActivo, EstadoActivo
    if db.query(Activo).count() == 0:
        contactos_por_empresa = {c.empresa_id: c for c in db.query(ContactoEmpresa).all()}
        ejemplos_activos = [
            (TipoActivo.SERVIDOR, "Servidor de aplicaciones SRV-APP01", "Dell", "PowerEdge R450",
             date.today() - timedelta(days=400), date.today() + timedelta(days=330)),
            (TipoActivo.LAPTOP, "Laptop Jefatura de TI", "Lenovo", "ThinkPad T14",
             date.today() - timedelta(days=200), date.today() + timedelta(days=530)),
            (TipoActivo.LICENCIA, "Licencias Microsoft 365 E3 (25 usuarios)", "Microsoft", "M365 E3",
             date.today() - timedelta(days=90), date.today() + timedelta(days=275)),
            (TipoActivo.RED, "Firewall perimetral", "Fortinet", "FortiGate 60F",
             date.today() - timedelta(days=600), date.today() - timedelta(days=20)),
        ]
        for i, empresa in enumerate(empresas):
            tipo, nombre, marca, modelo, f_compra, f_garantia = ejemplos_activos[i % len(ejemplos_activos)]
            contacto = contactos_por_empresa.get(empresa.id)
            db.add(Activo(
                codigo=f"AST-{i + 1:05d}", empresa_id=empresa.id, responsable_id=contacto.id if contacto else None,
                tipo=tipo, nombre=nombre, marca=marca, modelo=modelo, numero_serie=f"SN-{1000 + i}",
                ubicacion="Sede principal", fecha_compra=f_compra, fecha_garantia_fin=f_garantia,
                estado=EstadoActivo.ACTIVO,
            ))
        db.commit()

    # 6) Tickets de muestra, en distintos estados y prioridades (solo la primera vez).
    if db.query(Ticket).count() > 0:
        return
    svc = TicketService(db)
    ejemplos = [
        (0, PrioridadTicket.CRITICA, CategoriaTicket.INCIDENTE, "Servidor de correo caído",
         "Los usuarios no pueden enviar ni recibir correos desde las 8:00 a.m. Impacta a toda la sede principal.",
         EstadoTicket.EN_PROGRESO, empleado_tecnico),
        (0, PrioridadTicket.MEDIA, CategoriaTicket.REQUERIMIENTO, "Alta de nuevo colaborador",
         "Se necesita crear usuario de red, correo y accesos a Microsoft 365 para un nuevo ingreso el lunes.",
         EstadoTicket.ABIERTO, None),
        (1, PrioridadTicket.ALTA, CategoriaTicket.INCIDENTE, "Lentitud en sistema de historias clínicas",
         "El sistema tarda más de 30 segundos en cargar el historial de cada paciente desde ayer por la tarde.",
         EstadoTicket.EN_ESPERA_TERCERO, segundo_tecnico),
        (1, PrioridadTicket.BAJA, CategoriaTicket.CONSULTA, "Consulta sobre licencias disponibles",
         "¿Cuántas licencias de Microsoft 365 E3 nos quedan disponibles para asignar este trimestre?",
         EstadoTicket.RESUELTO, empleado_tecnico),
        (2, PrioridadTicket.MEDIA, CategoriaTicket.PROBLEMA, "Caídas intermitentes de Wi-Fi en almacén",
         "La señal Wi-Fi del almacén se cae varias veces al día, afectando el escaneo de guías de despacho.",
         EstadoTicket.ABIERTO, None),
    ]
    for idx, prioridad, categoria, titulo, descripcion, estado_objetivo, tecnico in ejemplos:
        if idx >= len(empresas):
            continue
        empresa = empresas[idx]
        contacto = db.query(ContactoEmpresa).filter(ContactoEmpresa.empresa_id == empresa.id).first()
        servicio = servicios[idx % len(servicios)] if servicios else None
        datos = TicketCrearRequest(
            empresa_id=empresa.id, contacto_id=contacto.id if contacto else None,
            servicio_id=servicio.id if servicio else None, titulo=titulo, descripcion=descripcion,
            categoria=categoria, prioridad=prioridad, canal=CanalTicket.PORTAL,
            asignado_a=tecnico.id if tecnico else None,
        )
        ticket = svc.crear(datos, actor=None)
        if estado_objetivo != ticket.estado:
            db.query(Ticket).filter(Ticket.id == ticket.id).update({"estado": estado_objetivo})
            if estado_objetivo == EstadoTicket.RESUELTO:
                db.query(Ticket).filter(Ticket.id == ticket.id).update({"fecha_resolucion": ticket.created_at + timedelta(hours=6)})
            db.add(TicketHistorial(
                ticket_id=ticket.id, actor_nombre="Sistema (datos de ejemplo)", evento="ESTADO",
                descripcion=f"Estado de ejemplo establecido a {estado_objetivo}",
            ))
        if contacto:
            db.add(TicketComentario(
                ticket_id=ticket.id, autor_nombre=f"{contacto.nombres} {contacto.apellidos}",
                contenido="Quedamos atentos a la actualización, gracias por la pronta atención.",
                es_del_cliente=True,
            ))
        if tecnico:
            db.add(TicketComentario(
                ticket_id=ticket.id, autor_nombre=tecnico.nombre_completo,
                contenido="Estamos revisando el caso, en breve les compartimos novedades.",
            ))
    db.commit()
