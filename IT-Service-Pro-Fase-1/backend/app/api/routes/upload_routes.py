"""Endpoint genérico de subida de archivos: fotos de tickets, adjuntos y
documentos del portal. Guarda el archivo en disco (carpeta `uploads/`) y
devuelve la URL pública con la que luego se referencia desde otros módulos."""
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.exceptions import ValidationException
from app.models.user_model import Usuario
from app.schemas.common_schema import RespuestaExito

router = APIRouter(prefix="/uploads", tags=["Archivos"])

EXTENSIONES_PERMITIDAS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt", ".zip",
}


def _upload_dir() -> Path:
    path = Path(settings.UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


@router.post("", response_model=RespuestaExito[dict], status_code=201)
async def subir_archivo(archivo: UploadFile = File(...), actor: Usuario = Depends(get_current_user)):
    extension = Path(archivo.filename or "").suffix.lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        raise ValidationException(
            f"Tipo de archivo no permitido ({extension or 'sin extensión'}). "
            f"Formatos aceptados: {', '.join(sorted(EXTENSIONES_PERMITIDAS))}"
        )

    contenido = await archivo.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contenido) > max_bytes:
        raise ValidationException(f"El archivo supera el límite de {settings.MAX_UPLOAD_SIZE_MB} MB")

    nombre_disco = f"{uuid.uuid4().hex}{extension}"
    destino = _upload_dir() / nombre_disco
    destino.write_bytes(contenido)

    return RespuestaExito(data={
        "url": f"/uploads/{nombre_disco}",
        "nombre_archivo": archivo.filename,
        "tipo_mime": archivo.content_type,
        "tamano_bytes": len(contenido),
    })
