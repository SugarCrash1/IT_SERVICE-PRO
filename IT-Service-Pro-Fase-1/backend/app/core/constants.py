"""
Constantes globales utilizadas en toda la aplicación.
Centraliza valores fijos para evitar cadenas mágicas dispersas en el código.
"""


class RolesSistema:
    """Nombres de los roles disponibles en el sistema."""

    ADMINISTRADOR = "ADMINISTRADOR"
    COORDINADOR = "COORDINADOR"
    TECNICO = "TECNICO"
    CLIENTE = "CLIENTE"

    TODOS = [ADMINISTRADOR, COORDINADOR, TECNICO, CLIENTE]


class EstadoCita:
    """Estados posibles de una cita."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    EN_PROCESO = "EN_PROCESO"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"
    NO_ASISTIO = "NO_ASISTIO"

    TODOS = [PENDIENTE, CONFIRMADA, EN_PROCESO, FINALIZADA, CANCELADA, NO_ASISTIO]


class EstadoGenerico:
    """Estados genéricos reutilizables (activo/inactivo)."""

    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"

    TODOS = [ACTIVO, INACTIVO]


class MetodoPago:
    """Métodos de pago aceptados por el sistema."""

    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"
    TRANSFERENCIA = "TRANSFERENCIA"
    YAPE = "YAPE"
    PLIN = "PLIN"

    TODOS = [EFECTIVO, TARJETA, TRANSFERENCIA, YAPE, PLIN]


class EstadoPago:
    """Estados posibles de un pago."""

    PENDIENTE = "PENDIENTE"
    PARCIAL = "PARCIAL"
    COMPLETO = "COMPLETO"
    ANULADO = "ANULADO"

    TODOS = [PENDIENTE, PARCIAL, COMPLETO, ANULADO]


class EstadoVenta:
    """Estados posibles de una venta."""

    COMPLETADA = "COMPLETADA"
    ANULADA = "ANULADA"

    TODOS = [COMPLETADA, ANULADA]


class TipoMovimientoInventario:
    """Tipos de movimiento de inventario."""

    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    AJUSTE = "AJUSTE"

    TODOS = [ENTRADA, SALIDA, AJUSTE]


class TipoComision:
    """Origen de una comisión."""

    SERVICIO = "SERVICIO"
    VENTA_PRODUCTO = "VENTA_PRODUCTO"

    TODOS = [SERVICIO, VENTA_PRODUCTO]


class EstadoComision:
    """Estado de pago de una comisión."""

    PENDIENTE = "PENDIENTE"
    PAGADA = "PAGADA"

    TODOS = [PENDIENTE, PAGADA]


class EstadoTicket:
    """Estados posibles de un ticket de soporte (mesa de ayuda)."""

    ABIERTO = "ABIERTO"
    EN_PROGRESO = "EN_PROGRESO"
    EN_ESPERA_CLIENTE = "EN_ESPERA_CLIENTE"
    EN_ESPERA_TERCERO = "EN_ESPERA_TERCERO"
    RESUELTO = "RESUELTO"
    CERRADO = "CERRADO"
    CANCELADO = "CANCELADO"

    TODOS = [ABIERTO, EN_PROGRESO, EN_ESPERA_CLIENTE, EN_ESPERA_TERCERO, RESUELTO, CERRADO, CANCELADO]
    ABIERTOS = [ABIERTO, EN_PROGRESO, EN_ESPERA_CLIENTE, EN_ESPERA_TERCERO]
    FINALES = [RESUELTO, CERRADO, CANCELADO]


class PrioridadTicket:
    """Prioridad de atención de un ticket."""

    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"

    TODOS = [BAJA, MEDIA, ALTA, CRITICA]


class CategoriaTicket:
    """Categoría ITIL simplificada del ticket."""

    INCIDENTE = "INCIDENTE"
    REQUERIMIENTO = "REQUERIMIENTO"
    CONSULTA = "CONSULTA"
    CAMBIO = "CAMBIO"
    PROBLEMA = "PROBLEMA"

    TODOS = [INCIDENTE, REQUERIMIENTO, CONSULTA, CAMBIO, PROBLEMA]


class CanalTicket:
    """Canal de origen de un ticket."""

    PORTAL = "PORTAL"
    CORREO = "CORREO"
    TELEFONO = "TELEFONO"
    CHAT = "CHAT"
    PRESENCIAL = "PRESENCIAL"
    INTERNO = "INTERNO"

    TODOS = [PORTAL, CORREO, TELEFONO, CHAT, PRESENCIAL, INTERNO]


class NivelSLA:
    """Nivel de servicio contratado por una empresa cliente."""

    STANDARD = "STANDARD"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

    TODOS = [STANDARD, GOLD, PLATINUM]


class TipoActivo:
    """Tipo de activo tecnológico registrado en el CMDB."""

    SERVIDOR = "SERVIDOR"
    LAPTOP = "LAPTOP"
    DESKTOP = "DESKTOP"
    IMPRESORA = "IMPRESORA"
    RED = "RED"
    LICENCIA = "LICENCIA"
    TELEFONIA = "TELEFONIA"
    OTRO = "OTRO"

    TODOS = [SERVIDOR, LAPTOP, DESKTOP, IMPRESORA, RED, LICENCIA, TELEFONIA, OTRO]


class EstadoActivo:
    """Estado operativo de un activo."""

    ACTIVO = "ACTIVO"
    EN_MANTENIMIENTO = "EN_MANTENIMIENTO"
    DADO_DE_BAJA = "DADO_DE_BAJA"

    TODOS = [ACTIVO, EN_MANTENIMIENTO, DADO_DE_BAJA]


class EstadoProyecto:
    """Estados posibles de un proyecto."""

    PLANIFICACION = "PLANIFICACION"
    EN_CURSO = "EN_CURSO"
    PAUSADO = "PAUSADO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"

    TODOS = [PLANIFICACION, EN_CURSO, PAUSADO, FINALIZADO, CANCELADO]


class EstadoTareaProyecto:
    """Estados posibles de una tarea de proyecto."""

    PENDIENTE = "PENDIENTE"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADA = "COMPLETADA"

    TODOS = [PENDIENTE, EN_PROGRESO, COMPLETADA]


class TipoContrato:
    """Tipo de contrato de servicios con una empresa cliente."""

    SOPORTE = "SOPORTE"
    BOLSA_HORAS = "BOLSA_HORAS"
    PROYECTO = "PROYECTO"
    LICENCIAMIENTO = "LICENCIAMIENTO"
    OTRO = "OTRO"

    TODOS = [SOPORTE, BOLSA_HORAS, PROYECTO, LICENCIAMIENTO, OTRO]


class EstadoContrato:
    """Estado de vigencia de un contrato."""

    VIGENTE = "VIGENTE"
    VENCIDO = "VENCIDO"
    CANCELADO = "CANCELADO"

    TODOS = [VIGENTE, VENCIDO, CANCELADO]


class TipoGuia:
    """Motivo de una guía de remisión / despacho."""

    ENTREGA_EQUIPO = "ENTREGA_EQUIPO"
    INSTALACION = "INSTALACION"
    PRESTAMO = "PRESTAMO"
    DEVOLUCION = "DEVOLUCION"
    TRASLADO_INTERNO = "TRASLADO_INTERNO"

    TODOS = [ENTREGA_EQUIPO, INSTALACION, PRESTAMO, DEVOLUCION, TRASLADO_INTERNO]


class EstadoGuia:
    """Estado del despacho."""

    EMITIDA = "EMITIDA"
    ENTREGADA = "ENTREGADA"
    ANULADA = "ANULADA"

    TODOS = [EMITIDA, ENTREGADA, ANULADA]


class AccionAuditoria:
    """Acciones registradas en la tabla de auditoría."""

    CREAR = "CREAR"
    EDITAR = "EDITAR"
    ELIMINAR = "ELIMINAR"
    CANCELAR = "CANCELAR"
    PAGAR = "PAGAR"
    LOGIN = "LOGIN"
    LOGIN_FALLIDO = "LOGIN_FALLIDO"
    LOGOUT = "LOGOUT"

    TODOS = [CREAR, EDITAR, ELIMINAR, CANCELAR, PAGAR, LOGIN, LOGIN_FALLIDO, LOGOUT]
