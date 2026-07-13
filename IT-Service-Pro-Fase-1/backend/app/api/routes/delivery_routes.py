"""Rutas REST de Guías de Remisión (despacho de equipos/materiales)."""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db, get_current_user
from app.core.constants import EstadoGuia, RolesSistema, TipoGuia, TipoMovimientoInventario
from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.core.permissions import require_roles
from app.models.delivery_model import GuiaDetalle, GuiaRemision
from app.models.inventory_model import InventarioMovimiento
from app.models.itsp_foundation_model import EmpresaCliente
from app.models.product_model import Producto
from app.models.ticket_model import Ticket
from app.models.user_model import Usuario
from app.schemas.delivery_schema import GuiaCreate, GuiaResponse

router = APIRouter(
    prefix="/delivery-notes", tags=["Guías de remisión"],
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR, RolesSistema.TECNICO))],
)


def _numero(db: Session) -> str:
    total = db.query(GuiaRemision.id).count()
    candidato = total + 1
    while True:
        numero = f"GR-{candidato:05d}"
        if not db.query(GuiaRemision.id).filter(GuiaRemision.numero == numero).first():
            return numero
        candidato += 1


def _response(g: GuiaRemision) -> GuiaResponse:
    return GuiaResponse(
        id=g.id, numero=g.numero, empresa_id=g.empresa_id,
        empresa_nombre=g.empresa.nombre_comercial or g.empresa.razon_social,
        ticket_id=g.ticket_id, ticket_codigo=g.ticket.codigo if g.ticket else None,
        usuario_nombre=g.usuario.nombre_completo, tipo=g.tipo, estado=g.estado,
        direccion_entrega=g.direccion_entrega, transportista=g.transportista,
        fecha_emision=g.fecha_emision, fecha_entrega=g.fecha_entrega, observaciones=g.observaciones,
        detalles=[
            {"id": d.id, "producto_id": d.producto_id, "producto_nombre": d.producto.nombre, "cantidad": d.cantidad, "descripcion": d.descripcion}
            for d in g.detalles
        ],
        created_at=g.created_at,
    )


def _query(db: Session):
    return db.query(GuiaRemision).options(
        joinedload(GuiaRemision.empresa), joinedload(GuiaRemision.ticket), joinedload(GuiaRemision.usuario),
        joinedload(GuiaRemision.detalles).joinedload(GuiaDetalle.producto),
    )


@router.get("", response_model=list[GuiaResponse])
def listar(empresa_id: uuid.UUID | None = Query(None), estado: str | None = Query(None), db: Session = Depends(get_db)):
    q = _query(db)
    if empresa_id:
        q = q.filter(GuiaRemision.empresa_id == empresa_id)
    if estado:
        q = q.filter(GuiaRemision.estado == estado)
    return [_response(g) for g in q.order_by(GuiaRemision.created_at.desc()).all()]


@router.get("/options", response_model=dict)
def opciones():
    return {"tipos": TipoGuia.TODOS, "estados": EstadoGuia.TODOS}


@router.post("", response_model=GuiaResponse, status_code=201)
def crear(datos: GuiaCreate, db: Session = Depends(get_db), actor: Usuario = Depends(get_current_user)):
    if not db.get(EmpresaCliente, datos.empresa_id):
        raise NotFoundException("Empresa no encontrada")
    if datos.ticket_id and not db.get(Ticket, datos.ticket_id):
        raise NotFoundException("Ticket no encontrado")
    productos = {}
    for linea in datos.detalles:
        producto = db.get(Producto, linea.producto_id)
        if not producto:
            raise NotFoundException(f"Producto {linea.producto_id} no encontrado")
        productos[str(linea.producto_id)] = producto

    guia = GuiaRemision(
        numero=_numero(db), empresa_id=datos.empresa_id, ticket_id=datos.ticket_id, usuario_id=actor.id,
        tipo=datos.tipo, direccion_entrega=datos.direccion_entrega, transportista=datos.transportista,
        observaciones=datos.observaciones,
    )
    db.add(guia)
    db.flush()
    for linea in datos.detalles:
        db.add(GuiaDetalle(guia_id=guia.id, producto_id=linea.producto_id, cantidad=linea.cantidad, descripcion=linea.descripcion))
    db.commit()
    return _response(_query(db).filter(GuiaRemision.id == guia.id).first())


@router.get("/{guia_id}", response_model=GuiaResponse)
def obtener(guia_id: uuid.UUID, db: Session = Depends(get_db)):
    item = _query(db).filter(GuiaRemision.id == guia_id).first()
    if not item:
        raise NotFoundException("Guía no encontrada")
    return _response(item)


@router.post("/{guia_id}/deliver", response_model=GuiaResponse)
def confirmar_entrega(guia_id: uuid.UUID, db: Session = Depends(get_db), actor: Usuario = Depends(get_current_user)):
    """Confirma la entrega: descuenta stock de cada producto y deja el
    movimiento correspondiente en el kardex."""
    guia = _query(db).filter(GuiaRemision.id == guia_id).first()
    if not guia:
        raise NotFoundException("Guía no encontrada")
    if guia.estado != EstadoGuia.EMITIDA:
        raise ConflictException("Solo se puede confirmar la entrega de una guía emitida")

    for detalle in guia.detalles:
        producto = detalle.producto
        if producto.stock < detalle.cantidad:
            raise ValidationException(f"Stock insuficiente de '{producto.nombre}' (disponible: {producto.stock}, requerido: {detalle.cantidad})")

    from datetime import datetime, timezone
    for detalle in guia.detalles:
        producto = detalle.producto
        producto.stock -= detalle.cantidad
        db.add(InventarioMovimiento(
            producto_id=producto.id, tipo=TipoMovimientoInventario.SALIDA, cantidad=detalle.cantidad,
            stock_resultante=producto.stock, motivo=f"Guía de remisión {guia.numero} — {guia.empresa.nombre_comercial or guia.empresa.razon_social}",
            usuario_id=actor.id,
        ))
    guia.estado = EstadoGuia.ENTREGADA
    guia.fecha_entrega = datetime.now(timezone.utc)
    db.commit()
    return _response(_query(db).filter(GuiaRemision.id == guia_id).first())


@router.post("/{guia_id}/void", response_model=GuiaResponse,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def anular(guia_id: uuid.UUID, db: Session = Depends(get_db)):
    guia = db.get(GuiaRemision, guia_id)
    if not guia:
        raise NotFoundException("Guía no encontrada")
    if guia.estado == EstadoGuia.ENTREGADA:
        raise ConflictException("No se puede anular una guía ya entregada (afectaría el kardex ya registrado)")
    guia.estado = EstadoGuia.ANULADA
    db.commit()
    return _response(_query(db).filter(GuiaRemision.id == guia_id).first())
