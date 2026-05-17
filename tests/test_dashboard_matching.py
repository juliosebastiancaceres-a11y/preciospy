import pandas as pd

from dashboard import normalizar_precios, preparar_comparacion_supermercados
from dashboard import preparar_tabla_comparacion
from dashboard import filtrar_por_busqueda_inteligente, preparar_terminos_busqueda


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
    assert fila["Confianza"] == "Alta"
    assert fila["Supermercados comparados"] == 2
    assert "Stock: COCA COLA 2L" in fila["Productos comparados"]
    assert "Superseis: Coca Cola 2000 ml" in fila["Productos comparados"]
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
    assert fila["Producto comparable"] == "coca cola original 2 L"
    assert fila["Supermercado más barato"] == "Superseis"
    assert fila["Coincidencia"] == "Flexible"
    assert fila["Confianza"] == "Media"


def test_preparar_tabla_comparacion_formatea_precios_y_prioriza_columnas():
    precios = normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Stock",
                    "nombre_producto": "COCA COLA 2L",
                    "precio": 12000,
                    "fecha_registro": "2026-05-08",
                },
                {
                    "supermercado": "Superseis",
                    "nombre_producto": "Coca Cola 2000 ml",
                    "precio": 11500,
                    "fecha_registro": "2026-05-08",
                },
            ]
        )
    )
    comparacion = preparar_comparacion_supermercados(precios)

    tabla = preparar_tabla_comparacion(comparacion)

    assert list(tabla.columns[:4]) == [
        "Producto comparable",
        "Coincidencia",
        "Confianza",
        "Supermercados comparados",
    ]
    assert tabla.iloc[0]["Mejor precio"] == "₲ 11.500"
    assert tabla.iloc[0]["Diferencia"] == "₲ 500"
    assert tabla.iloc[0]["Ahorro %"] == "4.2%"


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


def test_preparar_terminos_busqueda_agrupa_numero_y_unidad():
    assert preparar_terminos_busqueda("coca 1l") == ["coca", "1 L"]
    assert preparar_terminos_busqueda("aceite 500 ml") == ["aceite", "500 ml"]


def test_filtrar_por_busqueda_inteligente_encuentra_texto_vago():
    precios = normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Biggie",
                    "nombre_producto": "Gaseosa Coca Cola Original 1 Litro",
                    "precio": 9000,
                    "fecha_registro": "2026-05-15",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Coca Cola Zero 2L",
                    "precio": 12000,
                    "fecha_registro": "2026-05-15",
                },
                {
                    "supermercado": "Superseis",
                    "nombre_producto": "Sprite 1L",
                    "precio": 8500,
                    "fecha_registro": "2026-05-15",
                },
            ]
        )
    )

    filtrados = filtrar_por_busqueda_inteligente(precios, "coca 1l")

    assert list(filtrados["nombre_producto"]) == [
        "Gaseosa Coca Cola Original 1 Litro"
    ]
