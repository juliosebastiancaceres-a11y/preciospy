import pandas as pd

from dashboard import (
    formatear_fechas_faltantes,
    obtener_estado_monitoreo,
    obtener_estado_monitoreo_supermercados,
    preparar_tabla_monitoreo_supermercados,
)


def test_obtener_estado_monitoreo_detecta_historial_al_dia():
    precios = pd.DataFrame(
        {
            "fecha_registro": [
                "2026-05-08",
                "2026-05-09",
                "2026-05-10",
            ]
        }
    )

    estado = obtener_estado_monitoreo(precios, hoy="2026-05-10")

    assert estado["dias_registrados"] == 3
    assert estado["dias_calendario"] == 3
    assert estado["dias_faltantes"] == []
    assert estado["dias_sin_datos"] == 0
    assert estado["al_dia"] is True


def test_obtener_estado_monitoreo_detecta_faltantes_intermedios_y_recientes():
    precios = pd.DataFrame(
        {
            "fecha_registro": [
                "2026-05-02",
                "2026-05-03",
                "2026-05-04",
                "2026-05-05",
                "2026-05-07",
                "2026-05-08",
            ]
        }
    )

    estado = obtener_estado_monitoreo(precios, hoy="2026-05-10")

    assert estado["dias_registrados"] == 6
    assert estado["dias_calendario"] == 9
    assert [fecha.isoformat() for fecha in estado["dias_faltantes"]] == [
        "2026-05-06",
        "2026-05-09",
        "2026-05-10",
    ]
    assert estado["dias_sin_datos"] == 2
    assert estado["al_dia"] is False


def test_formatear_fechas_faltantes_limita_salida():
    fechas = pd.to_datetime(
        ["2026-05-06", "2026-05-09", "2026-05-10"]
    ).date

    assert (
        formatear_fechas_faltantes(fechas, limite=2)
        == "2026-05-06, 2026-05-09, +1 más"
    )


def test_obtener_estado_monitoreo_supermercados_detecta_huecos_independientes():
    precios = pd.DataFrame(
        [
            {"supermercado": "Stock", "fecha_registro": "2026-05-08"},
            {"supermercado": "Stock", "fecha_registro": "2026-05-10"},
            {"supermercado": "Superseis", "fecha_registro": "2026-05-07"},
            {"supermercado": "Superseis", "fecha_registro": "2026-05-08"},
        ]
    )

    estados = obtener_estado_monitoreo_supermercados(precios, hoy="2026-05-10")
    por_supermercado = {estado["supermercado"]: estado for estado in estados}

    assert [fecha.isoformat() for fecha in por_supermercado["Stock"]["dias_faltantes"]] == [
        "2026-05-09"
    ]
    assert por_supermercado["Stock"]["dias_sin_datos"] == 0
    assert [fecha.isoformat() for fecha in por_supermercado["Superseis"]["dias_faltantes"]] == [
        "2026-05-09",
        "2026-05-10",
    ]
    assert por_supermercado["Superseis"]["dias_sin_datos"] == 2


def test_preparar_tabla_monitoreo_supermercados_formatea_fechas():
    precios = pd.DataFrame(
        [
            {"supermercado": "Stock", "fecha_registro": "2026-05-08"},
            {"supermercado": "Stock", "fecha_registro": "2026-05-10"},
        ]
    )

    estados = obtener_estado_monitoreo_supermercados(precios, hoy="2026-05-10")
    tabla = preparar_tabla_monitoreo_supermercados(estados)

    assert tabla.iloc[0]["Supermercado"] == "Stock"
    assert tabla.iloc[0]["Primera fecha"] == "2026-05-08"
    assert tabla.iloc[0]["Última fecha"] == "2026-05-10"
    assert tabla.iloc[0]["Fechas faltantes"] == "2026-05-09"
