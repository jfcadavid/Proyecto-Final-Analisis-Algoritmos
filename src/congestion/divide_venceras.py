"""Divide y vencerás para encontrar la mayor congestión neta del SITVM.

Se trabaja con índices inclusivos, sin copiar las mitades de la lista.
"""

Resultado = tuple[int, int, int]


def _es_mejor(candidata: Resultado, actual: Resultado) -> bool:
    """Compara tramos por suma, posición inicial y posición final.

    Args:
        candidata: Tramo que se está evaluando.
        actual: Tramo usado como referencia.

    Returns:
        True si la candidata tiene mayor suma o gana el desempate.
    """
    if candidata[0] != actual[0]:
        return candidata[0] > actual[0]
    if candidata[1] != actual[1]:
        return candidata[1] < actual[1]
    return candidata[2] < actual[2]


def _mejor_cruce(
    saldos: list[int],
    inicio: int,
    centro: int,
    fin: int,
    contador: list[int] | None,
) -> Resultado:
    """Encuentra el mejor tramo que contiene ambos lados del centro.

    Args:
        saldos: Lista original de saldos.
        inicio: Primer índice del segmento.
        centro: Último índice de la mitad izquierda.
        fin: Último índice del segmento.
        contador: Contador opcional de operaciones instrumentadas.

    Returns:
        Mejor tramo que cruza entre centro y centro + 1.
    """
    suma = 0
    mejor_izquierda: int | None = None
    inicio_cruce = centro

    for i in range(centro, inicio - 1, -1):
        suma += saldos[i]
        if contador is not None:
            contador[0] += 1
        # En empate se escoge el comienzo más antiguo.
        if (mejor_izquierda is None or suma > mejor_izquierda
                or (suma == mejor_izquierda and i < inicio_cruce)):
            mejor_izquierda = suma
            inicio_cruce = i

    suma = 0
    mejor_derecha: int | None = None
    fin_cruce = centro + 1

    for j in range(centro + 1, fin + 1):
        suma += saldos[j]
        if contador is not None:
            contador[0] += 1
        # El primer final encontrado gana cuando hay empate.
        if mejor_derecha is None or suma > mejor_derecha:
            mejor_derecha = suma
            fin_cruce = j

    # Los dos ciclos siempre recorren al menos un elemento cada uno.
    assert mejor_izquierda is not None
    assert mejor_derecha is not None
    return (mejor_izquierda + mejor_derecha, inicio_cruce, fin_cruce)


def _resolver(
    saldos: list[int],
    inicio: int,
    fin: int,
    contador: list[int] | None,
) -> Resultado:
    """Calcula recursivamente el máximo de un segmento de la lista."""
    if inicio == fin:
        if contador is not None:
            contador[0] += 1  # Caso base resuelto.
        return (saldos[inicio], inicio, fin)

    centro = (inicio + fin) // 2
    izquierda = _resolver(saldos, inicio, centro, contador)
    derecha = _resolver(saldos, centro + 1, fin, contador)
    cruce = _mejor_cruce(saldos, inicio, centro, fin, contador)

    mejor = izquierda
    if contador is not None:
        contador[0] += 1  # Comparación con la mitad derecha.
    if _es_mejor(derecha, mejor):
        mejor = derecha
    if contador is not None:
        contador[0] += 1  # Comparación con el tramo central.
    if _es_mejor(cruce, mejor):
        mejor = cruce
    return mejor


def tramo_maximo_divide_venceras(saldos: list[int]) -> Resultado:
    """Encuentra el tramo de mayor saldo neto usando divide y vencerás.

    Args:
        saldos: Lista no vacía con los saldos netos de cinco minutos.

    Returns:
        Tupla (suma_maxima, inicio, fin) con índices inclusivos.
        En empates se elige menor inicio y, luego, menor fin.

    Raises:
        ValueError: Si la lista está vacía.
    """
    if not saldos:
        raise ValueError("La lista de saldos debe contener al menos un intervalo.")
    return _resolver(saldos, 0, len(saldos) - 1, contador=None)


def contar_operaciones(saldos: list[int]) -> int:
    """Cuenta trabajo instrumentado del algoritmo de divide y vencerás.

    Suma los elementos examinados para los cruces, los casos base y las
    dos comparaciones entre candidatos por cada llamada no trivial.

    Args:
        saldos: Lista no vacía de saldos netos.

    Returns:
        Número de operaciones según el criterio anterior.
    """
    if not saldos:
        raise ValueError("La lista de saldos debe contener al menos un intervalo.")
    contador = [0]
    _resolver(saldos, 0, len(saldos) - 1, contador)
    return contador[0]
