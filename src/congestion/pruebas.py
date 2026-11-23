"""Pruebas de correctitud para la operación 3: franjas de congestión.

Se comparan la búsqueda exhaustiva y divide y vencerás con entradas
idénticas. Los datos son sintéticos y la semilla permite repetirlos.

Ejecutar desde la raíz del repositorio:
    python src/congestion/pruebas.py
"""

import random

from datos import SEMILLA, generar_saldos
from divide_venceras import contar_operaciones as operaciones_divide
from divide_venceras import tramo_maximo_divide_venceras
from exhaustivo import contar_operaciones as operaciones_exhaustivo
from exhaustivo import tramo_maximo_exhaustivo

Resultado = tuple[int, int, int]

# Valores y resultados definidos a mano para comprobar casos concretos.
CASOS_FIJOS: tuple[tuple[str, list[int], Resultado], ...] = (
    ("Ejemplo de la fase 1", [3, -2, 5, -1, 4, -6, 2, -1], (9, 0, 4)),
    ("Un intervalo positivo", [5], (5, 0, 0)),
    ("Un intervalo negativo", [-9], (-9, 0, 0)),
    ("Un intervalo cero", [0], (0, 0, 0)),
    ("Todos negativos", [-7, -2, -5], (-2, 1, 1)),
    ("Todos ceros", [0, 0, 0], (0, 0, 0)),
    ("Empate entre intervalos", [1, -1, 1], (1, 0, 0)),
    ("Mismo inicio, distintos finales", [2, -2, 2], (2, 0, 0)),
    ("Cero entre negativos", [-1, 0, -1], (0, 1, 1)),
    ("Mejor tramo completo", [5, -1, 5], (9, 0, 2)),
    ("Empate de sumas con cero inicial", [0, 1, -1, 1, -1], (1, 0, 1)),
    ("Mejor tramo al final", [2, -3, 4, -1, 2], (5, 2, 4)),
    ("Cero antes de la mejor suma", [0, 5], (5, 0, 1)),
    ("Cero después de la mejor suma", [3, 0], (3, 0, 0)),
    ("Dos negativos iguales", [-2, -2], (-2, 0, 0)),
    ("Empate con cero final", [1, -1, 0], (1, 0, 0)),
)


def comprobar_ambos(
    saldos: list[int],
    descripcion: str,
    esperado: Resultado | None = None,
) -> None:
    """Compara ambas respuestas, sus límites y la lista original.

    Args:
        saldos: Lista no vacía de saldos netos por intervalo.
        descripcion: Identificador del caso para detectar fallos.
        esperado: Resultado manual cuando se conoce, o None.
    """
    originales = saldos.copy()
    exhaustivo = tramo_maximo_exhaustivo(saldos)
    divide = tramo_maximo_divide_venceras(saldos)

    assert exhaustivo == divide, (
        f"{descripcion}: exhaustivo={exhaustivo}; "
        f"divide y vencerás={divide}; saldos={saldos}"
    )
    if esperado is not None:
        assert exhaustivo == esperado, (
            f"{descripcion}: obtenido={exhaustivo}; esperado={esperado}"
        )

    suma, inicio, fin = exhaustivo
    assert 0 <= inicio <= fin < len(saldos), (
        f"{descripcion}: índices fuera del periodo: {exhaustivo}"
    )
    assert suma == sum(saldos[inicio:fin + 1]), (
        f"{descripcion}: la suma no coincide con el tramo: {exhaustivo}"
    )
    assert saldos == originales, f"{descripcion}: se modificó la entrada"

    # Comprobamos el significado del contador exhaustivo sin comparar
    # directamente los dos contadores, que miden trabajos diferentes.
    n = len(saldos)
    assert operaciones_exhaustivo(saldos) == n * (n + 1) // 2
    assert operaciones_divide(saldos) > 0
    assert saldos == originales, f"{descripcion}: el contador modificó la entrada"


def probar_casos_fijos() -> int:
    """Comprueba ejemplos conocidos, negativos, ceros y empates."""
    for nombre, saldos, resultado in CASOS_FIJOS:
        comprobar_ambos(saldos, nombre, resultado)
    return len(CASOS_FIJOS)


def probar_casos_aleatorios(cantidad: int = 300) -> int:
    """Compara las estrategias en listas pequeñas reproducibles.

    Args:
        cantidad: Número de instancias de prueba, por defecto 300.

    Returns:
        Cantidad de instancias verificadas.
    """
    generador_tamanos = random.Random(SEMILLA)
    for numero in range(cantidad):
        n = generador_tamanos.randint(1, 32)
        saldos = generar_saldos(
            n=n,
            semilla=SEMILLA + numero,
            minimo=-20,
            maximo=20,
        )
        comprobar_ambos(saldos, f"Aleatorio {numero + 1} (n={n})")
    return cantidad


def probar_generador() -> None:
    """Verifica tamaño, límites, semilla y entradas inválidas."""
    a = generar_saldos(30, semilla=SEMILLA, minimo=-5, maximo=5)
    b = generar_saldos(30, semilla=SEMILLA, minimo=-5, maximo=5)
    assert a == b, "La misma semilla no reprodujo los mismos datos"
    assert len(a) == 30
    assert all(-5 <= saldo <= 5 for saldo in a)
    assert generar_saldos(4, minimo=7, maximo=7) == [7, 7, 7, 7]

    for parametros in ({"n": 0}, {"n": -2}, {"n": 3, "minimo": 5, "maximo": -5}):
        try:
            generar_saldos(**parametros)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Se esperaba ValueError en {parametros}")


def probar_entrada_vacia() -> None:
    """Verifica la precondición de lista no vacía en ambas estrategias."""
    funciones = (
        tramo_maximo_exhaustivo,
        tramo_maximo_divide_venceras,
        operaciones_exhaustivo,
        operaciones_divide,
    )
    for funcion in funciones:
        try:
            funcion([])
        except ValueError:
            pass
        else:
            raise AssertionError(f"{funcion.__name__} aceptó una lista vacía")


def ejecutar_pruebas() -> None:
    """Ejecuta las verificaciones y presenta un resumen en la terminal."""
    casos_fijos = probar_casos_fijos()
    aleatorios = probar_casos_aleatorios()
    probar_generador()
    probar_entrada_vacia()

    print("Pruebas correctas de la operación 3 — Congestión del SITVM")
    print(f"Casos fijos comprobados: {casos_fijos}")
    print(f"Instancias aleatorias reproducibles: {aleatorios}")
    print("Comprobaciones adicionales: generador y entradas inválidas")
    print("Resultado: ambos algoritmos coinciden y conservan las entradas.")


if __name__ == "__main__":
    ejecutar_pruebas()