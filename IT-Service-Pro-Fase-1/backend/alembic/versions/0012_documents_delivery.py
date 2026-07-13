"""IT Service Pro: Documentos (repositorio por empresa) y Guías de Remisión.

Revision ID: 0012_documents_delivery
Revises: 0011_phase3_modules
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0012_documents_delivery"
down_revision = "0011_phase3_modules"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "documentos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("empresas_cliente.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("categoria", sa.String(60), nullable=False, server_default="General"),
        sa.Column("url_archivo", sa.String(500), nullable=False),
        sa.Column("tipo_mime", sa.String(120), nullable=True),
        sa.Column("tamano_bytes", sa.Integer(), nullable=True),
        sa.Column("visible_portal", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("subido_por_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_documentos_empresa_id", "documentos", ["empresa_id"])

    op.create_table(
        "guias_remision",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("numero", sa.String(20), nullable=False, unique=True),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("empresas_cliente.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False, server_default="ENTREGA_EQUIPO"),
        sa.Column("estado", sa.String(20), nullable=False, server_default="EMITIDA"),
        sa.Column("direccion_entrega", sa.String(250), nullable=True),
        sa.Column("transportista", sa.String(150), nullable=True),
        sa.Column("fecha_emision", sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column("fecha_entrega", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_guias_remision_empresa_id", "guias_remision", ["empresa_id"])
    op.create_index("ix_guias_remision_numero", "guias_remision", ["numero"])

    op.create_table(
        "guia_detalles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("guia_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("guias_remision.id", ondelete="CASCADE"), nullable=False),
        sa.Column("producto_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("descripcion", sa.String(250), nullable=True),
    )


def downgrade():
    op.drop_table("guia_detalles")
    op.drop_table("guias_remision")
    op.drop_table("documentos")
