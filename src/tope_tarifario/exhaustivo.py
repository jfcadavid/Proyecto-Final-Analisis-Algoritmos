"""Búsqueda exhaustiva para comprobar el costo mínimo en casos pequeños."""

from estrategia import (
    DIARIO,
    DIAS_MENSUAL,
    DIAS_SEMANAL,
    MENSUAL,
    PASAJE,
    SEMANAL,
)


def _resolver(viajes_por_dia: list[int]) -> tuple[int, int]:
    """Prueba todas las decisiones sin memoización.

    Args:
        viajes_por_dia: viajes de la tarjeta por día.

    Returns:
        Costo óptimo y cantidad de alternativas consideradas.
    """
    operaciones = 0
    dias = len(viajes_por_dia)

    def explorar(indice: int) -> int:
        """Explora recursivamente las maneras de cubrir el resto del periodo.

        Args:
            indice: índice del primer día que no ha quedado cubierto.

        Returns:
            Menor costo posible desde ese día hasta el final.
        """
        nonlocal operaciones

        if indice >= dias:
            return 0

        viajes = viajes_por_dia[indice]
        if viajes == 0:
            operaciones += 1
            return explorar(indice + 1)

        operaciones += 3
        pagar_dia = min(viajes * PASAJE, DIARIO) + explorar(indice + 1)
        pase_semana = SEMANAL + explorar(indice + DIAS_SEMANAL)
        pase_mes = MENSUAL + explorar(indice + DIAS_MENSUAL)
        return min(pagar_dia, pase_semana, pase_mes)

    return explorar(0), operaciones


def costo_exhaustivo(viajes_por_dia: list[int]) -> int:
    """Calcula el mismo costo probando todas las combinaciones de productos.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del mes.

    Returns:
        El costo mínimo en pesos.

    Notes:
        No usa memoización. Ejecutar solo en instancias pequeñas.
    """
    costo, _ = _resolver(viajes_por_dia)
    return costo


def contar_operaciones(viajes_por_dia: list[int]) -> int:
    """Cuenta las alternativas exploradas por el algoritmo exhaustivo.

    Args:
        viajes_por_dia: viajes de la tarjeta por día.

    Returns:
        Número de alternativas evaluadas, incluidas las repetidas.
    """
    _, operaciones = _resolver(viajes_por_dia)
    return operaciones
