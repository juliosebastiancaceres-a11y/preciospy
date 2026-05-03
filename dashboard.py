import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


RUTA_DB = Path(__file__).resolve().parent / "data" / "preciospy.db"


def cargar_precios():
    """Carga todos los registros de precios desde SQLite."""
    with sqlite3.connect(RUTA_DB) as conexion:
        return pd.read_sql_query("SELECT * FROM precios", conexion)


def mostrar_dashboard():
    """Muestra la tabla y el gráfico principal del dashboard."""
    st.title("PreciosPY — Monitor de precios Paraguay")

    precios = cargar_precios()

    st.dataframe(precios)
    st.bar_chart(precios, x="nombre_producto", y="precio")


if __name__ == "__main__":
    mostrar_dashboard()
