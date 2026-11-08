# Proyecto final — Análisis de Algoritmos

**Institución:** Instituto Tecnológico Metropolitano (ITM)  
**Curso:** Análisis de Algoritmos — 2026-2  
**Grupo:** 10 — Asíncrono  
**Caso asignado:** Caso 1 — Recaudo del transporte (SITVM)

**Integrantes:**

- Juan Felipe Cadavid Zabala
- Paula Andrea Calderón Quintero
- Juan David Velásquez Murillo

**Entregas:** Laboratorio 4 (18 de noviembre de 2026) y proyecto final (23 de noviembre de 2026).

> **Estado del documento:** Por ahora desarrollamos la **Parte 1 del Laboratorio 4: modelar y resolver a mano**. Las secciones correspondientes a programación, mediciones y la segunda operación se completarán en las siguientes etapas. Los supuestos descritos aquí deben ser revisados por los tres integrantes antes de programar.

## 1. Análisis del problema

### 1.1. ¿De qué trata nuestro caso?

Nos correspondió estudiar el Sistema Integrado de Transporte del Valle Metropolitano (SITVM), que maneja el metro, dos líneas de cable y buses alimentadores. Los usuarios pagan sus viajes con tarjetas sin contacto. Cada noche se procesan las validaciones para detectar registros repetidos, organizarlos, analizar congestiones y calcular los cobros.

El problema general es que el proceso tarda **más de 8 horas**. Las operaciones 1 y 2 deben ejecutarse dentro de una ventana de **4 horas (00:00 a 04:00)** cada noche, y la operación 4 comparte esa ventana en la noche de cierre de mes. Para el Laboratorio 4 nos corresponde trabajar específicamente en la **operación 4: liquidación del tope tarifario**. El análisis completo del proceso y la segunda operación se completarán para el proyecto final.

### 1.2. ¿Qué debemos resolver en la operación 4?

Al finalizar cada mes, el sistema debe revisar los viajes de cada tarjeta personalizada y calcular cuál habría sido la combinación **más barata** de pasajes y pases que cubriera todos esos viajes. Si a una persona le cobraron más de ese valor, se le debe devolver la diferencia como saldo de su tarjeta.

Actualmente, el programa intenta revisar todas las combinaciones posibles de pases, pero ese procedimiento no termina en un tiempo útil para las tarjetas que tienen viajes durante muchos días. En esos casos se usa una regla simplificada que combina el cobro diario con pases semanales y mensuales. Esta regla puede cobrar más del mínimo. Por eso, nuestra tarea es encontrar el **costo mínimo exacto** usando programación dinámica.

### 1.3. Entradas y unidades

La entrada principal es `viajes_por_dia`: una lista de números enteros en la que cada posición representa un día del mes y contiene la cantidad de viajes realizados ese día. Un día sin viajes se representa con `0`.

También se recibe `cobrado`, que es el total de dinero efectivamente descontado a esa tarjeta durante el mes, expresado en **pesos colombianos (COP)**, para calcular la devolución.

Las tarifas suministradas para el **perfil general** son:

| Producto | Precio (COP) | Cobertura |
|---|---:|---|
| Pasaje sencillo | $3.900 | Un viaje |
| Pase diario | $9.500 | Viajes ilimitados durante un día calendario |
| Pase semanal | $36.000 | Viajes ilimitados durante 7 días consecutivos |
| Pase mensual | $135.000 | Viajes ilimitados durante 30 días consecutivos |

El caso también indica que existen perfiles con tarifas diferenciales, pero **no proporciona sus precios numéricos**. Por eso este desarrollo manual usa únicamente el perfil general.

### 1.4. Salidas

Esperamos obtener dos resultados:

1. **Costo mínimo:** la cantidad más baja, en COP, que permite cubrir todos los viajes del periodo.
2. **Devolución:** el dinero que se debe devolver a la tarjeta si el cobro realizado fue superior al costo mínimo.

La devolución se calcula así:

```text
Devolución = max(0, cobrado - costo_mínimo)
```

Se usa `max(0, ...)` porque la devolución nunca puede ser negativa.

