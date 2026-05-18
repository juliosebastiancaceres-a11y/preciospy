import pandas as pd

from dashboard import normalizar_precios, preparar_comparacion_supermercados
from dashboard import preparar_tabla_comparacion
from dashboard import filtrar_por_busqueda_inteligente, preparar_terminos_busqueda
from dashboard import filtrar_comparacion_supermercados
from dashboard import preparar_resumen_categorias_comparacion


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
                "categoria": "Bebidas sin alcohol",
            },
            {
                "supermercado": "Superseis",
                "nombre_producto": "Coca-Cola sabor original gaseosa 2000ml",
                "precio": 12500,
                "fecha_registro": "2026-05-08",
                "categoria": "Bebidas sin alcohol",
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
        "Categoría comparable",
        "Coincidencia",
        "Confianza",
    ]
    assert tabla.iloc[0]["Categoría comparable"] == "Sin categoria"
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


def test_preparar_comparacion_supermercados_no_mezcla_categorias_flexibles():
    precios = pd.DataFrame(
        [
            {
                "supermercado": "Stock",
                "nombre_producto": "Coca Cola Original Botella 2 Litros",
                "precio": 12000,
                "fecha_registro": "2026-05-08",
                "categoria": "Bebidas sin alcohol",
            },
            {
                "supermercado": "Superseis",
                "nombre_producto": "Coca-Cola sabor original gaseosa 2000ml",
                "precio": 11500,
                "fecha_registro": "2026-05-08",
                "categoria": "Limpieza",
            },
        ]
    )

    precios = normalizar_precios(precios)
    comparacion = preparar_comparacion_supermercados(precios)

    assert comparacion.empty


def test_preparar_comparacion_supermercados_usa_categorias_flexibles():
    precios = pd.DataFrame(
        [
            {
                "supermercado": "Stock",
                "nombre_producto": "Coca Cola Original Botella 2 Litros",
                "precio": 12000,
                "fecha_registro": "2026-05-08",
                "categoria": "Bebidas sin alcohol",
            },
            {
                "supermercado": "Superseis",
                "nombre_producto": "Coca-Cola sabor original gaseosa 2000ml",
                "precio": 11500,
                "fecha_registro": "2026-05-08",
                "categoria": "Bebidas sin alcohol",
            },
        ]
    )

    precios = normalizar_precios(precios)
    comparacion = preparar_comparacion_supermercados(precios)

    assert len(comparacion) == 1
    fila = comparacion.iloc[0]
    assert fila["Coincidencia"] == "Flexible"
    assert fila["Categoría comparable"] == "Bebidas"
    assert "Stock: Bebidas sin alcohol" in fila["Categorías comparadas"]


def test_preparar_comparacion_supermercados_ignora_flexibles_sin_categoria():
    precios = pd.DataFrame(
        [
            {
                "supermercado": "Stock",
                "nombre_producto": "Coca Cola Original Botella 2 Litros",
                "precio": 12000,
                "fecha_registro": "2026-05-08",
            },
            {
                "supermercado": "Superseis",
                "nombre_producto": "Coca-Cola sabor original gaseosa 2000ml",
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


def test_filtrar_comparacion_supermercados_combina_filtros():
    comparacion = pd.DataFrame(
        [
            {
                "Producto comparable": "coca cola original 2 L",
                "Categoría comparable": "Bebidas",
                "Producto mejor precio": "Coca Cola 2L",
                "Supermercado más barato": "Stock",
                "Coincidencia": "Flexible",
                "Productos comparados": "Stock: Coca Cola 2L",
                "Categorías comparadas": "Stock: Bebidas sin alcohol",
                "Mejor precio": 11000,
                "Diferencia": 1000,
                "Ahorro %": 8.3,
            },
            {
                "Producto comparable": "detergente 500 ml",
                "Categoría comparable": "Limpieza",
                "Producto mejor precio": "Detergente",
                "Supermercado más barato": "Superseis",
                "Coincidencia": "Exacta",
                "Productos comparados": "Superseis: Detergente",
                "Categorías comparadas": "Superseis: Limpieza",
                "Mejor precio": 8000,
                "Diferencia": 300,
                "Ahorro %": 3.6,
            },
        ]
    )

    filtrada = filtrar_comparacion_supermercados(
        comparacion,
        categorias=["Bebidas"],
        coincidencias=["Flexible"],
        texto_busqueda="coca 2l",
        diferencia_minima=500,
    )

    assert list(filtrada["Producto comparable"]) == ["coca cola original 2 L"]


def test_preparar_resumen_categorias_comparacion_formatea_metricas():
    comparacion = pd.DataFrame(
        [
            {
                "Producto comparable": "coca cola 2 L",
                "Categoría comparable": "Bebidas",
                "Coincidencia": "Exacta",
                "Diferencia": 1000,
                "Ahorro %": 8.3,
            },
            {
                "Producto comparable": "sprite 2 L",
                "Categoría comparable": "Bebidas",
                "Coincidencia": "Flexible",
                "Diferencia": 500,
                "Ahorro %": 4.2,
            },
            {
                "Producto comparable": "detergente 500 ml",
                "Categoría comparable": "Limpieza",
                "Coincidencia": "Exacta",
                "Diferencia": 300,
                "Ahorro %": 3.6,
            },
        ]
    )

    resumen = preparar_resumen_categorias_comparacion(comparacion)

    bebidas = resumen[resumen["Categoría comparable"] == "Bebidas"].iloc[0]
    assert bebidas["Coincidencias"] == 2
    assert bebidas["Exactas"] == 1
    assert bebidas["Flexibles"] == 1
    assert bebidas["Mayor diferencia"] == "₲ 1.000"
    assert bebidas["Ahorro promedio"] == "6.2%"
