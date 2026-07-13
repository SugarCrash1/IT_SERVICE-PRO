"""IT Service Pro: CMDB — tabla de activos tecnológicos por empresa cliente.

Revision ID: 0010_cmdb_assets
Revises: 0009_tickets_module
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_cmdb_assets"
down_revision = "0009_tickets_module"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "activos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(20), nullable=False, unique=True),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("empresas_cliente.id", ondelete="CASCADE"), nullable=False),
        sa.Column("responsable_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contactos_empresa.id", ondelete="SET NULL"), nullable=True),
        sa.Column("tipo", sa.String(30), nullable=False, server_default="OTRO"),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("marca", sa.String(100), nullable=True),
        sa.Column("modelo", sa.String(100), nullable=True),
        sa.Column("numero_serie", sa.String(120), nullable=True),
        sa.Column("ubicacion", sa.String(150), nullable=True),
        sa.Column("ip_asignada", sa.String(60), nullable=True),
        sa.Column("fecha_compra", sa.Date(), nullable=True),
        sa.Column("fecha_garantia_fin", sa.Date(), nullable=True),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column("estado", sa.String(30), nullable=False, server_default="ACTIVO"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_activos_empresa_id", "activos", ["empresa_id"])
    op.create_index("ix_activos_codigo", "activos", ["codigo"])


def downgrade():
    op.drop_table("activos")