### 1.5. Restricciones y datos importantes del caso

- Se deben cubrir **todos** los viajes válidos, sin cobrar una validación repetida dos veces.
- El costo calculado debe ser el **mínimo exacto**, no una aproximación.
- No se debe devolver ni un peso de menos al usuario ni un peso de más frente a la diferencia que corresponde.
- La lista original de viajes no se debe modificar durante el cálculo; el caso exige conservar los datos originales de validaciones para garantizar la trazabilidad.
- Los pases cubren días **consecutivos**: 1, 7 o 30 según el producto.
- En un mes de cierre, la operación 4 comparte la ventana nocturna de cuatro horas con las operaciones 1 y 2.
- De las **3.200.000 tarjetas emitidas**, cerca de **950.000 se utilizan al menos una vez al mes**. La operación 4 debe considerar ese volumen mensual de tarjetas.
- El servidor dedicado consume aproximadamente **500 W bajo carga sostenida** y no se cuenta con procesamiento en paralelo.

Como datos del proceso completo, el cliente también informa **1.400.000 validaciones en un día hábil típico**, de las cuales entre **4 % y 9 %** pueden llegar repetidas por reenvíos de lotes. Estos datos son importantes para el contexto, pero no son entradas directas de nuestra función de programación dinámica.

La deduplicación pertenece a la operación 1 del proceso. Para este cálculo partimos de la lista de viajes válidos de una tarjeta, como establece la entrada del Laboratorio 4.

### 1.6. Supuestos que usaremos

Para que los tres programemos bajo las mismas reglas, **proponemos** estas interpretaciones. Debemos revisarlas y acordarlas entre los integrantes antes de implementarlas en el código y en las pruebas:

- La lista está organizada cronológicamente y puede tener **28, 29, 30 o 31 días** en un mes real.
- La cantidad de viajes por día es un entero no negativo.
- Un pase semanal o mensual puede comenzar en cualquier día del periodo. Si su cobertura llega más allá del último día evaluado, los días sobrantes no generan otro costo en esta liquidación.
- Cuando un día no tiene viajes, podemos avanzar al siguiente sin comprar nada.
- Los precios y el dinero cobrado se trabajan como números enteros de pesos; no se utilizan decimales.
- Si hay varias combinaciones que cuestan lo mismo, cualquiera es óptima. Para programar, conservaremos la primera alternativa que alcance ese mínimo.
- La forma exacta en que el programa actual escoge el inicio de los pases no aparece detallada en el caso. Más adelante declaramos una **interpretación de esa regla** para poder compararla; no afirmamos que sea el código real del SITVM.

## 2. Diseño de la solución

### 2.1. ¿Por qué escogimos programación dinámica?

Escogimos programación dinámica porque una compra puede afectar varios días. Si compramos un pase semanal el día 2, ya no tenemos que buscar cómo pagar los días 3 al 8. La siguiente decisión sería desde el día 9.

**Subestructura óptima:** una vez elegimos cómo cubrir el primer día pendiente, lo que queda por pagar también debe estar cubierto de la forma más barata. Si esa parte no fuera la más económica, podríamos reemplazarla y bajar el costo total.

**Subproblemas que se repiten:** distintas opciones pueden llevarnos al mismo día pendiente de pagar. Por ejemplo, el costo a partir del día 8 puede aparecer al evaluar un pase semanal desde el día 1 y también al continuar después de un día anterior. En vez de calcularlo varias veces, guardamos ese resultado en una tabla.

### 2.2. Estado, decisiones y caso base

Vamos a llamar **`C(t)`** al costo mínimo para cubrir todos los viajes **desde el día `t` hasta el final del periodo**, suponiendo que los días anteriores ya están pagos.

Si el periodo tiene `d` días, la respuesta será `C(1)`.

Cuando el día `t` tiene viajes, podemos:

- **Pagar solamente ese día:** escoger el menor entre los pasajes sencillos y el pase diario, y añadir `C(t + 1)`.
- **Comprar un pase semanal:** pagar $36.000 y continuar en `t + 7`.
- **Comprar un pase mensual:** pagar $135.000 y continuar en `t + 30`.

