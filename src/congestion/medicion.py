"""Mide los algoritmos de congestión y genera CSV, gráficas y análisis.

Se ejecuta desde la raíz del repositorio con:
    python src/congestion/medicion.py

Las mediciones usan listas sintéticas, una misma entrada para ambos
algoritmos y contadores ejecutados fuera del cronómetro.
"""

import csv
from pathlib import Path
from statistics import median
from time import perf_counter
from typing import Callable

import matplotlib

matplotlib.use("Agg")  # Permite crear PNG sin interfaz gráfica.
import matplotlib.pyplot as plt

from datos import SEMILLA, generar_saldos
from divide_venceras import contar_operaciones as operaciones_divide
from divide_venceras import tramo_maximo_divide_venceras
from exhaustivo import contar_operaciones as operaciones_exhaustivo
from exhaustivo import tramo_maximo_exhaustivo


RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "graficas" / "congestion"
TAMANOS_AMBOS = (8, 16, 32, 64, 128, 256, 512, 1024, 2048)
TAMANOS_DIVIDE = (4096, 8192, 16384, 32768, 65536, 166000)
MIN_SALDO = -50
MAX_SALDO = 50
ESTACIONES = 80
POTENCIA_KW = 0.5  # 500 W informados por el caso.
CORRIDAS_ANUALES_HIPOTETICAS = 12  # Solo escenario: no figura en el caso.

ALGORITMOS: tuple[
    tuple[str, Callable[[list[int]], tuple[int, int, int]], Callable[[list[int]], int]],
    ...,
] = (
    ("Búsqueda exhaustiva", tramo_maximo_exhaustivo, operaciones_exhaustivo),
    ("Divide y vencerás", tramo_maximo_divide_venceras, operaciones_divide),
)

CAMPOS = (
    "intervalos", "algoritmo", "semilla", "saldo_minimo", "saldo_maximo",
    "repeticiones", "tiempo_mediano_segundos", "operaciones_instrumentadas",
    "suma_maxima", "inicio", "fin",
)


def cantidad_repeticiones(nombre: str, n: int) -> int:
    """Escoge repeticiones según costo; evita repetir demasiado la exhaustiva."""
    if nombre == "Búsqueda exhaustiva":
        if n <= 128:
            return 20
        if n <= 512:
            return 10
        if n <= 1024:
            return 5
        return 3
    if n <= 512:
        return 40
    if n <= 8192:
        return 15
    return 7


def tiempo_mediano(funcion: Callable[[list[int]], tuple[int, int, int]],
                   saldos: list[int], repeticiones: int) -> float:
    """Calcula la mediana de ejecuciones individuales con perf_counter()."""
    funcion(saldos)  # Calentamiento fuera de la medición.
    duraciones: list[float] = []
    for _ in range(repeticiones):
        inicio = perf_counter()
        funcion(saldos)
        duraciones.append(perf_counter() - inicio)
    return median(duraciones)


def medir() -> list[dict[str, int | float | str]]:
    """Mide entradas compartidas y comprueba resultados antes de registrarlos."""
    resultados: list[dict[str, int | float | str]] = []
    for n in (*TAMANOS_AMBOS, *TAMANOS_DIVIDE):
        saldos = generar_saldos(
            n=n, semilla=SEMILLA, minimo=MIN_SALDO, maximo=MAX_SALDO
        )
        entrada_original = saldos.copy()
        resultado_referencia = tramo_maximo_divide_venceras(saldos)
        if n in TAMANOS_AMBOS:
            assert tramo_maximo_exhaustivo(saldos) == resultado_referencia, (
                f"Los algoritmos no coinciden para n={n}."
            )
        assert saldos == entrada_original, "Una estrategia modificó la entrada."

        for nombre, funcion, contador in ALGORITMOS:
            if nombre == "Búsqueda exhaustiva" and n not in TAMANOS_AMBOS:
                continue  # Evitamos tiempos prohibitivos en tamaños grandes.
            repeticiones = cantidad_repeticiones(nombre, n)
            tiempo = tiempo_mediano(funcion, saldos, repeticiones)
            operaciones = contador(saldos)  # Fuera del cronómetro.
            respuesta = funcion(saldos)
            assert respuesta == resultado_referencia, (
                f"Resultado diferente para {nombre}, n={n}."
            )
            assert saldos == entrada_original, "La lista original fue alterada."
            fila: dict[str, int | float | str] = {
                "intervalos": n,
                "algoritmo": nombre,
                "semilla": SEMILLA,
                "saldo_minimo": MIN_SALDO,
                "saldo_maximo": MAX_SALDO,
                "repeticiones": repeticiones,
                "tiempo_mediano_segundos": tiempo,
                "operaciones_instrumentadas": operaciones,
                "suma_maxima": respuesta[0],
                "inicio": respuesta[1],
                "fin": respuesta[2],
            }
            resultados.append(fila)
            print(
                f"n={n:>6} | {nombre:<20} | {tiempo:.8f} s "
                f"| {operaciones:>11} operaciones | suma={respuesta[0]}"
            )
    return resultados


