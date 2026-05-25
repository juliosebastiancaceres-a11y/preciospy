import pandas as pd

from dashboard import normalizar_precios, preparar_comparacion_supermercados
from dashboard import preparar_tabla_comparacion
from dashboard import filtrar_por_busqueda_inteligente, preparar_terminos_busqueda
from dashboard import filtrar_comparacion_supermercados
from dashboard import preparar_resumen_categorias_comparacion
from dashboard import preparar_mejores_compras
from dashboard import preparar_resumen_categorias
from dashboard import preparar_ranking_supermercados
from dashboard import preparar_ranking_supermercados_por_categoria
from dashboard import preparar_matches_sospechosos
from dashboard import preparar_tabla_mejores_compras
from dashboard import preparar_tabla_resumen_categorias
from dashboard import preparar_tabla_ranking_supermercados
from dashboard import preparar_tabla_matches_sospechosos


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


def test_preparar_comparacion_supermercados_une_descartable_real_con_generico():
    precios = pd.DataFrame(
        [
            {
                "supermercado": "Areté",
                "nombre_producto": "GASEOSA COCA COLA DESCARTABLE 2LTS.",
                "precio": 14900,
                "fecha_registro": "2026-05-25",
                "categoria": "Bebidas sin alcohol",
            },
            {
                "supermercado": "Stock",
                "nombre_producto": "COCA COLA 2L",
                "precio": 13500,
                "fecha_registro": "2026-05-25",
                "categoria": "Bebidas",
            },
        ]
    )

    precios = normalizar_precios(precios)
    comparacion = preparar_comparacion_supermercados(precios)

    assert len(comparacion) == 1
    fila = comparacion.iloc[0]
    assert fila["Producto comparable"] == "coca cola 2 L"
    assert fila["Supermercado más barato"] == "Stock"
    assert fila["Coincidencia"] == "Flexible"
    assert fila["Categoría comparable"] == "Bebidas"


def test_preparar_comparacion_supermercados_no_mezcla_retornable_con_descartable():
    precios = pd.DataFrame(
        [
            {
                "supermercado": "Areté",
                "nombre_producto": "GASEOSA COCA COLA RETORNABLE 2 LT",
                "precio": 10000,
                "fecha_registro": "2026-05-25",
                "categoria": "Bebidas sin alcohol",
            },
            {
                "supermercado": "Stock",
                "nombre_producto": "COCA COLA 2L",
                "precio": 13500,
                "fecha_registro": "2026-05-25",
                "categoria": "Bebidas",
            },
        ]
    )

    precios = normalizar_precios(precios)
    comparacion = preparar_comparacion_supermercados(precios)

    assert comparacion.empty


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


def test_preparar_mejores_compras_ordena_oportunidades_accionables():
    comparacion = pd.DataFrame(
        [
            {
                "Producto comparable": "coca cola 2 L",
                "Categoría comparable": "Bebidas",
                "Producto mejor precio": "COCA COLA 2L",
                "Supermercado más barato": "Stock",
                "Coincidencia": "Flexible",
                "Confianza": "Media",
                "Supermercados comparados": 3,
                "Productos comparados": "Stock: COCA COLA 2L",
                "Mejor precio": 11000,
                "Diferencia": 3000,
                "Ahorro %": 21.4,
                "Stock": 11000,
                "Superseis": 12000,
                "Areté": 14000,
            },
            {
                "Producto comparable": "detergente 500 ml",
                "Categoría comparable": "Limpieza",
                "Producto mejor precio": "Detergente",
                "Supermercado más barato": "Superseis",
                "Coincidencia": "Exacta",
                "Confianza": "Alta",
                "Supermercados comparados": 2,
                "Productos comparados": "Superseis: Detergente",
                "Mejor precio": 8000,
                "Diferencia": 300,
                "Ahorro %": 3.6,
                "Stock": 8300,
                "Superseis": 8000,
                "Areté": None,
            },
        ]
    )

    oportunidades = preparar_mejores_compras(
        comparacion,
        ahorro_minimo_porcentaje=5,
        supermercados_minimos=3,
    )

    assert list(oportunidades["Producto comparable"]) == ["coca cola 2 L"]
    fila = oportunidades.iloc[0]
    assert fila["Mejor supermercado"] == "Stock"
    assert fila["Supermercado más caro"] == "Areté"
    assert fila["Precio más caro"] == 14000
    assert fila["Ahorro posible"] == 3000

    tabla = preparar_tabla_mejores_compras(oportunidades)
    assert tabla.iloc[0]["Mejor precio"] == "₲ 11.000"
    assert tabla.iloc[0]["Precio más caro"] == "₲ 14.000"
    assert tabla.iloc[0]["Ahorro posible"] == "₲ 3.000"
    assert tabla.iloc[0]["Ahorro %"] == "21.4%"


