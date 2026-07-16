"""
Configuración de logging estructurado para la aplicación y Uvicorn.
Corrige el problema de que Uvicorn escribe a stderr y se marca como severity=error.
"""
import logging
import sys
from typing import Any

# Formato estándar que incluye el nivel de log para parsing correcto
DEFAULT_FORMAT = "%(levelname)s:     %(message)s"
ACCESS_FORMAT = '%(levelname)s:     %(client_addr)s - "%(request_line)s" %(status_code)s'


def get_logging_config() -> dict[str, Any]:
    """
    Retorna la configuración de logging para Uvicorn y la aplicación.
    
    Esto asegura que:
    - Los niveles de log (INFO, WARNING, ERROR) se parseén correctamente
    - No se dependea del file descriptor (stderr vs stdout)
    - Ambos Uvicorn y la aplicación usen handlers consistentes
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        
        # Formatos: incluyen el nivel explícitamente para que sea parseado correctamente
        "formatters": {
            "default": {
                "format": DEFAULT_FORMAT,
            },
            "access": {
                "format": ACCESS_FORMAT,
            },
        },
        
        # Handlers: todos escriben a stdout (no stderr) para evitar severity=error
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # Explícitamente stdout
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # Explícitamente stdout
            },
        },
        
        # Loggers: configuran los niveles correctos para cada módulo
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "INFO",
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
            },
            "app": {
                "handlers": ["default"],
                "level": "INFO",
            },
        },
    }


# Configuración alternativa con dictConfig (para compatibilidad)
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": DEFAULT_FORMAT},
        "access": {"format": ACCESS_FORMAT},
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO"},
        "app": {"handlers": ["default"], "level": "INFO"},
    },
}
