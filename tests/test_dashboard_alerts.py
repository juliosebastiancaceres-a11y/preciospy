import pandas as pd

from dashboard import (
    normalizar_precios,
    preparar_alertas_precios,
    preparar_tabla_alertas,
)


def test_preparar_alertas_precios_detecta_minimo_historico():
    precios = normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Arroz 1kg",
                    "precio": 10000,
                    "fecha_registro": "2026-05-07",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Arroz 1kg",
                    "precio": 9000,
                    "fecha_registro": "2026-05-08",
                },
            ]
        )
    )

    alertas = preparar_alertas_precios(precios)

    assert len(alertas) == 1
    assert alertas.iloc[0]["Alerta"] == "Mínimo histórico"
    assert alertas.iloc[0]["Variación"] == -1000
    assert round(alertas.iloc[0]["Variación %"], 1) == -10.0


def test_preparar_alertas_precios_detecta_subida_relevante():
    precios = normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Superseis",
                    "nombre_producto": "Aceite 900ml",
                    "precio": 15000,
                    "fecha_registro": "2026-05-07",
                },
                {
                    "supermercado": "Superseis",
                    "nombre_producto": "Aceite 900ml",
                    "precio": 16500,
                    "fecha_registro": "2026-05-08",
                },
            ]
        )
    )

    alertas = preparar_alertas_precios(precios)

    assert len(alertas) == 1
    assert alertas.iloc[0]["Alerta"] == "Subió"
    assert alertas.iloc[0]["Variación"] == 1500
    assert round(alertas.iloc[0]["Variación %"], 1) == 10.0


def test_preparar_alertas_precios_detecta_bajada_relevante_no_minima():
    precios = normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Harina 1kg",
                    "precio": 9000,
                    "fecha_registro": "2026-05-06",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Harina 1kg",
                    "precio": 12000,
                    "fecha_registro": "2026-05-07",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Harina 1kg",
                    "precio": 11000,
                    "fecha_registro": "2026-05-08",
                },
            ]
        )
    )

    alertas = preparar_alertas_precios(precios)

    assert len(alertas) == 1
    assert alertas.iloc[0]["Alerta"] == "Bajó"
    assert alertas.iloc[0]["Variación"] == -1000
    assert round(alertas.iloc[0]["Variación %"], 1) == -8.3


def test_preparar_alertas_precios_ignora_cambios_pequenos():
    precios = normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Leche 1L",
                    "precio": 10000,
                    "fecha_registro": "2026-05-07",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Leche 1L",
                    "precio": 10200,
                    "fecha_registro": "2026-05-08",
                },
            ]
        )
    )

    alertas = preparar_alertas_precios(precios)

    assert alertas.empty


def test_preparar_tabla_alertas_formatea_precios_y_porcentajes():
    precios = normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Arroz 1kg",
                    "precio": 10000,
                    "fecha_registro": "2026-05-07",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Arroz 1kg",
                    "precio": 9000,
                    "fecha_registro": "2026-05-08",
                },
            ]
        )
    )

    tabla = preparar_tabla_alertas(preparar_alertas_precios(precios))

    assert tabla.iloc[0]["Precio anterior"] == "₲ 10.000"
    assert tabla.iloc[0]["Precio actual"] == "₲ 9.000"
    assert tabla.iloc[0]["Variación"] == "-₲ 1.000"
    assert tabla.iloc[0]["Variación %"] == "-10.0%"