Por tanto, cuando hay viajes:

```text
C(t) = min(
    min(3900 × viajes[t], 9500) + C(t + 1),
    36000 + C(min(t + 7, d + 1)),
    135000 + C(min(t + 30, d + 1))
)
```

En la fórmula los días se numeran desde **1**, por lo que al implementarla en una lista de Python el número de viajes del día `t` se consulta como `viajes_por_dia[t - 1]`.

Si ese día no tiene viajes:

```text
C(t) = C(t + 1)
```

Y el **caso base** es:

```text
C(d + 1) = 0
```

Esto quiere decir que, si ya llegamos al final del periodo, no queda nada más por pagar. La expresión `min(t + duración, d + 1)` evita consultar un día fuera de la tabla.

Llenaremos la tabla **del último día hacia el primero**, porque para calcular el costo de hoy necesitamos conocer los costos de los días siguientes. También guardaremos qué compra produjo el mínimo en cada día para poder recuperar la combinación de productos.

Con un número fijo de productos, el tiempo es **Θ(d)**, porque evaluamos un número constante de opciones por día. Si guardamos costos y decisiones, el espacio utilizado es **Θ(d)**. La solución exhaustiva, en cambio, vuelve a explorar combinaciones y puede crecer exponencialmente con los días con viajes.

### 2.3. Ejemplo de ocho días resuelto a mano

Para practicar usamos un periodo **ficticio de 8 días**, que cumple la indicación del profesor de trabajar un ejemplo pequeño de entre 4 y 8 elementos. Usamos las tarifas reales del perfil general, pero la lista de viajes es inventada solo para el ejercicio:

```python
viajes_por_dia = [1, 3, 3, 3, 3, 0, 0, 3]
```

| Día | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Viajes | 1 | 3 | 3 | 3 | 3 | 0 | 0 | 3 |

Para pagar solo un día:

- Con **1 viaje**, conviene pagar $3.900, porque el pase diario vale $9.500.
- Con **3 viajes**, los pasajes sencillos costarían `3 × 3900 = 11700`, así que conviene el pase diario de $9.500.
- Con **0 viajes**, no hay nada que pagar.

Primero ponemos el caso base: **`C(9) = 0`**. Después llenamos la tabla de atrás hacia adelante.

| Día | Viajes | Pagar solo hoy + resto | Semanal + resto | Mensual + resto | C(t) |
|---:|---:|---:|---:|---:|---:|
| 9 | — | — | — | — | **$0** |
| 8 | 3 | $9.500 + $0 = $9.500 | $36.000 | $135.000 | **$9.500** |
| 7 | 0 | Sin viajes: C(8) | — | — | **$9.500** |
| 6 | 0 | Sin viajes: C(7) | — | — | **$9.500** |
| 5 | 3 | $9.500 + $9.500 = $19.000 | $36.000 | $135.000 | **$19.000** |
| 4 | 3 | $9.500 + $19.000 = $28.500 | $36.000 | $135.000 | **$28.500** |
| 3 | 3 | $9.500 + $28.500 = $38.000 | $36.000 | $135.000 | **$36.000** |
| 2 | 3 | $9.500 + $36.000 = $45.500 | $36.000 | $135.000 | **$36.000** |
| 1 | 1 | $3.900 + $36.000 = $39.900 | $36.000 + $9.500 = $45.500 | $135.000 | **$39.900** |

**Así hicimos los cálculos más importantes:**

1. **Día 8:** lo más económico es un pase diario: `C(8) = 9500`.
2. **Días 7 y 6:** no hay viajes. Por eso `C(7) = C(8) = 9500` y `C(6) = C(7) = 9500`.
3. **Día 5:** pagar solo hoy cuesta `9500 + C(6) = 19000`, menos que comprar un pase semanal o mensual. Entonces `C(5) = 19000`.
4. **Día 4:** pagar hoy y continuar cuesta `9500 + C(5) = 28500`. Entonces `C(4) = 28500`.
5. **Día 3:** pagar hoy y continuar da `9500 + C(4) = 38000`, pero un pase semanal cuesta `$36000` y cubre hasta el final de estos ocho días. Por eso `C(3) = 36000`.
6. **Día 2:** pagar hoy y seguir daría `9500 + C(3) = 45500`. El pase semanal desde el día 2 cubre hasta el día 8 por `$36000`. Así que `C(2) = 36000`.
7. **Día 1:** un viaje suelto más `C(2)` cuesta `3900 + 36000 = 39900`. El pase semanal desde el día 1 costaría `36000 + C(8) = 45500`. El mensual vale $135.000. El menor de los tres es **$39.900**.

