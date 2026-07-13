"""
Seed de usuarios iniciales del sistema: administrador, recepcionista y estilista.
Se ejecuta después de `roles_seed.py`, ya que depende de que los roles existan.
"""
from sqlalchemy.orm import Session

from app.core.constants import EstadoGenerico, RolesSistema
from app.core.security import hash_password
from app.models.role_model import Rol
from app.models.user_model import Usuario

USUARIOS_INICIALES = [
    {
        "nombre_completo": "Administrador IT Service Pro",
        "correo": "admin@itservicepro.com",
        "password": "Admin123*",
        "rol": RolesSistema.ADMINISTRADOR,
    },
    {
        "nombre_completo": "Coordinador Service Desk",
        "correo": "coordinador@itservicepro.com",
        "password": "Coordinador123*",
        "rol": RolesSistema.COORDINADOR,
    },
    {
        "nombre_completo": "Técnico de Soporte",
        "correo": "tecnico@itservicepro.com",
        "password": "Tecnico123*",
        "rol": RolesSistema.TECNICO,
    },
]


def seed_admin_and_base_users(db: Session, roles: dict[str, Rol]) -> dict[str, Usuario]:
    """
    Crea los tres usuarios iniciales del sistema (uno por cada rol) si no existen aún.

    Args:
        db: sesión activa de base de datos.
        roles: diccionario de roles ya creados por `seed_roles`.

    Returns:
        Diccionario {correo: instancia Usuario} de los usuarios creados o existentes.
    """
    usuarios: dict[str, Usuario] = {}
    for datos in USUARIOS_INICIALES:
        usuario_existente = db.query(Usuario).filter(Usuario.correo == datos["correo"]).first()
        if usuario_existente:
            usuarios[datos["correo"]] = usuario_existente
            continue

        nuevo_usuario = Usuario(
            nombre_completo=datos["nombre_completo"],
            correo=datos["correo"],
            password_hash=hash_password(datos["password"]),
            rol_id=roles[datos["rol"]].id,
            estado=EstadoGenerico.ACTIVO,
            debe_cambiar_password=False,
        )
        db.add(nuevo_usuario)
        db.flush()
        usuarios[datos["correo"]] = nuevo_usuario

    db.commit()
    return usuarios
