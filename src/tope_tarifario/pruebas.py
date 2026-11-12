"""Verificaciones con assert para la liquidación del tope tarifario."""

from datos import generar_viajes
from estrategia import compras_optimas, costo_minimo, liquidar_tope
from exhaustivo import costo_exhaustivo
from regla_actual import costo_regla_actual


def ejecutar_pruebas() -> None:
    """Comprueba límites, ejemplo manual y casos aleatorios pequeños.

    Returns:
        None. Si falla algún assert, Python muestra el caso incorrecto.
    """
    # Casos límite: nada que pagar y un solo día.
    assert costo_minimo([]) == 0
    assert costo_exhaustivo([]) == 0
    assert costo_regla_actual([]) == 0
    assert liquidar_tope([], 0) == 0

    assert costo_minimo([0]) == 0
    assert costo_minimo([1]) == 3900
    assert costo_minimo([3]) == 9500
    assert costo_exhaustivo([3]) == 9500
    assert costo_regla_actual([3]) == 9500
    assert costo_minimo([0] * 31) == 0

    # Comprueba la duración del pase mensual en meses de 30 y 31 días.
    assert costo_minimo([3] * 30) == 135000
    assert costo_minimo([3] * 31) == 144500

    # Caso desarrollado a mano en la Parte 1 del README.
    ejemplo = [1, 3, 3, 3, 3, 0, 0, 3]
    copia_ejemplo = ejemplo.copy()
    assert costo_minimo(ejemplo) == 39900
    assert costo_exhaustivo(ejemplo) == 39900
    assert costo_regla_actual(ejemplo) == 45500
    assert costo_regla_actual(ejemplo) - costo_minimo(ejemplo) == 5600
    assert compras_optimas(ejemplo) == [
        (1, "pasajes sencillos", 3900),
        (2, "pase semanal", 36000),
    ]
    assert ejemplo == copia_ejemplo

    # La devolución nunca es negativa y corresponde al mínimo exacto.
    assert liquidar_tope(ejemplo, 62400) == 22500
    assert liquidar_tope(ejemplo, 39900) == 0
    assert liquidar_tope(ejemplo, 30000) == 0

    # 30 pruebas aleatorias reproducibles, sin cambiar sus entradas.
    for indice in range(30):
        dias = (indice % 10) + 1
        viajes = generar_viajes(
            dias=dias,
            semilla=2026 + indice,
            max_viajes=6,
            probabilidad_cero=0.20,
        )
        original = viajes.copy()
        optimo = costo_minimo(viajes)
        exacto = costo_exhaustivo(viajes)
        regla = costo_regla_actual(viajes)

        assert optimo == exacto, f"Error con {viajes}: {optimo} != {exacto}"
        assert regla >= optimo, f"La regla no cubrió bien {viajes}"
        assert sum(compra[2] for compra in compras_optimas(viajes)) == optimo
        assert viajes == original, "La función modificó la entrada"

        cobrado = sum(viajes) * 3900
        assert liquidar_tope(viajes, cobrado) == max(0, cobrado - optimo)

    print(
        "Pruebas correctas: casos límite, ejemplo y 30 instancias aleatorias."
    )


if __name__ == "__main__":
    ejecutar_pruebas()