def guardar_csv(resultados: list[dict[str, int | float | str]]) -> Path:
    """Guarda todos los valores medidos, sin redondear los tiempos del CSV."""
    destino = SALIDA / "resultados.csv"
    with destino.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(resultados)
    return destino


def guardar_grafica(resultados: list[dict[str, int | float | str]],
                    campo: str, titulo: str, ylabel: str, nombre: str) -> Path:
    """Grafica las dos estrategias con el mismo eje y escalas logarítmicas."""
    fig, eje = plt.subplots(figsize=(11, 6))
    for algoritmo, _, _ in ALGORITMOS:
        filas = [r for r in resultados if r["algoritmo"] == algoritmo]
        xs = [int(r["intervalos"]) for r in filas]
        ys = [float(r[campo]) for r in filas]
        eje.plot(xs, ys, marker="o", linewidth=1.8, label=algoritmo)
    eje.set_title(titulo)
    eje.set_xlabel("Tamaño de entrada: intervalos de 5 minutos (n)")
    eje.set_ylabel(ylabel)
    eje.set_xscale("log", base=2)
    eje.set_yscale("log")
    eje.grid(True, which="both", alpha=0.3)
    eje.legend()
    fig.tight_layout()
    destino = SALIDA / nombre
    fig.savefig(destino, dpi=180)
    plt.close(fig)
    return destino


def obtener(resultados: list[dict[str, int | float | str]],
            algoritmo: str, n: int) -> dict[str, int | float | str]:
    """Localiza una fila concreta de los experimentos."""
    for fila in resultados:
        if fila["algoritmo"] == algoritmo and fila["intervalos"] == n:
            return fila
    raise ValueError(f"No hay mediciones de {algoritmo} con n={n}.")


