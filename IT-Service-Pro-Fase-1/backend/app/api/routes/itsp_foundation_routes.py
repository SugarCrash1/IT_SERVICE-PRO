"""Endpoints base de IT Service Pro (Fase 1)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.constants import RolesSistema
from app.core.exceptions import ConflictException, NotFoundException
from app.core.permissions import require_roles
from app.models.itsp_foundation_model import ContactoEmpresa, EmpresaCliente, ServicioTI
from app.models.user_model import Usuario
from app.schemas.itsp_foundation_schema import (
    CambiarEstadoRequest,
    ContactoCreate,
    ContactoResponse,
    ContactoUpdate,
    EmpresaCreate,
    EmpresaResponse,
    EmpresaUpdate,
    ServicioTICreate,
    ServicioTIResponse,
    ServicioTIUpdate,
)

router = APIRouter(prefix="/itsp", tags=["IT Service Pro - Fundación"])


@router.get("/foundation")
def foundation() -> dict:
    return {
        "producto": "IT Service Pro",
        "version": "1.0.0-fase-1",
        "modulos": ["Empresas", "Contactos", "Servicios TI", "Tickets", "Proyectos", "CMDB"],
        "roles": RolesSistema.TODOS,
    }


@router.get("/companies", response_model=list[EmpresaResponse])
def list_companies(
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR, RolesSistema.TECNICO)),
):
    q = db.query(EmpresaCliente)
    if search:
        term = f"%{search.strip()}%"
        q = q.filter((EmpresaCliente.razon_social.ilike(term)) | (EmpresaCliente.nombre_comercial.ilike(term)))
    return q.order_by(EmpresaCliente.razon_social).all()


@router.post("/companies", response_model=EmpresaResponse, status_code=201)
def create_company(
    payload: EmpresaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR)),
):
    if db.query(EmpresaCliente).filter(EmpresaCliente.ruc == payload.ruc).first():
        raise ConflictException("Ya existe una empresa con ese RUC")
    item = EmpresaCliente(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/contacts", response_model=list[ContactoResponse])
def list_contacts(
    empresa_id: str | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR, RolesSistema.TECNICO)),
):
    q = db.query(ContactoEmpresa)
    if empresa_id:
        q = q.filter(ContactoEmpresa.empresa_id == empresa_id)
    return q.order_by(ContactoEmpresa.apellidos, ContactoEmpresa.nombres).all()


@router.post("/contacts", response_model=ContactoResponse, status_code=201)
def create_contact(
    payload: ContactoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR)),
):
    if not db.get(EmpresaCliente, payload.empresa_id):
        raise NotFoundException("Empresa no encontrada")
    item = ContactoEmpresa(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/services", response_model=list[ServicioTIResponse])
def list_services(
    categoria: str | None = None,
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(*RolesSistema.TODOS)),
):
    q = db.query(ServicioTI)
    if not incluir_inactivos:
        q = q.filter(ServicioTI.estado == "ACTIVO")
    if categoria:
        q = q.filter(ServicioTI.categoria == categoria)
    return q.order_by(ServicioTI.destacado.desc(), ServicioTI.nombre).all()


@router.post("/services", response_model=ServicioTIResponse, status_code=201)
def create_service(
    payload: ServicioTICreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(RolesSistema.ADMINISTRADOR)),
):
    if db.query(ServicioTI).filter(ServicioTI.codigo == payload.codigo).first():
        raise ConflictException("Ya existe un servicio TI con ese código")
    item = ServicioTI(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# ---------------------------------------------------------------------------
# Edición, cambio de estado y eliminación: completan el CRUD de las tres
# entidades base (empresas, contactos, servicios TI).
# ---------------------------------------------------------------------------

@router.put("/companies/{empresa_id}", response_model=EmpresaResponse)
def update_company(
    empresa_id: str, payload: EmpresaUpdate, db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR)),
):
    item = db.get(EmpresaCliente, empresa_id)
    if not item:
        raise NotFoundException("Empresa no encontrada")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/companies/{empresa_id}/status", response_model=EmpresaResponse,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR))])
def toggle_company_status(empresa_id: str, payload: CambiarEstadoRequest, db: Session = Depends(get_db)):
    item = db.get(EmpresaCliente, empresa_id)
    if not item:
        raise NotFoundException("Empresa no encontrada")
    item.estado = payload.estado
    db.commit()
    db.refresh(item)
    return item


@router.put("/contacts/{contacto_id}", response_model=ContactoResponse)
def update_contact(
    contacto_id: str, payload: ContactoUpdate, db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR)),
):
    item = db.get(ContactoEmpresa, contacto_id)
    if not item:
        raise NotFoundException("Contacto no encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/contacts/{contacto_id}/status", response_model=ContactoResponse)
def toggle_contact_status(
    contacto_id: str, payload: CambiarEstadoRequest, db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR)),
):
    item = db.get(ContactoEmpresa, contacto_id)
    if not item:
        raise NotFoundException("Contacto no encontrado")
    item.estado = payload.estado
    db.commit()
    db.refresh(item)
    return item


@router.delete("/contacts/{contacto_id}", status_code=204,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR, RolesSistema.COORDINADOR))])
def delete_contact(contacto_id: str, db: Session = Depends(get_db)):
    item = db.get(ContactoEmpresa, contacto_id)
    if not item:
        raise NotFoundException("Contacto no encontrado")
    db.delete(item)
    db.commit()


@router.put("/services/{servicio_id}", response_model=ServicioTIResponse,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR))])
def update_service(servicio_id: str, payload: ServicioTIUpdate, db: Session = Depends(get_db)):
    item = db.get(ServicioTI, servicio_id)
    if not item:
        raise NotFoundException("Servicio TI no encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/services/{servicio_id}/status", response_model=ServicioTIResponse,
    dependencies=[Depends(require_roles(RolesSistema.ADMINISTRADOR))])
def toggle_service_status(servicio_id: str, payload: CambiarEstadoRequest, db: Session = Depends(get_db)):
    item = db.get(ServicioTI, servicio_id)
    if not item:
        raise NotFoundException("Servicio TI no encontrado")
    item.estado = payload.estado
    db.commit()
    db.refresh(item)
    return item
