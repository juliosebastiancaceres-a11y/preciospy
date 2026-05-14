import pandas as pd

from dashboard import (
    filtrar_evolucion_supermercados,
    normalizar_precios,
    obtener_configuracion_evolucion,
    obtener_colores_supermercados,
    preparar_evolucion_producto,
    preparar_opciones_evolucion,
    preparar_resumen_evolucion,
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


def test_filtrar_evolucion_supermercados_limita_series():
    evolucion = preparar_evolucion_producto(_precios_equivalentes(), "coca cola 2 L")

    filtrada = filtrar_evolucion_supermercados(evolucion, ["Stock"])

    assert set(filtrada["supermercado"]) == {"Stock"}
    assert len(filtrada) == 2


def test_obtener_configuracion_evolucion_prepara_modo_comparar():
    evolucion = preparar_evolucion_producto(_precios_equivalentes(), "coca cola 2 L")

    filtrada, comparar = obtener_configuracion_evolucion(
        evolucion,
        "Comparar supermercados",
        ["Stock", "Superseis"],
    )

    assert comparar is True
    assert set(filtrada["supermercado"]) == {"Stock", "Superseis"}


def test_obtener_colores_supermercados_reconocibles():
    dominio, colores = obtener_colores_supermercados(
        ["Biggie", "Los Jardines", "Casa Rica", "Stock", "Superseis"]
    )

    assert dict(zip(dominio, colores)) == {
        "Biggie": "#C6051D",
        "Los Jardines": "#D6A300",
        "Casa Rica": "#101828",
        "Stock": "#0038A8",
        "Superseis": "#2E7D32",
    }


def test_preparar_resumen_evolucion_calcula_variacion():
    evolucion = preparar_evolucion_producto(_precios_equivalentes(), "coca cola 2 L")
    resumen = preparar_resumen_evolucion(evolucion)
    stock = resumen[resumen["Supermercado"] == "Stock"].iloc[0]

    assert stock["Último precio"] == "₲ 12.200"
    assert stock["Precio mínimo"] == "₲ 12.000"
    assert stock["Variación"] == "+₲ 200"
    assert stock["Variación %"] == "+1.7%"