def guardar_resumen(resultados: list[dict[str, int | float | str]]) -> Path:
    """Redacta un análisis con cifras tomadas exclusivamente del CSV calculado."""
    n1, n2, n_real = 1024, 2048, 166000
    ex1 = obtener(resultados, "Búsqueda exhaustiva", n1)
    ex2 = obtener(resultados, "Búsqueda exhaustiva", n2)
    dv1 = obtener(resultados, "Divide y vencerás", n1)
    dv2 = obtener(resultados, "Divide y vencerás", n2)
    dv_real = obtener(resultados, "Divide y vencerás", n_real)

    def tiempo(fila: dict[str, int | float | str]) -> float:
        return float(fila["tiempo_mediano_segundos"])

    def trabajo(fila: dict[str, int | float | str]) -> int:
        return int(fila["operaciones_instrumentadas"])

    # La exhaustiva examina exactamente n*(n+1)/2 tramos.
    # Proyectamos su tiempo conservando el costo medio por tramo del tamaño 2048.
    tramos_real = n_real * (n_real + 1) // 2
    tramos_referencia = n2 * (n2 + 1) // 2
    ex_seg_real_estimado = tiempo(ex2) * tramos_real / tramos_referencia
    dv_seg_real_medido = tiempo(dv_real)
    ex_seg_80 = ex_seg_real_estimado * ESTACIONES
    dv_seg_80 = dv_seg_real_medido * ESTACIONES
    ex_kwh = POTENCIA_KW * ex_seg_80 / 3600
    dv_kwh = POTENCIA_KW * dv_seg_80 / 3600
    diferencia_kwh = ex_kwh - dv_kwh
    ratio_t_ex = tiempo(ex2) / tiempo(ex1)
    ratio_t_dv = tiempo(dv2) / tiempo(dv1)
    ratio_op_ex = trabajo(ex2) / trabajo(ex1)
    ratio_op_dv = trabajo(dv2) / trabajo(dv1)

    contenido = f"""### Operación 3 — Mediciones experimentales y análisis

Para comparar los algoritmos de congestión, generamos listas sintéticas de saldos
netos con `generar_saldos()`, semilla `{SEMILLA}` y valores entre `{MIN_SALDO}` y
`{MAX_SALDO}`. Cuando ejecutamos ambos algoritmos, usamos la misma lista de entrada.
Medimos con `time.perf_counter()` y reportamos la **mediana** de varias
repeticiones. La generación de datos, las verificaciones y los contadores
quedaron fuera del tiempo cronometrado. Esto representa el rendimiento del
computador que ejecutó el experimento, no el servidor real del SITVM.

Los resultados completos están en
[`graficas/congestion/resultados.csv`](graficas/congestion/resultados.csv).

![Tiempo de ejecución de los algoritmos de congestión](graficas/congestion/tiempo_vs_n.png)

![Operaciones instrumentadas de los algoritmos de congestión](graficas/congestion/operaciones_vs_n.png)

**Comparación cuando duplicamos la entrada de {n1:,} a {n2:,} intervalos:**

| Algoritmo | Tiempo en {n1:,} (ms) | Tiempo en {n2:,} (ms) | Multiplicador del tiempo | Operaciones {n1:,} → {n2:,} | Multiplicador de operaciones |
|---|---:|---:|---:|---:|---:|
| Búsqueda exhaustiva | {1000*tiempo(ex1):.4f} | {1000*tiempo(ex2):.4f} | {ratio_t_ex:.2f}× | {trabajo(ex1):,} → {trabajo(ex2):,} | {ratio_op_ex:.2f}× |
| Divide y vencerás | {1000*tiempo(dv1):.4f} | {1000*tiempo(dv2):.4f} | {ratio_t_dv:.2f}× | {trabajo(dv1):,} → {trabajo(dv2):,} | {ratio_op_dv:.2f}× |

La búsqueda exhaustiva revisa `n(n + 1) / 2` tramos y tiene crecimiento
**Θ(n²)**. Cuando duplicamos `n`, esperamos casi cuatro veces más trabajo.
Divide y vencerás resuelve dos mitades y examina los cruces, siguiendo
`T(n) = 2T(n/2) + Θ(n)`, por lo que esperamos **Θ(n log n)**.
Los tiempos pueden no crecer exactamente en esa proporción por el costo de
Python, el sistema operativo y la carga del computador. Los contadores miden
**trabajos instrumentados distintos** en cada algoritmo; conviene comparar
cómo crece cada uno, no sus cantidades absolutas entre métodos.

**Proyección al histórico indicado en el caso:** aproximadamente `{n_real:,}`
intervalos por estación y `{ESTACIONES}` estaciones. Para divide y vencerás
**sí ejecutamos** `{n_real:,}` intervalos: mediana
`{dv_seg_real_medido:.6f} s` por estación. Para la exhaustiva
**no ejecutamos** ese tamaño: extrapolamos desde `{n2:,}` intervalos usando
la relación exacta del número de tramos
`[n(n+1)/2]`, coherente con Θ(n²).

| Algoritmo | Tiempo por estación, {n_real:,} intervalos | Tiempo para {ESTACIONES} estaciones (secuencial) | Energía estimada para {ESTACIONES} estaciones (500 W) |
|---|---:|---:|---:|
| Búsqueda exhaustiva | {ex_seg_real_estimado:,.2f} s **(estimado)** | {ex_seg_80/3600:,.2f} h **(estimado)** | {ex_kwh:,.4f} kWh **(estimado)** |
| Divide y vencerás | {dv_seg_real_medido:,.6f} s **(medido en este computador)** | {dv_seg_80:,.2f} s **(estimado)** | {dv_kwh:,.6f} kWh **(estimado)** |

Para energía aplicamos `kWh = 0,5 kW × tiempo en horas`.
La diferencia por ejecución completa de 80 estaciones sería aproximadamente
**{diferencia_kwh:,.4f} kWh** a favor de divide y vencerás en este escenario.
Si este análisis histórico se ejecutara **12 veces al año** (supuesto solo
para ilustrar, no informado por el cliente), la diferencia sería
**{diferencia_kwh*CORRIDAS_ANUALES_HIPOTETICAS:,.4f} kWh/año**.
Sin una periodicidad real no podemos asignar un ahorro anual definitivo.

**Límite de interpretación:** el caso fija una ventana obligatoria de cuatro
horas para las operaciones 1 y 2, y para la operación 4 en el cierre mensual;
**no indica esa misma ventana como obligación independiente de la operación 3**.
Podemos tomar cuatro horas como referencia de comparación, no como requisito
verificado de Planeación. Tampoco conocemos los tiempos del servidor real ni
el costo de lectura y preparación de los registros originales.

Un aumento del 30 % en las **validaciones diarias** no implica por sí solo un
30 % más de intervalos por estación: los intervalos siguen siendo de cinco
minutos. Si el número de intervalos por estación sí creciera 30 %, el análisis
teórico predice un factor cercano a `1,3² = 1,69` para la exhaustiva y
`1,3 × log₂(1,3n)/log₂(n)` para divide y vencerás. El número de nuevas
estaciones también afectaría el tiempo total y debe medirse aparte.
"""
    destino = SALIDA / "resumen_mediciones.md"
    destino.write_text(contenido, encoding="utf-8")
    return destino


def main() -> None:
    """Ejecuta las mediciones y crea todos los archivos del informe."""
    SALIDA.mkdir(parents=True, exist_ok=True)
    resultados = medir()
    archivos = [
        guardar_csv(resultados),
        guardar_grafica(
            resultados, "tiempo_mediano_segundos",
            "Congestión: tiempo de ejecución por algoritmo",
            "Tiempo mediano por ejecución (segundos, escala log)",
            "tiempo_vs_n.png",
        ),
        guardar_grafica(
            resultados, "operaciones_instrumentadas",
            "Congestión: operaciones instrumentadas por algoritmo",
            "Operaciones instrumentadas (escala log)",
            "operaciones_vs_n.png",
        ),
        guardar_resumen(resultados),
    ]
    print("\nArchivos creados:")
    for ruta in archivos:
        print(f" - {ruta}")


if __name__ == "__main__":
    main()
