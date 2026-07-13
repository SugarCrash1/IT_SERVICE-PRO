"""
Seed de roles del sistema.
Crea los tres roles fijos (ADMINISTRADOR, RECEPCIONISTA, ESTILISTA) si no existen.
"""
from sqlalchemy.orm import Session

from app.core.constants import RolesSistema
from app.models.role_model import Rol

DESCRIPCIONES_ROLES = {
    RolesSistema.ADMINISTRADOR: "Acceso total al sistema: usuarios, configuración, reportes y auditoría",
    RolesSistema.COORDINADOR: "Coordinación de mesa de ayuda, empresas, tickets y asignaciones",
    RolesSistema.TECNICO: "Atención técnica de tickets, tareas, evidencias y tiempos",
    RolesSistema.CLIENTE: "Portal empresarial para registrar y dar seguimiento a tickets",
}


def seed_roles(db: Session) -> dict[str, Rol]:
    """
    Crea los roles base del sistema si aún no existen en la base de datos.

    Returns:
        Diccionario {nombre_rol: instancia Rol} con los tres roles disponibles.
    """
    roles: dict[str, Rol] = {}
    for nombre in RolesSistema.TODOS:
        rol_existente = db.query(Rol).filter(Rol.nombre == nombre).first()
        if rol_existente:
            roles[nombre] = rol_existente
            continue
        nuevo_rol = Rol(nombre=nombre, descripcion=DESCRIPCIONES_ROLES[nombre])
        db.add(nuevo_rol)
        db.flush()
        roles[nombre] = nuevo_rol
    db.commit()
    return roles
