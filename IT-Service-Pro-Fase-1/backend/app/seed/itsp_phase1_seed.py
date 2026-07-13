"""Datos iniciales de IT Service Pro Fase 1."""
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.itsp_foundation_model import EmpresaCliente, ContactoEmpresa, ServicioTI


def seed_itsp_phase1(db: Session) -> None:
    if db.query(EmpresaCliente).count() == 0:
        empresas = [
            EmpresaCliente(razon_social="Andes Retail S.A.C.", nombre_comercial="Andes Retail", ruc="20600100101", sector="Retail", correo="ti@andesretail.com", telefono="+51 1 700 1001", ciudad="Lima", nivel_sla="GOLD", contrato_inicio=date.today(), contrato_fin=date.today()+timedelta(days=365), logo_url="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=300&q=80"),
            EmpresaCliente(razon_social="Nova Salud Digital S.A.C.", nombre_comercial="Nova Salud", ruc="20600100102", sector="Salud", correo="soporte@novasalud.com", telefono="+51 1 700 1002", ciudad="Lima", nivel_sla="PLATINUM", contrato_inicio=date.today(), contrato_fin=date.today()+timedelta(days=365), logo_url="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=300&q=80"),
            EmpresaCliente(razon_social="Logística del Pacífico S.A.", nombre_comercial="LogiPac", ruc="20600100103", sector="Logística", correo="infraestructura@logipac.com", telefono="+51 1 700 1003", ciudad="Callao", nivel_sla="STANDARD", contrato_inicio=date.today(), contrato_fin=date.today()+timedelta(days=180), logo_url="https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=300&q=80"),
        ]
        db.add_all(empresas); db.flush()
        db.add_all([
            ContactoEmpresa(empresa_id=empresas[0].id,nombres="Lucía",apellidos="Mendoza",cargo="Jefa de TI",area="Tecnología",correo="lucia.mendoza@andesretail.com",telefono="999111001",es_contacto_principal=True),
            ContactoEmpresa(empresa_id=empresas[1].id,nombres="Carlos",apellidos="Vega",cargo="Coordinador de Sistemas",area="Infraestructura",correo="carlos.vega@novasalud.com",telefono="999111002",es_contacto_principal=True),
            ContactoEmpresa(empresa_id=empresas[2].id,nombres="Mariana",apellidos="Paredes",cargo="Analista de Soporte",area="Operaciones",correo="mariana.paredes@logipac.com",telefono="999111003",es_contacto_principal=True),
        ])
    if db.query(ServicioTI).count() == 0:
        db.add_all([
            ServicioTI(codigo="SRV-HD",nombre="Mesa de Ayuda",categoria="Soporte",descripcion="Atención centralizada de incidentes y requerimientos de usuarios.",tecnologia="ITSM, Windows, Microsoft 365",tiempo_respuesta_horas=2,precio_base=1500,destacado=True,imagen_url="https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=900&q=80"),
            ServicioTI(codigo="SRV-CLOUD",nombre="Cloud y Microsoft Azure",categoria="Cloud",descripcion="Diseño, migración, optimización y operación de plataformas cloud.",tecnologia="Azure, AWS, Microsoft 365",tiempo_respuesta_horas=4,precio_base=2800,destacado=True,imagen_url="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=900&q=80"),
            ServicioTI(codigo="SRV-SEC",nombre="Ciberseguridad Gestionada",categoria="Seguridad",descripcion="Monitoreo, hardening, gestión de vulnerabilidades y respuesta ante incidentes.",tecnologia="Fortinet, EDR, SIEM",tiempo_respuesta_horas=1,precio_base=3500,destacado=True,imagen_url="https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=900&q=80"),
            ServicioTI(codigo="SRV-NET",nombre="Redes e Infraestructura",categoria="Infraestructura",descripcion="Implementación y soporte de redes LAN, WAN, Wi-Fi y servidores.",tecnologia="Cisco, Fortinet, VMware, Linux",tiempo_respuesta_horas=4,precio_base=2400,imagen_url="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=900&q=80"),
            ServicioTI(codigo="SRV-DEV",nombre="Desarrollo de Software",categoria="Desarrollo",descripcion="Aplicaciones empresariales, APIs, automatización e integraciones.",tecnologia="Python, Java, React, PostgreSQL",tiempo_respuesta_horas=8,precio_base=5000,imagen_url="https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=900&q=80"),
            ServicioTI(codigo="SRV-DATA",nombre="Datos y Business Intelligence",categoria="Datos",descripcion="Arquitectura de datos, dashboards y analítica empresarial.",tecnologia="Power BI, SQL Server, PostgreSQL",tiempo_respuesta_horas=8,precio_base=3200,imagen_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=900&q=80"),
        ])
    db.commit()