def test_preparar_resumen_categorias_identifica_supermercado_lider():
    comparacion = pd.DataFrame(
        [
            {
                "Producto comparable": "coca cola 2 L",
                "Categoría comparable": "Bebidas",
                "Supermercado más barato": "Stock",
                "Supermercados comparados": 3,
                "Mejor precio": 11000,
                "Diferencia": 3000,
                "Ahorro %": 21.4,
                "Stock": 11000,
                "Superseis": 12000,
                "Areté": 14000,
            },
            {
                "Producto comparable": "sprite 2 L",
                "Categoría comparable": "Bebidas",
                "Supermercado más barato": "Stock",
                "Supermercados comparados": 2,
                "Mejor precio": 9500,
                "Diferencia": 500,
                "Ahorro %": 5.0,
                "Stock": 9500,
                "Superseis": 10000,
                "Areté": None,
            },
            {
                "Producto comparable": "detergente 500 ml",
                "Categoría comparable": "Limpieza",
                "Supermercado más barato": "Superseis",
                "Supermercados comparados": 2,
                "Mejor precio": 8000,
                "Diferencia": 1000,
                "Ahorro %": 11.1,
                "Stock": 9000,
                "Superseis": 8000,
                "Areté": None,
            },
        ]
    )

    resumen = preparar_resumen_categorias(comparacion)

    bebidas = resumen[resumen["Categoría comparable"] == "Bebidas"].iloc[0]
    assert bebidas["Oportunidades"] == 2
    assert bebidas["Supermercado más conveniente"] == "Stock"
    assert bebidas["Victorias del líder"] == 2
    assert round(bebidas["Ahorro_promedio"], 1) == 1750

    tabla = preparar_tabla_resumen_categorias(resumen)
    bebidas_tabla = tabla[tabla["Categoría comparable"] == "Bebidas"].iloc[0]
    assert bebidas_tabla["Ahorro promedio"] == "₲ 1.750"
    assert bebidas_tabla["Ahorro máximo"] == "₲ 3.000"
    assert bebidas_tabla["Ahorro promedio %"] == "13.2%"


def test_preparar_ranking_supermercados_mide_victorias_y_sobrecosto():
    comparacion = pd.DataFrame(
        [
            {
                "Producto comparable": "coca cola 2 L",
                "Categoría comparable": "Bebidas",
                "Supermercado más barato": "Stock",
                "Supermercados comparados": 3,
                "Mejor precio": 11000,
                "Diferencia": 3000,
                "Ahorro %": 21.4,
                "Stock": 11000,
                "Superseis": 12000,
                "Areté": 14000,
            },
            {
                "Producto comparable": "detergente 500 ml",
                "Categoría comparable": "Limpieza",
                "Supermercado más barato": "Superseis",
                "Supermercados comparados": 2,
                "Mejor precio": 8000,
                "Diferencia": 1000,
                "Ahorro %": 11.1,
                "Stock": 9000,
                "Superseis": 8000,
                "Areté": None,
            },
        ]
    )

    ranking = preparar_ranking_supermercados(comparacion)

    stock = ranking[ranking["Supermercado"] == "Stock"].iloc[0]
    assert stock["Productos comparables"] == 2
    assert stock["Mejores precios"] == 1
    assert stock["Peores precios"] == 1
    assert stock["Ahorro vs mejor"] == 1000
    assert stock["Ahorro frente al segundo"] == 1000
    assert stock["Ahorro promedio al segundo"] == 1000

    arete = ranking[ranking["Supermercado"] == "Areté"].iloc[0]
    assert arete["Productos comparables"] == 1
    assert arete["Peores precios"] == 1

    tabla = preparar_tabla_ranking_supermercados(ranking)
    stock_tabla = tabla[tabla["Supermercado"] == "Stock"].iloc[0]
    assert stock_tabla["Ahorro vs mejor"] == "₲ 1.000"
    assert stock_tabla["Ahorro frente al segundo"] == "₲ 1.000"
    assert stock_tabla["Ahorro promedio al segundo"] == "₲ 1.000"
    assert stock_tabla["Tasa de victoria %"] == "50.0%"


