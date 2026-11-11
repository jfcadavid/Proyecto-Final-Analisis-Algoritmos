"""Interpretación reproducible de la regla simplificada del SITVM."""

from estrategia import (
    DIARIO,
    DIAS_MENSUAL,
    DIAS_SEMANAL,
    MENSUAL,
    PASAJE,
    SEMANAL,
)


def _resolver(viajes_por_dia: list[int]) -> tuple[int, int]:
    """Aplica la interpretación documentada en el apartado 5.1 del README.

    Primero calcula el costo individual de cada día. Desde cada día con
    viajes pendientes, compra el pase mensual si los próximos 30 días
    cuestan más que dicho pase; en caso contrario comprueba el semanal.
    Si ninguno conviene, paga solo el día actual.

    Args:
        viajes_por_dia: viajes de la tarjeta por día.

    Returns:
        Total cobrado y número de operaciones instrumentadas.
    """
    costos_diarios = [min(viajes * PASAJE, DIARIO)
                      for viajes in viajes_por_dia]
    operaciones = len(viajes_por_dia)
    cobro = 0
    indice = 0
    dias = len(viajes_por_dia)

    while indice < dias:
        operaciones += 1
        if viajes_por_dia[indice] == 0:
            indice += 1
            continue

        fin_mes = min(indice + DIAS_MENSUAL, dias)
        costo_30_dias = sum(costos_diarios[indice:fin_mes])
        operaciones += fin_mes - indice + 1

        if costo_30_dias > MENSUAL:
            cobro += MENSUAL
            indice += DIAS_MENSUAL
            continue

        fin_semana = min(indice + DIAS_SEMANAL, dias)
        costo_7_dias = sum(costos_diarios[indice:fin_semana])
        operaciones += fin_semana - indice + 1

        if costo_7_dias > SEMANAL:
            cobro += SEMANAL
            indice += DIAS_SEMANAL
        else:
            cobro += costos_diarios[indice]
            indice += 1

    return cobro, operaciones


def costo_regla_actual(viajes_por_dia: list[int]) -> int:
    """Calcula lo que cobra hoy la regla simplificada del sistema.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del mes.

    Returns:
        El costo cobrado en pesos.

    Notes:
        El caso no especifica cómo inicia cada pase. Por eso se utiliza
        la interpretación declarada en el README, no el código real del SITVM.
    """
    cobro, _ = _resolver(viajes_por_dia)
    return cobro


def contar_operaciones(viajes_por_dia: list[int]) -> int:
    """Cuenta revisiones diarias y elementos evaluados en las ventanas.

    Args:
        viajes_por_dia: viajes por cada día del periodo.

    Returns:
        Cantidad de operaciones instrumentadas en la regla simplificada.
    """
    _, operaciones = _resolver(viajes_por_dia)
    return operaciones