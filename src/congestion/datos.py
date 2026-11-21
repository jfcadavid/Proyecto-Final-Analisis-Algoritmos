"""Generación reproducible de saldos netos ficticios para el SITVM."""

import random

SEMILLA = 2026


def generar_saldos(
    n: int,
    semilla: int = SEMILLA,
    minimo: int = -50,
    maximo: int = 50,
) -> list[int]:
    """Genera saldos netos enteros en intervalos consecutivos de cinco minutos.

    Los números son sintéticos: no representan mediciones del SITVM.
    Usar los mismos parámetros y semilla reproduce exactamente la lista.

    Args:
        n: Cantidad de intervalos a generar, al menos uno.
        semilla: Semilla del generador de números pseudoaleatorios.
        minimo: Saldo mínimo permitido por intervalo.
        maximo: Saldo máximo permitido por intervalo.

    Returns:
        Lista de n saldos enteros, positivos, negativos o cero.

    Raises:
        ValueError: Si n es menor que uno o minimo supera maximo.
    """
    if n < 1:
        raise ValueError("La cantidad de intervalos debe ser mayor que cero.")
    if minimo > maximo:
        raise ValueError("El saldo mínimo no puede superar el máximo.")
    generador = random.Random(semilla)
    return [generador.randint(minimo, maximo) for _ in range(n)]
