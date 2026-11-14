"""Experimentos reproducibles para la liquidación del tope del SITVM.

Los algoritmos se comparan con las mismas listas sintéticas de viajes.
Se miden los periodos pequeños con las tres soluciones; para periodos
mucho mayores se omite la búsqueda exhaustiva por su alto costo.
"""

import csv
from collections.abc import Callable
from pathlib import Path
from statistics import mean
from time import perf_counter

import matplotlib.pyplot as plt

from datos import SEMILLA, generar_viajes
from estrategia import contar_operaciones as operaciones_dinamica
from estrategia import costo_minimo
from exhaustivo import contar_operaciones as operaciones_exhaustiva
from exhaustivo import costo_exhaustivo
from regla_actual import contar_operaciones as operaciones_regla
from regla_actual import costo_regla_actual

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "graficas" / "tope_tarifario"

# Nueve tamaños pequeños para comparar los tres algoritmos.
# Incluye tamaños que se duplican: 4-8, 8-16 y 16-32.
TAMANOS_CON_EXHAUSTIVO = (4, 8, 12, 16, 24, 28, 30, 31, 32)

# Tamaños grandes para estudiar el crecimiento de los algoritmos.
# En estos tamaños no se ejecuta la búsqueda exhaustiva.
TAMANOS_ESCALABILIDAD = (64, 128, 256, 512, 1024, 4096, 16384)

MAX_VIAJES = 5
PROBABILIDAD_CERO = 0.0  # Todos los días tienen viajes.

ALGORITMOS: tuple[
    tuple[str, Callable[[list[int]], int], Callable[[list[int]], int]],
    ...,
] = (
    ("Programación dinámica", costo_minimo, operaciones_dinamica),
    ("Regla simplificada", costo_regla_actual, operaciones_regla),
    ("Búsqueda exhaustiva", costo_exhaustivo, operaciones_exhaustiva),
)


def repeticiones_para(algoritmo: str, dias: int) -> int:
    """Selecciona repeticiones sin sobrecargar la búsqueda exhaustiva.

    Args:
        algoritmo: Nombre de la estrategia a medir.
        dias: Tamaño de la instancia.

    Returns:
        Número de repeticiones de la medición.
    """
    if algoritmo == "Búsqueda exhaustiva":
        if dias <= 32:
            return 20
        return 3

    if dias <= 128:
        return 200

    if dias <= 4096:
        return 30

    return 8


def medir_tiempo(
    funcion: Callable[[list[int]], int],
    viajes: list[int],
    repeticiones: int,
) -> float:
    """Cronometra únicamente las llamadas al algoritmo.

    Los datos se generan antes de comenzar la medición.

    Args:
        funcion: Algoritmo cuyo tiempo se quiere medir.
        viajes: Lista sintética compartida entre los algoritmos.
        repeticiones: Cantidad de ejecuciones que se promedian.

    Returns:
        Tiempo medio por ejecución, en segundos.
    """
    tiempos: list[float] = []

    for _ in range(repeticiones):
        inicio = perf_counter()
        funcion(viajes)
        tiempos.append(perf_counter() - inicio)

    return mean(tiempos)


def medir() -> list[dict[str, int | float | str]]:
    """Mide las tres soluciones y compara sus resultados.

    Para cada tamaño se genera una lista con semilla fija.
    La búsqueda exhaustiva solo se usa con tamaños pequeños.

    Returns:
        Registros con tiempos, operaciones y costos calculados.
    """
    resultados: list[dict[str, int | float | str]] = []

    tamanos = TAMANOS_CON_EXHAUSTIVO + TAMANOS_ESCALABILIDAD

    for dias in tamanos:

        # Generamos los datos fuera del cronómetro.
        viajes = generar_viajes(
            dias=dias,
            semilla=SEMILLA,
            max_viajes=MAX_VIAJES,
            probabilidad_cero=PROBABILIDAD_CERO,
        )

        assert len(viajes) == dias
        assert all(cantidad > 0 for cantidad in viajes)

        # Calculamos el costo óptimo mediante programación dinámica.
        optimo = costo_minimo(viajes)

        # Calculamos el resultado de la regla actual.
        regla = costo_regla_actual(viajes)

        assert regla >= optimo, (
            "La regla actual no debe mejorar el costo óptimo"
        )

        # Comprobamos el resultado con búsqueda exhaustiva.
        if dias in TAMANOS_CON_EXHAUSTIVO:
            exacto = costo_exhaustivo(viajes)

            assert exacto == optimo, (
                f"Para d={dias}: "
                f"dinámica={optimo}, exhaustiva={exacto}"
            )

        # Medimos cada algoritmo con la misma lista de viajes.
        for nombre, funcion, contador in ALGORITMOS:

            if (
                nombre == "Búsqueda exhaustiva"
                and dias not in TAMANOS_CON_EXHAUSTIVO
            ):
                continue

            repeticiones = repeticiones_para(nombre, dias)

            # Medimos solamente el tiempo del algoritmo.
            tiempo = medir_tiempo(
                funcion,
                viajes,
                repeticiones,
            )

            # Contamos las operaciones fuera del cronómetro.
            operaciones = contador(viajes)

            # Comprobamos nuevamente el costo obtenido.
            costo = funcion(viajes)

            assert costo >= optimo

            if nombre != "Regla simplificada":
                assert costo == optimo

            resultados.append({
                "dias": dias,
                "dias_con_viajes": sum(
                    cantidad > 0 for cantidad in viajes
                ),
                "semilla": SEMILLA,
                "algoritmo": nombre,
                "repeticiones": repeticiones,
                "tiempo_medio_segundos": tiempo,
                "operaciones_instrumentadas": operaciones,
                "costo_pesos": costo,
                "diferencia_frente_optimo_pesos": costo - optimo,
            })

            print(
                f"d={dias:>5} | {nombre:<22} | "
                f"{tiempo:.8f} s | "
                f"{operaciones:>10} operaciones | "
                f"costo=${costo:,}"
            )

    return resultados