def test_preparar_ranking_supermercados_por_categoria_separa_rubros():
    comparacion = pd.DataFrame(
        [
            {
                "Producto comparable": "coca cola 2 L",
                "Categoría comparable": "Bebidas",
                "Supermercado más barato": "Stock",
                "Supermercados comparados": 2,
                "Mejor precio": 11000,
                "Diferencia": 1000,
                "Ahorro %": 8.3,
                "Stock": 11000,
                "Superseis": 12000,
            },
            {
                "Producto comparable": "detergente 500 ml",
                "Categoría comparable": "Limpieza",
                "Supermercado más barato": "Superseis",
                "Supermercados comparados": 2,
                "Mejor precio": 8000,
                "Diferencia": 1000,
                "Ahorro %": 11.1,
                "Stock": 9000,
                "Superseis": 8000,
            },
        ]
    )

    ranking = preparar_ranking_supermercados_por_categoria(comparacion)

    bebidas_stock = ranking[
        (ranking["Categoría comparable"] == "Bebidas")
        & (ranking["Supermercado"] == "Stock")
    ].iloc[0]
    limpieza_superseis = ranking[
        (ranking["Categoría comparable"] == "Limpieza")
        & (ranking["Supermercado"] == "Superseis")
    ].iloc[0]

    assert bebidas_stock["Mejores precios"] == 1
    assert limpieza_superseis["Mejores precios"] == 1


def test_preparar_matches_sospechosos_detecta_riesgo_operativo():
    comparacion = pd.DataFrame(
        [
            {
                "Producto comparable": "envase retornable coca cola 1.5 L",
                "Categoría comparable": "Bebidas",
                "Producto mejor precio": "ENVASE RETORNABLE COCA COLA 1 1/2 LT",
                "Supermercado más barato": "Los Jardines",
                "Coincidencia": "Flexible",
                "Confianza": "Baja",
                "Presentación": "1.5 L",
                "Supermercados comparados": 2,
                "Productos comparados": (
                    "Los Jardines: ENVASE RETORNABLE COCA COLA 1 1/2 LT "
                    "(₲ 5.500) | Stock: GASEOSA COCA COLA 1.5L (₲ 12.000)"
                ),
                "Categorías comparadas": "Los Jardines: Bebidas | Stock: Bebidas",
                "Mejor precio": 5500,
                "Diferencia": 6500,
                "Ahorro %": 54.1,
            },
            {
                "Producto comparable": "arroz 1 kg",
                "Categoría comparable": "Almacen",
                "Producto mejor precio": "Arroz 1kg",
                "Supermercado más barato": "Stock",
                "Coincidencia": "Exacta",
                "Confianza": "Alta",
                "Presentación": "1 kg",
                "Supermercados comparados": 4,
                "Productos comparados": "Stock: Arroz 1kg | Biggie: Arroz 1kg",
                "Categorías comparadas": "Stock: Almacen | Biggie: Almacen",
                "Mejor precio": 7000,
                "Diferencia": 300,
                "Ahorro %": 4.1,
            },
        ]
    )

    sospechosos = preparar_matches_sospechosos(comparacion)

    assert list(sospechosos["Producto comparable"]) == [
        "envase retornable coca cola 1.5 L"
    ]
    fila = sospechosos.iloc[0]
    assert "Confianza baja" in fila["Motivos"]
    assert "Palabras sensibles" in fila["Motivos"]
    assert "envase" in fila["Señales"]
    assert "retornable" in fila["Señales"]

    tabla = preparar_tabla_matches_sospechosos(sospechosos)
    assert tabla.iloc[0]["Mejor precio"] == "₲ 5.500"
    assert tabla.iloc[0]["Diferencia"] == "₲ 6.500"
    assert tabla.iloc[0]["Ahorro %"] == "54.1%"
