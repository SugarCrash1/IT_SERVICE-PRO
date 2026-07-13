"""Seed oficial de IT Service Pro Fase 1.

Uso:
    python -m app.seed.run_seed
"""
from app.database.session import SessionLocal
from app.seed.admin_seed import seed_admin_and_base_users
from app.seed.itsp_phase1_seed import seed_itsp_phase1
from app.seed.roles_seed import seed_roles
from app.seed.tickets_seed import seed_tickets


def main() -> None:
    db = SessionLocal()
    try:
        print("1/4 Creando roles de IT Service Pro...")
        roles = seed_roles(db)
        print(f"    Roles: {list(roles.keys())}")
        print("2/4 Creando usuarios iniciales...")
        usuarios = seed_admin_and_base_users(db, roles)
        print(f"    Usuarios: {list(usuarios.keys())}")
        print("3/4 Cargando empresas, contactos y servicios TI...")
        seed_itsp_phase1(db)
        print("4/4 Cargando técnicos, portal de contactos y tickets de ejemplo...")
        seed_tickets(db)
        print("Seed de IT Service Pro completado.")
        print("Admin: admin@itservicepro.com / Admin123*")
        print("Coordinador: coordinador@itservicepro.com / Coordinador123*")
        print("Técnico: tecnico@itservicepro.com / Tecnico123*")
        print("Técnico 2: tecnico2@itservicepro.com / Tecnico123*")
        print("Portal empresarial (contacto principal): revisa la tabla contactos_empresa / Portal123*")
    finally:
        db.close()


if __name__ == "__main__":
    main()
