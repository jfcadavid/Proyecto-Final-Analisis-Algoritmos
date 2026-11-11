"""Generación reproducible de viajes diarios de tarjetas del SITVM."""

import random

SEMILLA = 2026


def generar_viajes(
    dias: int,
    semilla: int = SEMILLA,
    max_viajes: int = 5,
    probabilidad_cero: float = 0.05,
) -> list[int]:
    """Genera una instancia sintética usando una semilla fija.

    Args:
        dias: cantidad de días que tendrá la lista.
        semilla: semilla del generador aleatorio local.
        max_viajes: máximo número de viajes posibles en un día activo.
        probabilidad_cero: probabilidad de generar un día sin viajes.

    Returns:
        Lista de viajes por día. No se modifican los datos del caso real.
    """
    generador = random.Random(semilla)
    viajes: list[int] = []

    for _ in range(dias):
        if generador.random() < probabilidad_cero:
            viajes.append(0)
        else:
            viajes.append(generador.randint(1, max_viajes))

    return viajes