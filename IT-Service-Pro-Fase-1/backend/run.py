"""
Script de arranque del servidor de desarrollo.
Ejecutar con: python run.py
"""
import os
import subprocess
import sys

import uvicorn

from app.core.config import settings

if __name__ == "__main__":
    # Ejecutar migraciones de Alembic automáticamente
    print("Ejecutando migraciones de Alembic...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"⚠️ Error en migraciones: {result.stderr}")
        else:
            print("✅ Migraciones ejecutadas correctamente.")
    except Exception as e:
        print(f"⚠️ No se pudieron ejecutar las migraciones automáticamente: {e}")
    
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.APP_ENV == "development",
    )
