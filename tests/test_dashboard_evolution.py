import pandas as pd

from dashboard import (
    normalizar_precios,
    preparar_evolucion_producto,
    preparar_opciones_evolucion,
)


def _precios_equivalentes():
    return normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Stock",
                    "nombre_producto": "COCA COLA 2L",
                    "precio": 12000,
                    "fecha_registro": "2026-05-07",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "COCA COLA 2L",
                    "precio": 12200,
                    "fecha_registro": "2026-05-08",
                },
                {
                    "supermercado": "Superseis",
                    "nombre_producto": "Coca Cola 2000 ml",
                    "precio": 11500,
                    "fecha_registro": "2026-05-07",
                },
                {
                    "supermercado": "Superseis",
                    "nombre_producto": "Coca Cola 2000 ml",
                    "precio": 11800,
                    "fecha_registro": "2026-05-08",
                },
            ]
        )
    )


def test_preparar_opciones_evolucion_usa_clave_matching():
    opciones = preparar_opciones_evolucion(_precios_equivalentes())

    assert len(opciones) == 1
    assert opciones.iloc[0]["clave_matching"] == "coca cola 2 L"
    assert opciones.iloc[0]["supermercados"] == 2
    assert opciones.iloc[0]["fechas"] == 2
    assert "coca cola 2 L" in opciones.iloc[0]["label"]


def test_preparar_evolucion_producto_compara_nombres_equivalentes():
    precios = _precios_equivalentes()
    evolucion = preparar_evolucion_producto(precios, "coca cola 2 L")

    assert len(evolucion) == 4
    assert set(evolucion["supermercado"]) == {"Stock", "Superseis"}
    assert evolucion["fecha"].nunique() == 2
    assert set(evolucion["precio_formateado"]) == {
        "₲ 12.000",
        "₲ 12.200",
        "₲ 11.500",
        "₲ 11.800",
    }


def test_preparar_evolucion_producto_retorna_vacio_si_no_hay_clave():
    evolucion = preparar_evolucion_producto(_precios_equivalentes(), "")

    assert evolucion.empty
