import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


RUTA_DB = Path(__file__).resolve().parent / "data" / "preciospy.db"


def cargar_precios():
    """Carga todos los registros de precios desde SQLite."""
    with sqlite3.connect(RUTA_DB) as conexion:
        return pd.read_sql_query("SELECT * FROM precios", conexion)


def filtrar_por_supermercado(precios, supermercados):
    """Filtra productos por uno o varios supermercados."""
    if not supermercados:
        return precios.iloc[0:0]

    return precios[precios["supermercado"].isin(supermercados)]


def filtrar_por_nombre(precios, texto_busqueda):
    """Filtra productos cuyo nombre contiene el texto buscado."""
    if not texto_busqueda:
        return precios

    return precios[
        precios["nombre_producto"].str.contains(texto_busqueda, case=False, na=False)
    ]


def filtrar_por_precio(precios, rango_precio):
    """Filtra productos dentro del rango de precios seleccionado."""
    precio_minimo, precio_maximo = rango_precio
    return precios[
        (precios["precio"] >= precio_minimo) & (precios["precio"] <= precio_maximo)
    ]


def obtener_rango_precios(precios):
    """Obtiene el precio mínimo y máximo desde los datos reales."""
    if precios.empty:
        return 0, 0

    return int(precios["precio"].min()), int(precios["precio"].max())


def mostrar_dashboard():
    """Muestra el dashboard con filtros, tabla y gráfico."""
    st.title("PreciosPY — Monitor de precios Paraguay")

    precios = cargar_precios()
    total_productos = len(precios)

    if precios.empty:
        st.info("Todavía no hay productos guardados en la base de datos.")
        return

    supermercados = sorted(precios["supermercado"].dropna().unique())
    precio_minimo, precio_maximo = obtener_rango_precios(precios)

    # Filtros laterales para soportar más supermercados en el futuro.
    supermercados_seleccionados = st.sidebar.multiselect(
        "Supermercados",
        supermercados,
        default=supermercados,
    )
    rango_precio = st.sidebar.slider(
        "Rango de precios",
        min_value=precio_minimo,
        max_value=precio_maximo,
        value=(precio_minimo, precio_maximo),
    )

    texto_busqueda = st.text_input("Buscar producto por nombre")

    precios_filtrados = filtrar_por_supermercado(
        precios,
        supermercados_seleccionados,
    )
    precios_filtrados = filtrar_por_nombre(precios_filtrados, texto_busqueda)
    precios_filtrados = filtrar_por_precio(precios_filtrados, rango_precio)

    st.write(f"Productos visibles: {len(precios_filtrados)} de {total_productos}")

    st.dataframe(
        precios_filtrados[["nombre_producto", "precio", "fecha_registro"]],
        use_container_width=True,
    )
    st.bar_chart(
        precios_filtrados.head(20),
        x="nombre_producto",
        y="precio",
    )


if __name__ == "__main__":
    mostrar_dashboard()
