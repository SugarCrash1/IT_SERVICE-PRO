"""IT Service Pro: Proyectos, Contratos, Base de Conocimiento y Timesheet.

Revision ID: 0011_phase3_modules
Revises: 0010_cmdb_assets
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0011_phase3_modules"
down_revision = "0010_cmdb_assets"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "proyectos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(20), nullable=False, unique=True),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("empresas_cliente.id", ondelete="CASCADE"), nullable=False),
        sa.Column("responsable_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True),
        sa.Column("nombre", sa.String(180), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("estado", sa.String(30), nullable=False, server_default="PLANIFICACION"),
        sa.Column("fecha_inicio", sa.Date(), nullable=True),
        sa.Column("fecha_fin_estimada", sa.Date(), nullable=True),
        sa.Column("fecha_fin_real", sa.Date(), nullable=True),
        sa.Column("presupuesto", sa.Numeric(12, 2), nullable=True),
        sa.Column("avance_porcentaje", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_proyectos_empresa_id", "proyectos", ["empresa_id"])

    op.create_table(
        "proyecto_tareas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("proyecto_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proyectos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("responsable_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("estado", sa.String(30), nullable=False, server_default="PENDIENTE"),
        sa.Column("fecha_limite", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_proyecto_tareas_proyecto_id", "proyecto_tareas", ["proyecto_id"])

    op.create_table(
        "contratos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(20), nullable=False, unique=True),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("empresas_cliente.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nombre", sa.String(180), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False, server_default="SOPORTE"),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=True),
        sa.Column("horas_incluidas_mes", sa.Integer(), nullable=True),
        sa.Column("horas_consumidas_mes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("valor_mensual", sa.Numeric(12, 2), nullable=True),
        sa.Column("estado", sa.String(30), nullable=False, server_default="VIGENTE"),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_contratos_empresa_id", "contratos", ["empresa_id"])

    op.create_table(
        "articulos_conocimiento",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("categoria", sa.String(80), nullable=False, server_default="General"),
        sa.Column("servicio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("servicios_ti.id", ondelete="SET NULL"), nullable=True),
        sa.Column("autor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("publicado", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("vistas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "registros_tiempo",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("empleado_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("proyecto_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proyectos.id", ondelete="SET NULL"), nullable=True),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("minutos", sa.Integer(), nullable=False),
        sa.Column("descripcion", sa.String(300), nullable=False),
        sa.Column("facturable", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_registros_tiempo_empleado_id", "registros_tiempo", ["empleado_id"])
    op.create_index("ix_registros_tiempo_ticket_id", "registros_tiempo", ["ticket_id"])
    op.create_index("ix_registros_tiempo_proyecto_id", "registros_tiempo", ["proyecto_id"])
    op.create_index("ix_registros_tiempo_fecha", "registros_tiempo", ["fecha"])


def downgrade():
    op.drop_table("registros_tiempo")
    op.drop_table("articulos_conocimiento")
    op.drop_table("contratos")
    op.drop_table("proyecto_tareas")
    op.drop_table("proyectos")
