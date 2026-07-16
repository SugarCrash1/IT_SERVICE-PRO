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
    print("\n" + "="*60)
    print("🔧 Iniciando aplicación...")
    print("="*60)
    print("📝 Ejecutando migraciones de Alembic...\n")
    
    try:
        # Correr alembic sin capturar output para verlo en los logs
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print("\n✅ Migraciones completadas exitosamente.")
        else:
            print(f"\n⚠️ Advertencia: Alembic retornó código {result.returncode}")
            print("La aplicación continuará, pero puede que falten tablas.")
    
    except FileNotFoundError:
        print("\n⚠️ Alembic no encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "alembic"], check=True)
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"])
        print("✅ Migraciones completadas después de instalar alembic.")
    
    except Exception as e:
        print(f"\n❌ Error al ejecutar migraciones: {type(e).__name__}: {e}")
        print("La aplicación continuará, pero puede que falten tablas.")
    
    print("="*60)
    print("🚀 Iniciando servidor Uvicorn...\n")
    print("="*60 + "\n")
    
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.APP_ENV == "development",
    )
