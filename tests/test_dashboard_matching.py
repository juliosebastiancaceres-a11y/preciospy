import pandas as pd

from dashboard import normalizar_precios, preparar_comparacion_supermercados


def test_preparar_comparacion_supermercados_detecta_equivalentes():
    precios = pd.DataFrame(
        [
            {
                "supermercado": "Stock",
                "nombre_producto": "COCA COLA 2L",
                "precio": 12000,
                "fecha_registro": "2026-05-08",
                "fecha_hora_registro": "2026-05-08T10:00:00",
            },
            {
                "supermercado": "Superseis",
                "nombre_producto": "Coca Cola 2000 ml",
                "precio": 11500,
                "fecha_registro": "2026-05-08",
                "fecha_hora_registro": "2026-05-08T10:00:00",
            },
        ]
    )

    precios = normalizar_precios(precios)
    comparacion = preparar_comparacion_supermercados(precios)

    assert len(comparacion) == 1
    fila = comparacion.iloc[0]
    assert fila["Producto comparable"] == "coca cola 2 L"
    assert fila["Supermercado más barato"] == "Superseis"
    assert fila["Coincidencia"] == "Exacta"
    assert fila["Mejor precio"] == 11500
    assert fila["Diferencia"] == 500


def test_preparar_comparacion_supermercados_detecta_match_flexible():
    precios = pd.DataFrame(
        [
            {
                "supermercado": "Stock",
                "nombre_producto": "Gaseosa Coca Cola Original Botella 2 Litros",
                "precio": 13000,
                "fecha_registro": "2026-05-08",
            },
            {
                "supermercado": "Superseis",
                "nombre_producto": "Coca-Cola sabor original gaseosa 2000ml",
                "precio": 12500,
                "fecha_registro": "2026-05-08",
            },
        ]
    )

    precios = normalizar_precios(precios)
    comparacion = preparar_comparacion_supermercados(precios)

    assert len(comparacion) == 1
    fila = comparacion.iloc[0]
    assert fila["Producto comparable"] == "coca cola original gaseosa 2 L"
    assert fila["Supermercado más barato"] == "Superseis"
    assert fila["Coincidencia"] == "Flexible"


def test_preparar_comparacion_supermercados_no_mezcla_variantes_distintas():
    precios = pd.DataFrame(
        [
            {
                "supermercado": "Stock",
                "nombre_producto": "Coca Cola Original 2L",
                "precio": 12000,
                "fecha_registro": "2026-05-08",
            },
            {
                "supermercado": "Superseis",
                "nombre_producto": "Coca Cola Zero 2L",
                "precio": 11500,
                "fecha_registro": "2026-05-08",
            },
        ]
    )

    precios = normalizar_precios(precios)
    comparacion = preparar_comparacion_supermercados(precios)

    assert comparacion.empty


def test_preparar_comparacion_supermercados_ignora_un_solo_supermercado():
    precios = pd.DataFrame(
        [
            {
                "supermercado": "Stock",
                "nombre_producto": "COCA COLA 2L",
                "precio": 12000,
                "fecha_registro": "2026-05-08",
            }
        ]
    )

    precios = normalizar_precios(precios)
    comparacion = preparar_comparacion_supermercados(precios)

    assert comparacion.empty
