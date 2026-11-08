"""Liquidación del tope tarifario de una tarjeta."""

PASAJE = 3900
DIARIO = 9500
SEMANAL = 36000
MENSUAL = 135000

DIAS_SEMANAL = 7
DIAS_MENSUAL = 30


def _resolver(
    viajes_por_dia: list[int],
) -> tuple[list[int], list[str], int]:
    """Construye la tabla de costos mínimos de derecha a izquierda.

    Args:
        viajes_por_dia: cantidad de viajes en cada día del periodo.

    Returns:
        Tabla de costos, decisiones tomadas y alternativas evaluadas.
    """
    dias = len(viajes_por_dia)
    costos = [0] * (dias + 1)
    decisiones = [""] * dias
    operaciones = 0

    for indice in range(dias - 1, -1, -1):
        viajes = viajes_por_dia[indice]

        if viajes == 0:
            costos[indice] = costos[indice + 1]
            decisiones[indice] = "sin_viajes"
            operaciones += 1
            continue

        sencillos = viajes * PASAJE
        precio_dia = min(sencillos, DIARIO)
        mejor = precio_dia + costos[indice + 1]
        opcion = "sencillo" if sencillos <= DIARIO else "diario"
        operaciones += 1

        siguiente_semana = min(indice + DIAS_SEMANAL, dias)
        costo_semanal = SEMANAL + costos[siguiente_semana]
        operaciones += 1
        if costo_semanal < mejor:
            mejor = costo_semanal
            opcion = "semanal"

        siguiente_mes = min(indice + DIAS_MENSUAL, dias)
        costo_mensual = MENSUAL + costos[siguiente_mes]
        operaciones += 1
        if costo_mensual < mejor:
            mejor = costo_mensual
            opcion = "mensual"

        costos[indice] = mejor
        decisiones[indice] = opcion

    return costos, decisiones, operaciones


def costo_minimo(viajes_por_dia: list[int]) -> int:
    """Calcula el costo de la combinación más barata que cubre los viajes.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del mes. El índice 0
            es el primer día; un día sin viajes vale 0.

    Returns:
        El costo mínimo en pesos.
    """
    costos, _, _ = _resolver(viajes_por_dia)
    return costos[0]


def liquidar_tope(viajes_por_dia: list[int], cobrado: int) -> int:
    """Calcula la devolución que corresponde al usuario.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del mes.
        cobrado: pesos que se le cobraron durante el mes.

    Returns:
        La diferencia entre lo cobrado y el costo mínimo, nunca negativa.
    """
    return max(0, cobrado - costo_minimo(viajes_por_dia))


def compras_optimas(viajes_por_dia: list[int]) -> list[tuple[int, str, int]]:
    """Recupera una combinación de productos que alcanza el costo mínimo.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del mes.

    Returns:
        Compras como (día empezando en 1, producto, precio en pesos).
        Los días sin viajes no generan una compra.
    """
    _, decisiones, _ = _resolver(viajes_por_dia)
    compras: list[tuple[int, str, int]] = []
    indice = 0

    while indice < len(viajes_por_dia):
        opcion = decisiones[indice]
        dia = indice + 1

        if opcion == "sin_viajes":
            indice += 1
        elif opcion == "sencillo":
            precio = viajes_por_dia[indice] * PASAJE
            compras.append((dia, "pasajes sencillos", precio))
            indice += 1
        elif opcion == "diario":
            compras.append((dia, "pase diario", DIARIO))
            indice += 1
        elif opcion == "semanal":
            compras.append((dia, "pase semanal", SEMANAL))
            indice += DIAS_SEMANAL
        else:
            compras.append((dia, "pase mensual", MENSUAL))
            indice += DIAS_MENSUAL

    return compras


def contar_operaciones(viajes_por_dia: list[int]) -> int:
    """Cuenta las alternativas evaluadas por la programación dinámica.

    Args:
        viajes_por_dia: viajes por cada día del periodo.

    Returns:
        Número de alternativas revisadas (incluye saltos por día vacío).
    """
    _, _, operaciones = _resolver(viajes_por_dia)
    return operaciones
