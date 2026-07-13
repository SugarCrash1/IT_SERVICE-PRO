"""IT Service Pro: módulo completo de Tickets (mesa de ayuda) con SLA,
comentarios, adjuntos, historial y vínculo del portal de contactos.

Revision ID: 0009_tickets_module
Revises: 0008_itsp_phase1_foundation
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0009_tickets_module"
down_revision = "0008_itsp_phase1_foundation"
branch_labels = None
depends_on = None


def upgrade():
    # Vínculo del usuario del portal con su contacto de empresa (IT Service Pro)
    op.add_column("usuarios", sa.Column("contacto_empresa_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_usuarios_contacto_empresa", "usuarios", "contactos_empresa",
        ["contacto_empresa_id"], ["id"], ondelete="SET NULL",
    )
    op.create_index("ix_usuarios_contacto_empresa_id", "usuarios", ["contacto_empresa_id"], unique=True)

    op.create_table(
        "sla_politicas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nivel_sla", sa.String(30), nullable=False),
        sa.Column("prioridad", sa.String(20), nullable=False),
        sa.Column("horas_respuesta", sa.Integer(), nullable=False),
        sa.Column("horas_resolucion", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("nivel_sla", "prioridad", name="uq_sla_nivel_prioridad"),
    )
    op.create_index("ix_sla_politicas_nivel", "sla_politicas", ["nivel_sla"])
    op.create_index("ix_sla_politicas_prioridad", "sla_politicas", ["prioridad"])

    op.create_table(
        "tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(20), nullable=False, unique=True),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("empresas_cliente.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("contacto_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contactos_empresa.id", ondelete="SET NULL"), nullable=True),
        sa.Column("servicio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("servicios_ti.id", ondelete="SET NULL"), nullable=True),
        sa.Column("asignado_a", postgresql.UUID(as_uuid=True), sa.ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("categoria", sa.String(30), nullable=False, server_default="INCIDENTE"),
        sa.Column("prioridad", sa.String(20), nullable=False, server_default="MEDIA"),
        sa.Column("estado", sa.String(30), nullable=False, server_default="ABIERTO"),
        sa.Column("canal", sa.String(20), nullable=False, server_default="PORTAL"),
        sa.Column("horas_respuesta_sla", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("horas_resolucion_sla", sa.Integer(), nullable=False, server_default="48"),
        sa.Column("fecha_limite_respuesta", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_limite_resolucion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_primera_respuesta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_resolucion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_cierre", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tiempo_invertido_minutos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("calificacion_satisfaccion", sa.Integer(), nullable=True),
        sa.Column("comentario_satisfaccion", sa.String(500), nullable=True),
        sa.Column("motivo_cierre", sa.String(500), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tickets_empresa_id", "tickets", ["empresa_id"])
    op.create_index("ix_tickets_contacto_id", "tickets", ["contacto_id"])
    op.create_index("ix_tickets_servicio_id", "tickets", ["servicio_id"])
    op.create_index("ix_tickets_asignado_a", "tickets", ["asignado_a"])
    op.create_index("ix_tickets_estado", "tickets", ["estado"])
    op.create_index("ix_tickets_codigo", "tickets", ["codigo"])

    op.create_table(
        "ticket_comentarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("autor_usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("autor_nombre", sa.String(150), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("es_interno", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("es_del_cliente", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ticket_comentarios_ticket_id", "ticket_comentarios", ["ticket_id"])

    op.create_table(
        "ticket_adjuntos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("comentario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ticket_comentarios.id", ondelete="CASCADE"), nullable=True),
        sa.Column("nombre_archivo", sa.String(255), nullable=False),
        sa.Column("url_archivo", sa.Text(), nullable=False),
        sa.Column("tipo_mime", sa.String(120), nullable=True),
        sa.Column("tamano_bytes", sa.Integer(), nullable=True),
        sa.Column("subido_por_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ticket_adjuntos_ticket_id", "ticket_adjuntos", ["ticket_id"])

    op.create_table(
        "ticket_historial",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_nombre", sa.String(150), nullable=False),
        sa.Column("evento", sa.String(50), nullable=False),
        sa.Column("descripcion", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ticket_historial_ticket_id", "ticket_historial", ["ticket_id"])

    # Políticas de SLA por defecto (horas de respuesta / resolución) por nivel y prioridad
    sla_table = sa.table(
        "sla_politicas", sa.column("id", postgresql.UUID(as_uuid=True)), sa.column("nivel_sla", sa.String),
        sa.column("prioridad", sa.String), sa.column("horas_respuesta", sa.Integer), sa.column("horas_resolucion", sa.Integer),
    )
    import uuid as _uuid
    filas = []
    matriz = {
        "STANDARD": {"CRITICA": (2, 8), "ALTA": (4, 16), "MEDIA": (8, 32), "BAJA": (24, 72)},
        "GOLD": {"CRITICA": (1, 4), "ALTA": (2, 8), "MEDIA": (4, 16), "BAJA": (16, 48)},
        "PLATINUM": {"CRITICA": (0, 2), "ALTA": (1, 4), "MEDIA": (2, 8), "BAJA": (8, 24)},
    }
    for nivel, prioridades in matriz.items():
        for prioridad, (h_resp, h_res) in prioridades.items():
            filas.append({
                "id": _uuid.uuid4(), "nivel_sla": nivel, "prioridad": prioridad,
                "horas_respuesta": h_resp, "horas_resolucion": h_res,
            })
    op.bulk_insert(sla_table, filas)


def downgrade():
    op.drop_table("ticket_historial")
    op.drop_table("ticket_adjuntos")
    op.drop_table("ticket_comentarios")
    op.drop_table("tickets")
    op.drop_table("sla_politicas")
    op.drop_index("ix_usuarios_contacto_empresa_id", table_name="usuarios")
    op.drop_constraint("fk_usuarios_contacto_empresa", "usuarios", type_="foreignkey")
    op.drop_column("usuarios", "contacto_empresa_id")
