"""Búsqueda exhaustiva del tramo de mayor congestión del SITVM.

Cada elemento de entrada es un saldo neto de pasajeros en cinco minutos.
Los índices de inicio y fin de la respuesta son inclusivos y empiezan en 0.
"""

Resultado = tuple[int, int, int]


def _es_mejor(candidata: Resultado, actual: Resultado) -> bool:
    """Determina si una solución supera a otra con el desempate acordado.

    Args:
        candidata: Tupla (suma, inicio, fin) que queremos comparar.
        actual: Mejor solución encontrada hasta el momento.

    Returns:
        True si la candidata tiene mayor suma o gana el desempate.
    """
    if candidata[0] != actual[0]:
        return candidata[0] > actual[0]
    if candidata[1] != actual[1]:
        return candidata[1] < actual[1]
    return candidata[2] < actual[2]


def _buscar(saldos: list[int], medir_operaciones: bool) -> tuple[Resultado, int]:
    """Revisa todos los tramos usando una suma acumulada por inicio.

    Args:
        saldos: Saldos netos ordenados de una estación; lista no vacía.
        medir_operaciones: Indica si se cuentan los tramos examinados.

    Returns:
        Mejor tramo y cantidad de tramos examinados, si se solicitó.

    Raises:
        ValueError: Si se recibe una lista vacía.
    """
    if not saldos:
        raise ValueError("La lista de saldos debe contener al menos un intervalo.")

    mejor: Resultado = (saldos[0], 0, 0)
    operaciones = 0

    for inicio in range(len(saldos)):
        suma = 0
        for fin in range(inicio, len(saldos)):
            suma += saldos[fin]
            candidata: Resultado = (suma, inicio, fin)
            if medir_operaciones:
                operaciones += 1
            if _es_mejor(candidata, mejor):
                mejor = candidata

    return mejor, operaciones


def tramo_maximo_exhaustivo(saldos: list[int]) -> Resultado:
    """Encuentra el tramo de saldo neto máximo mediante búsqueda exhaustiva.

    Args:
        saldos: Lista no vacía de saldos netos de cinco minutos.

    Returns:
        Tupla (suma_maxima, inicio, fin), con extremos inclusivos.
        Si hay empates, se escoge menor inicio y después menor fin.

    Raises:
        ValueError: Si la lista está vacía.
    """
    resultado, _ = _buscar(saldos, medir_operaciones=False)
    return resultado


def contar_operaciones(saldos: list[int]) -> int:
    """Cuenta cuántos tramos candidatos examina la búsqueda exhaustiva.

    Args:
        saldos: Lista no vacía de saldos netos.

    Returns:
        Número de tramos examinados: n * (n + 1) // 2.
    """
    _, operaciones = _buscar(saldos, medir_operaciones=True)
    return operaciones