Por lo tanto:

```text
C(1) = min(39900, 45500, 135000) = 39900
```

### 2.4. ¿Qué debemos comprar según el resultado?

La tabla nos dice cuánto pagar, pero también necesitamos saber qué productos utilizar.

Empezamos desde el día 1 y seguimos las decisiones que dieron el mínimo:

| Día | Compra | Costo |
|---|---|---:|
| 1 | Un pasaje sencillo | $3.900 |
| 2 | Un pase semanal que cubre del día 2 al 8 | $36.000 |
| **Total** | | **$39.900** |

En el día 2 se compró el pase semanal, por lo que **no compramos nada adicional en los días 3 al 8**: ya quedaron cubiertos.

Así comprobamos que el total es el mismo que obtuvimos en la tabla: **$39.900**.

Para entender la devolución, supongamos **solo como ejemplo** que al usuario le cobraron los 16 viajes individualmente, por $3.900 cada uno:

```text
Cobrado = 16 × 3900 = 62400 pesos
Costo mínimo = 39900 pesos
Devolución = 62400 - 39900 = 22500 pesos
```

En este escenario hipotético se deberían devolver **$22.500**. No estamos afirmando que ese haya sido un cobro real del SITVM.

### 2.5. Segunda operación del proyecto

**Pendiente para la entrega del 23 de noviembre de 2026.**

## 3. Implementación

**En desarrollo para el Laboratorio 4 (18 de noviembre).** Aquí agregaremos la explicación de los archivos `estrategia.py`, `exhaustivo.py`, `regla_actual.py` y `pruebas.py`, con sus enlaces al código una vez estén implementados.

**La implementación de la segunda operación queda pendiente para el 23 de noviembre.**

## 4. Evaluación del desempeño

**En desarrollo para el Laboratorio 4 (18 de noviembre).** Aquí incluiremos las pruebas, las mediciones con datos sintéticos, las gráficas, el contraste con la complejidad teórica, la extrapolación a las 950.000 tarjetas y la estimación energética. No escribimos resultados experimentales hasta ejecutar los programas.

**La evaluación de la segunda operación queda pendiente para el 23 de noviembre.**

## 5. Análisis comparativo

### 5.1. ¿Cómo interpretamos la regla actual?

El caso dice que hoy se escoge lo más barato entre pasajes sencillos y pase diario, y luego se aplican pases semanales o mensuales si la suma supera su precio. **No explica exactamente cómo se elige el día de inicio de esos pases**.

Para poder probar esa idea en nuestro trabajo, **proponemos** esta interpretación concreta, pendiente de validación por los tres integrantes:

1. Empezamos en el primer día con viajes pendientes.
2. Calculamos cuánto costaría pagar cada día por separado, escogiendo el menor valor entre viajes sencillos y pase diario.
3. Miramos si la suma de los próximos **30 días** supera $135.000. Si es así, compramos un pase mensual desde el día actual y saltamos su cobertura.
4. Si no se aplica el mensual, miramos si la suma de los próximos **7 días** supera $36.000. Si es así, compramos un pase semanal desde el día actual y saltamos su cobertura.
5. Si ninguna suma supera el precio del pase correspondiente, pagamos únicamente el día actual y seguimos al siguiente.
6. Repetimos hasta terminar el periodo. Si un día no tiene viajes, avanzamos sin pagar.

Esta es una **suposición de nuestro equipo para reproducir la regla simplificada**, no una afirmación de que el sistema real esté implementado exactamente de esa forma. La usaremos de manera consistente en el código, las pruebas y las mediciones, como permite la guía del laboratorio.

