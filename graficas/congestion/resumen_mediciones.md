### Operación 3 — Mediciones experimentales y análisis

Para comparar los algoritmos de congestión, generamos listas sintéticas de saldos
netos con `generar_saldos()`, semilla `2026` y valores entre `-50` y
`50`. Cuando ejecutamos ambos algoritmos, usamos la misma lista de entrada.
Medimos con `time.perf_counter()` y reportamos la **mediana** de varias
repeticiones. La generación de datos, las verificaciones y los contadores
quedaron fuera del tiempo cronometrado. Esto representa el rendimiento del
computador que ejecutó el experimento, no el servidor real del SITVM.

Los resultados completos están en
[`graficas/congestion/resultados.csv`](graficas/congestion/resultados.csv).

![Tiempo de ejecución de los algoritmos de congestión](graficas/congestion/tiempo_vs_n.png)

![Operaciones instrumentadas de los algoritmos de congestión](graficas/congestion/operaciones_vs_n.png)

**Comparación cuando duplicamos la entrada de 1,024 a 2,048 intervalos:**

| Algoritmo | Tiempo en 1,024 (ms) | Tiempo en 2,048 (ms) | Multiplicador del tiempo | Operaciones 1,024 → 2,048 | Multiplicador de operaciones |
|---|---:|---:|---:|---:|---:|
| Búsqueda exhaustiva | 161.7441 | 704.1544 | 4.35× | 524,800 → 2,098,176 | 4.00× |
| Divide y vencerás | 3.0982 | 3.6426 | 1.18× | 13,310 → 28,670 | 2.15× |

La búsqueda exhaustiva revisa `n(n + 1) / 2` tramos y tiene crecimiento
**Θ(n²)**. Cuando duplicamos `n`, esperamos casi cuatro veces más trabajo.
Divide y vencerás resuelve dos mitades y examina los cruces, siguiendo
`T(n) = 2T(n/2) + Θ(n)`, por lo que esperamos **Θ(n log n)**.
Los tiempos pueden no crecer exactamente en esa proporción por el costo de
Python, el sistema operativo y la carga del computador. Los contadores miden
**trabajos instrumentados distintos** en cada algoritmo; conviene comparar
cómo crece cada uno, no sus cantidades absolutas entre métodos.

**Proyección al histórico indicado en el caso:** aproximadamente `166,000`
intervalos por estación y `80` estaciones. Para divide y vencerás
**sí ejecutamos** `166,000` intervalos: mediana
`0.405722 s` por estación. Para la exhaustiva
**no ejecutamos** ese tamaño: extrapolamos desde `2,048` intervalos usando
la relación exacta del número de tramos
`[n(n+1)/2]`, coherente con Θ(n²).

| Algoritmo | Tiempo por estación, 166,000 intervalos | Tiempo para 80 estaciones (secuencial) | Energía estimada para 80 estaciones (500 W) |
|---|---:|---:|---:|
| Búsqueda exhaustiva | 4,623.97 s **(estimado)** | 102.75 h **(estimado)** | 51.3774 kWh **(estimado)** |
| Divide y vencerás | 0.405722 s **(medido en este computador)** | 32.46 s **(estimado)** | 0.004508 kWh **(estimado)** |

Para energía aplicamos `kWh = 0,5 kW × tiempo en horas`.
La diferencia por ejecución completa de 80 estaciones sería aproximadamente
**51.3729 kWh** a favor de divide y vencerás en este escenario.
Si este análisis histórico se ejecutara **12 veces al año** (supuesto solo
para ilustrar, no informado por el cliente), la diferencia sería
**616.4749 kWh/año**.
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