def guardar_csv(
    resultados: list[dict[str, int | float | str]],
) -> None:
    """Guarda los resultados de los experimentos en un CSV.

    Args:
        resultados: Registros obtenidos durante las mediciones.

    Returns:
        None.
    """
    ruta = SALIDA / "resultados.csv"

    with ruta.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as archivo:

        escritor = csv.DictWriter(
            archivo,
            fieldnames=[
                "dias",
                "dias_con_viajes",
                "semilla",
                "algoritmo",
                "repeticiones",
                "tiempo_medio_segundos",
                "operaciones_instrumentadas",
                "costo_pesos",
                "diferencia_frente_optimo_pesos",
            ],
        )

        escritor.writeheader()
        escritor.writerows(resultados)


def guardar_grafica(
    resultados: list[dict[str, int | float | str]],
    campo: str,
    titulo: str,
    etiqueta_y: str,
    archivo: str,
) -> None:
    """Genera una gráfica comparativa de los algoritmos.

    Args:
        resultados: Mediciones realizadas.
        campo: Columna que se representa en el eje vertical.
        titulo: Título de la gráfica.
        etiqueta_y: Nombre y unidad del eje vertical.
        archivo: Nombre del archivo PNG.

    Returns:
        None.
    """
    fig, eje = plt.subplots(figsize=(11, 6))

    for nombre, _, _ in ALGORITMOS:

        filas = [
            fila
            for fila in resultados
            if fila["algoritmo"] == nombre
        ]

        dias = [
            int(fila["dias"])
            for fila in filas
        ]

        valores = [
            float(fila[campo])
            for fila in filas
        ]

        eje.plot(
            dias,
            valores,
            marker="o",
            linewidth=1.8,
            label=nombre,
        )

    eje.set_title(titulo)

    eje.set_xlabel(
        "Tamaño de entrada: días del periodo (d)"
    )

    eje.set_ylabel(etiqueta_y)

    eje.set_xscale("log", base=2)

    marcas = (
        4, 8, 16, 32, 64, 128,
        256, 512, 1024, 4096, 16384,
    )

    eje.set_xticks(
        marcas,
        labels=[str(numero) for numero in marcas],
    )

    eje.set_yscale("log")

    eje.grid(
        True,
        which="both",
        alpha=0.3,
    )

    eje.legend()

    fig.tight_layout()

    fig.savefig(
        SALIDA / archivo,
        dpi=180,
    )

    plt.close(fig)


def main() -> None:
    """Ejecuta los experimentos y genera los archivos.

    Returns:
        None.
    """
    SALIDA.mkdir(
        parents=True,
        exist_ok=True,
    )

    resultados = medir()

    guardar_csv(resultados)

    guardar_grafica(
        resultados,
        "tiempo_medio_segundos",
        "Parte 3: tiempo medio de liquidación por algoritmo",
        "Tiempo medio por ejecución (segundos, escala log)",
        "tiempo_vs_n.png",
    )

    guardar_grafica(
        resultados,
        "operaciones_instrumentadas",
        "Parte 3: trabajo instrumentado por algoritmo",
        "Operaciones instrumentadas (conteo, escala log)",
        "operaciones_vs_n.png",
    )

    print(
        f"\nArchivos guardados en: {SALIDA}"
    )


if __name__ == "__main__":
    main()
