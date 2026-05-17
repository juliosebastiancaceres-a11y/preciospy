import pandas as pd

from dashboard import (
    convertir_a_csv,
    convertir_a_excel,
    normalizar_precios,
    obtener_rango_precios,
    preparar_exportacion_historico,
    preparar_tabla,
)


def _precios_de_prueba():
    return normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Stock",
                    "nombre_producto": "COCA COLA 2L",
                    "precio": 12000,
                    "unidad": "unidad",
                    "fecha_registro": "2026-05-08",
                    "fecha_hora_registro": "2026-05-08T10:00:00",
                    "moneda": "PYG",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "COCA COLA 2L",
                    "precio": 12500,
                    "unidad": "unidad",
                    "fecha_registro": "2026-05-07",
                    "fecha_hora_registro": "2026-05-07T10:00:00",
                    "moneda": "PYG",
                },
            ]
        )
    )


def test_preparar_exportacion_historico_incluye_campos_utiles():
    historico = preparar_exportacion_historico(_precios_de_prueba())

    assert list(historico["Fecha"]) == ["2026-05-08", "2026-05-07"]
    assert "Nombre normalizado" in historico.columns
    assert "Clave matching" in historico.columns
    assert "Precio formateado" in historico.columns
    assert historico.iloc[0]["Precio formateado"] == "₲ 12.000"


def test_obtener_rango_precios_vacio_devuelve_cero():
    precios = normalizar_precios(
        pd.DataFrame(
            columns=["supermercado", "nombre_producto", "precio", "fecha_registro"]
        )
    )

    assert obtener_rango_precios(precios) == (0, 0)


def test_normalizar_precios_omite_megashop():
    precios = normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Megashop",
                    "nombre_producto": "Producto argentino",
                    "precio": 15000,
                    "fecha_registro": "2026-05-17",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Producto paraguayo",
                    "precio": 12000,
                    "fecha_registro": "2026-05-17",
                }
            ]
        )
    )

    assert list(precios["supermercado"]) == ["Stock"]


def test_convertir_a_csv_genera_bytes_compatibles():
    tabla = preparar_tabla(_precios_de_prueba())
    contenido = convertir_a_csv(tabla)

    assert isinstance(contenido, bytes)
    assert contenido.startswith(b"\xef\xbb\xbf")
    assert "COCA COLA 2L" in contenido.decode("utf-8-sig")


def test_convertir_a_excel_genera_archivo_xlsx():
    tabla = preparar_tabla(_precios_de_prueba())
    contenido = convertir_a_excel({"Productos": tabla})

    assert isinstance(contenido, bytes)
    assert contenido.startswith(b"PK")