### 5.2. Contraejemplo: la regla puede cobrar de más

Usamos el mismo ejemplo de ocho días para comparar ambas estrategias:

```python
viajes_por_dia = [1, 3, 3, 3, 3, 0, 0, 3]
```

Si pagamos cada día individualmente, tenemos:

| Día | Viajes | Menor costo individual |
|---:|---:|---:|
| 1 | 1 | $3.900 |
| 2 | 3 | $9.500 |
| 3 | 3 | $9.500 |
| 4 | 3 | $9.500 |
| 5 | 3 | $9.500 |
| 6 | 0 | $0 |
| 7 | 0 | $0 |
| 8 | 3 | $9.500 |
| **Total** | **16** | **$51.400** |

**Aplicando nuestra interpretación de la regla actual:**

- Desde el **día 1**, el costo de los días 1 al 7 sumaría `3900 + 9500 + 9500 + 9500 + 9500 = 41900` pesos.
- Como $41.900 **supera** los $36.000 del pase semanal, la regla compra un pase semanal **desde el día 1**, cubriendo los días 1 al 7.
- El día 8 queda fuera del pase. Como tiene tres viajes, pagamos un pase diario de $9.500.
- El pase mensual no se aplica, porque el total individual de los ocho días ($51.400) no supera $135.000.

**Total de la regla simplificada:**

```text
36000 + 9500 = 45500 pesos
```

**En cambio, la programación dinámica encontró:**

```text
Pasaje sencillo del día 1: 3900
Pase semanal del día 2 al 8: 36000
Total óptimo: 39900 pesos
```

Comparamos:

| Estrategia | Costo |
|---|---:|
| Regla simplificada interpretada | $45.500 |
| Programación dinámica | **$39.900** |
| **Diferencia** | **$5.600** |

La regla falla en este ejemplo porque compra el pase semanal desde el día 1, aunque **comenzarlo el día 2** permite cubrir mejor los viajes. La programación dinámica sí compara esas alternativas y encuentra una combinación $5.600 más barata.

El contraejemplo muestra que **la regla simplificada definida para esta comparación no siempre garantiza el mínimo**. No demuestra por sí solo cómo se comporta una implementación del SITVM cuya lógica exacta no conocemos.

### 5.3. ¿Qué tendría que cambiar para que una estrategia voraz fuera adecuada?

Una regla de escoger lo más barato cada día sí sería suficiente **si no existieran pases que cubrieran varios días**; es decir, si solamente pudiéramos comprar pasajes sencillos y pases diarios.

En ese caso, lo que compramos hoy no afectaría lo que podemos comprar mañana. Bastaría con sumar el menor costo de cada día:

```text
Costo total = suma(min(3900 × viajes_del_dia, 9500))
```

La situación actual es distinta porque los pases semanales y mensuales unen las decisiones de varios días. Por eso preferimos la programación dinámica para encontrar el costo mínimo exacto.

### 5.4. Comparación final y recomendación

**En desarrollo para el Laboratorio 4 (18 de noviembre).** La recomendación definitiva debe apoyarse también en las pruebas y las mediciones que todavía no hemos hecho.

La comparación con la segunda operación queda **pendiente para el 23 de noviembre**.

## 6. Implicaciones éticas, sociales y ambientales

**En desarrollo para el Laboratorio 4 (18 de noviembre):** cálculo del consumo energético de la operación 4, comparación entre regla actual y programación dinámica y proyección anual, basados en mediciones reales del equipo.

**Pendiente para el 23 de noviembre:** consecuencias para los usuarios, marco normativo con fuentes, trazabilidad, crecimiento del 30 % y demás preguntas de impacto del Caso 1.

## 7. Conclusiones

**Pendiente para la entrega del 23 de noviembre de 2026.**

## 8. Cómo reproducir las pruebas y mediciones

**En desarrollo para el Laboratorio 4 (18 de noviembre).** Aquí documentaremos los comandos para preparar el entorno, ejecutar las pruebas, generar los datos sintéticos y producir las gráficas.
