import pandas as pd

from dashboard import (
    filtrar_evolucion_supermercados,
    filtrar_precios_evolucion,
    normalizar_precios,
    obtener_configuracion_evolucion,
    obtener_colores_supermercados,
    obtener_indice_opcion_evolucion,
    preparar_evolucion_producto,
    preparar_opciones_evolucion,
    preparar_resumen_evolucion,
    reconciliar_supermercados_seleccionados,
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


def test_preparar_opciones_evolucion_filtra_por_minimo_fechas():
    precios = normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Coca Cola 1L",
                    "precio": 8500,
                    "fecha_registro": "2026-05-07",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Pepsi 1L",
                    "precio": 7600,
                    "fecha_registro": "2026-05-07",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Pepsi 1L",
                    "precio": 7800,
                    "fecha_registro": "2026-05-08",
                },
            ]
        )
    )

    opciones = preparar_opciones_evolucion(precios, minimo_fechas=2)

    assert len(opciones) == 1
    assert opciones.iloc[0]["clave_matching"] == "pepsi 1 L"


def test_obtener_indice_opcion_evolucion_conserva_clave_valida():
    opciones = pd.DataFrame(
        [
            {"clave_matching": "aceite 1 L"},
            {"clave_matching": "coca cola 2 L"},
        ]
    )

    assert obtener_indice_opcion_evolucion(opciones, "coca cola 2 L") == 1


def test_obtener_indice_opcion_evolucion_usa_primera_si_clave_no_existe():
    opciones = pd.DataFrame(
        [
            {"clave_matching": "aceite 1 L"},
            {"clave_matching": "coca cola 2 L"},
        ]
    )

    assert obtener_indice_opcion_evolucion(opciones, "leche 1 L") == 0


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


def test_filtrar_precios_evolucion_respeta_supermercado_seleccionado():
    precios = _precios_equivalentes()

    filtrados = filtrar_precios_evolucion(precios, ["Stock"], "")

    assert set(filtrados["supermercado"]) == {"Stock"}
    assert len(filtrados) == 2


def test_filtrar_precios_evolucion_busca_dentro_de_la_seleccion():
    precios = normalizar_precios(
        pd.DataFrame(
            [
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Coca Cola 1000 ml retornable",
                    "precio": 8500,
                    "fecha_registro": "2026-05-07",
                },
                {
                    "supermercado": "Casa Rica",
                    "nombre_producto": "Coca Cola 1 L sin azucar",
                    "precio": 9800,
                    "fecha_registro": "2026-05-07",
                },
                {
                    "supermercado": "Stock",
                    "nombre_producto": "Pepsi 1000 ml",
                    "precio": 7600,
                    "fecha_registro": "2026-05-07",
                },
            ]
        )
    )

    filtrados = filtrar_precios_evolucion(precios, ["Stock"], "coca 1l")

    assert list(filtrados["nombre_producto"]) == ["Coca Cola 1000 ml retornable"]
    assert set(filtrados["supermercado"]) == {"Stock"}


def test_obtener_configuracion_evolucion_prepara_modo_comparar():
    evolucion = preparar_evolucion_producto(_precios_equivalentes(), "coca cola 2 L")

    filtrada, comparar = obtener_configuracion_evolucion(
        evolucion,
        "Comparar supermercados",
        ["Stock", "Superseis"],
    )

    assert comparar is True
    assert set(filtrada["supermercado"]) == {"Stock", "Superseis"}


def test_obtener_configuracion_evolucion_acepta_lista_en_modo_unico():
    evolucion = preparar_evolucion_producto(_precios_equivalentes(), "coca cola 2 L")

    filtrada, comparar = obtener_configuracion_evolucion(
        evolucion,
        "Ver un supermercado",
        ["Superseis"],
    )

    assert comparar is False
    assert set(filtrada["supermercado"]) == {"Superseis"}
    assert len(filtrada) == 2


def test_obtener_colores_supermercados_reconocibles():
    dominio, colores = obtener_colores_supermercados(
        ["Biggie", "Los Jardines", "Casa Rica", "Areté", "Stock", "Superseis"]
    )

    assert dict(zip(dominio, colores)) == {
        "Biggie": "#C6051D",
        "Los Jardines": "#D6A300",
        "Casa Rica": "#101828",
        "Areté": "#38BDF8",
        "Stock": "#0038A8",
        "Superseis": "#2E7D32",
    }


def test_reconciliar_supermercados_seleccionados_agrega_nuevos():
    seleccion = ["Stock", "Superseis"]
    supermercados = ["Biggie", "Casa Rica", "Stock", "Superseis"]
    supermercados_anteriores = ["Stock", "Superseis"]

    assert reconciliar_supermercados_seleccionados(
        seleccion,
        supermercados,
        supermercados_anteriores,
    ) == ["Stock", "Superseis", "Biggie", "Casa Rica"]


def test_reconciliar_supermercados_seleccionados_agrega_si_antes_estaban_todos():
    seleccion = ["Biggie", "Casa Rica", "Stock", "Superseis"]
    supermercados = ["Areté", "Biggie", "Casa Rica", "Stock", "Superseis"]
    supermercados_anteriores = ["Biggie", "Casa Rica", "Stock", "Superseis"]

    assert reconciliar_supermercados_seleccionados(
        seleccion,
        supermercados,
        supermercados_anteriores,
    ) == ["Biggie", "Casa Rica", "Stock", "Superseis", "Areté"]


def test_reconciliar_supermercados_seleccionados_respeta_removidos():
    seleccion = ["Stock", "Superseis"]
    supermercados = ["Biggie", "Casa Rica", "Stock", "Superseis"]
    supermercados_anteriores = ["Biggie", "Casa Rica", "Stock", "Superseis"]

    assert reconciliar_supermercados_seleccionados(
        seleccion,
        supermercados,
        supermercados_anteriores,
    ) == ["Stock", "Superseis"]


def test_reconciliar_supermercados_seleccionados_limpia_obsoletos():
    seleccion = ["Stock", "Viejo"]
    supermercados = ["Biggie", "Stock"]
    supermercados_anteriores = ["Biggie", "Stock", "Viejo"]

    assert reconciliar_supermercados_seleccionados(
        seleccion,
        supermercados,
        supermercados_anteriores,
    ) == ["Stock"]


def test_preparar_resumen_evolucion_calcula_variacion():
    evolucion = preparar_evolucion_producto(_precios_equivalentes(), "coca cola 2 L")
    resumen = preparar_resumen_evolucion(evolucion)
    stock = resumen[resumen["Supermercado"] == "Stock"].iloc[0]

    assert stock["Último precio"] == "₲ 12.200"
    assert stock["Precio mínimo"] == "₲ 12.000"
    assert stock["Variación"] == "+₲ 200"
    assert stock["Variación %"] == "+1.7%"
