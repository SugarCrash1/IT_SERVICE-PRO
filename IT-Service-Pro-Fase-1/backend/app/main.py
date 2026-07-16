"""
Punto de entrada de la aplicación FastAPI.
Configura middlewares, CORS, manejo de excepciones y el registro de rutas.
Fase 7: se registran autenticación, usuarios, clientes, categorías y servicios.
"""
import logging
import logging.config
import subprocess
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Aplicar configuración de logging centralizada
from app.core.logging_config import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)

from app.api.routes.auth_routes import router as auth_router
from app.api.routes.user_routes import router as user_router
from app.api.routes.client_routes import router as client_router
from app.api.routes.service_routes import router as service_router
from app.api.routes.employee_routes import router as employee_router
from app.api.routes.appointment_routes import router as appointment_router
from app.api.routes.sale_routes import router as sale_router
from app.api.routes.inventory_routes import router as inventory_router
from app.api.routes.report_routes import router as report_router
from app.api.routes.client_portal_routes import router as client_portal_router
from app.api.routes.finance_routes import router as finance_router
from app.api.routes.public_routes import router as public_router
from app.api.routes.itsp_foundation_routes import router as itsp_foundation_router
from app.api.routes.ticket_routes import router as ticket_router
from app.api.routes.asset_routes import router as asset_router
from app.api.routes.project_routes import router as project_router
from app.api.routes.contract_routes import router as contract_router
from app.api.routes.knowledge_routes import router as knowledge_router
from fastapi.staticfiles import StaticFiles
from app.api.routes.timesheet_routes import router as timesheet_router
from app.api.routes.upload_routes import router as upload_router
from app.api.routes.document_routes import router as document_router
from app.api.routes.delivery_routes import router as delivery_router
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.database.base import Base
from app.database.session import engine

# Logger para mensajes de startup
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="ERP + Service Desk para consultoras de tecnología: empresas, contactos, servicios TI, tickets, proyectos, CMDB y operación comercial.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS: permite que el frontend (Vite en localhost:5173) consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejadores globales de excepciones
register_exception_handlers(app)


# ===========================================
# Inicialización de Base de Datos (Module-level)
# ===========================================
def _init_database_sync() -> None:
    """Inicializa la BD al nivel del módulo (antes de Uvicorn)."""
    print("\n" + "="*70, flush=True)
    print("🔧 INICIALIZANDO BASE DE DATOS...", flush=True)
    print("="*70, flush=True)
    
    # Paso 1: Intentar migraciones con Alembic
    print("\n📝 Intento 1: Ejecutando migraciones de Alembic...", flush=True)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Migraciones de Alembic completadas exitosamente.\n", flush=True)
            return
        else:
            print(f"⚠️ Alembic retornó código {result.returncode}", flush=True)
            if result.stderr:
                print(f"   Error: {result.stderr[:300]}\n", flush=True)
    
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout en Alembic (>60s), intentando fallback...\n", flush=True)
    except Exception as e:
        print(f"⚠️ Error en Alembic: {type(e).__name__}: {str(e)[:200]}\n", flush=True)
    
    # Paso 2: Fallback a SQLAlchemy create_all
    print("📝 Intento 2: Creando/verificando tablas con SQLAlchemy...", flush=True)
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas/verificadas exitosamente.\n", flush=True)
    except Exception as e:
        print(f"❌ ERROR al crear tablas: {type(e).__name__}: {str(e)[:300]}\n", flush=True)
        raise
    
    print("="*70)
    print("🚀 BASE DE DATOS LISTA PARA OPERACIÓN")
    print("="*70 + "\n", flush=True)


# Ejecutar inicialización de BD al importarse este módulo
_init_database_sync()


@app.on_event("startup")
async def startup_event() -> None:
    """Event handler adicional (puede no ejecutarse si la BD ya está lista)."""
    print("🚀 Evento startup de FastAPI ejecutado.", flush=True)


@app.get("/", tags=["Sistema"])
def raiz() -> dict:
    """Endpoint raíz de verificación rápida de que la API está activa."""
    return {
        "aplicacion": settings.APP_NAME,
        "estado": "activo",
        "version": app.version,
        "documentacion": "/docs",
    }


@app.get("/health", tags=["Sistema"])
def health_check() -> dict:
    """Endpoint de verificación de salud (health check) para monitoreo."""
    return {"status": "ok"}


# Registro de routers de negocio
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(user_router, prefix=settings.API_V1_PREFIX)
app.include_router(client_router, prefix=settings.API_V1_PREFIX)
app.include_router(service_router, prefix=settings.API_V1_PREFIX)
app.include_router(employee_router, prefix=settings.API_V1_PREFIX)
app.include_router(appointment_router, prefix=settings.API_V1_PREFIX)
app.include_router(sale_router, prefix=settings.API_V1_PREFIX)
app.include_router(inventory_router, prefix=settings.API_V1_PREFIX)
app.include_router(report_router, prefix=settings.API_V1_PREFIX)
app.include_router(client_portal_router, prefix=settings.API_V1_PREFIX)
app.include_router(finance_router, prefix=settings.API_V1_PREFIX)
app.include_router(public_router, prefix=settings.API_V1_PREFIX)
app.include_router(itsp_foundation_router, prefix=settings.API_V1_PREFIX)
app.include_router(ticket_router, prefix=settings.API_V1_PREFIX)
app.include_router(asset_router, prefix=settings.API_V1_PREFIX)
app.include_router(project_router, prefix=settings.API_V1_PREFIX)
app.include_router(contract_router, prefix=settings.API_V1_PREFIX)
app.include_router(knowledge_router, prefix=settings.API_V1_PREFIX)
app.include_router(timesheet_router, prefix=settings.API_V1_PREFIX)
app.include_router(upload_router, prefix=settings.API_V1_PREFIX)
app.include_router(document_router, prefix=settings.API_V1_PREFIX)
app.include_router(delivery_router, prefix=settings.API_V1_PREFIX)

import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Fase 9: dashboard, indicadores, reportes y exportaciones integrados.
