"""IT Service Pro Fase 1: fundación del dominio TI.

Revision ID: 0008_itsp_phase1_foundation
Revises: 0007_chat_memory
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_itsp_phase1_foundation"
down_revision = "0007_chat_memory"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE roles SET nombre='COORDINADOR', descripcion='Coordina la mesa de ayuda, empresas y asignaciones' WHERE nombre='RECEPCIONISTA'")
    op.execute("UPDATE roles SET nombre='TECNICO', descripcion='Atiende tickets y actividades técnicas asignadas' WHERE nombre='ESTILISTA'")
    op.create_table(
        "empresas_cliente",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("razon_social", sa.String(180), nullable=False),
        sa.Column("nombre_comercial", sa.String(150)),
        sa.Column("ruc", sa.String(20), nullable=False, unique=True),
        sa.Column("sector", sa.String(100)), sa.Column("sitio_web", sa.String(255)),
        sa.Column("correo", sa.String(180)), sa.Column("telefono", sa.String(40)),
        sa.Column("direccion", sa.String(255)), sa.Column("ciudad", sa.String(100)),
        sa.Column("pais", sa.String(80), nullable=False, server_default="Perú"),
        sa.Column("nivel_sla", sa.String(30), nullable=False, server_default="STANDARD"),
        sa.Column("contrato_inicio", sa.Date()), sa.Column("contrato_fin", sa.Date()),
        sa.Column("logo_url", sa.String(500)),
        sa.Column("estado", sa.String(20), nullable=False, server_default="ACTIVO"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_empresas_cliente_razon_social", "empresas_cliente", ["razon_social"])
    op.create_index("ix_empresas_cliente_estado", "empresas_cliente", ["estado"])
    op.create_table(
        "contactos_empresa",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("empresas_cliente.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nombres", sa.String(100), nullable=False), sa.Column("apellidos", sa.String(100), nullable=False),
        sa.Column("cargo", sa.String(120)), sa.Column("area", sa.String(100)),
        sa.Column("correo", sa.String(180), nullable=False), sa.Column("telefono", sa.String(40)),
        sa.Column("puede_crear_tickets", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("es_contacto_principal", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("estado", sa.String(20), nullable=False, server_default="ACTIVO"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_contactos_empresa_empresa_id", "contactos_empresa", ["empresa_id"])
    op.create_table(
        "servicios_ti",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(30), nullable=False, unique=True),
        sa.Column("nombre", sa.String(150), nullable=False), sa.Column("categoria", sa.String(80), nullable=False),
        sa.Column("descripcion", sa.Text()), sa.Column("tecnologia", sa.String(180)),
        sa.Column("tiempo_respuesta_horas", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("precio_base", sa.Numeric(12,2), nullable=False, server_default="0"),
        sa.Column("imagen_url", sa.String(500)), sa.Column("destacado", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("estado", sa.String(20), nullable=False, server_default="ACTIVO"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_servicios_ti_categoria", "servicios_ti", ["categoria"])


def downgrade():
    op.drop_table("servicios_ti")
    op.drop_table("contactos_empresa")
    op.drop_table("empresas_cliente")
    op.execute("UPDATE roles SET nombre='RECEPCIONISTA' WHERE nombre='COORDINADOR'")
    op.execute("UPDATE roles SET nombre='ESTILISTA' WHERE nombre='TECNICO'")
