import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


RUTA_DB = Path(__file__).resolve().parent / "data" / "preciospy.db"


st.set_page_config(
    page_title="PreciosPY",
    page_icon="🛒",
    layout="wide",
)


def aplicar_estilos():
    """Aplica estilos visuales personalizados al dashboard."""
    st.markdown(
        """
        <style>
            :root {
                --color-primario: #D52B1E;
                --color-secundario: #FFFFFF;
                --color-acento: #003893;
                --color-fondo: #F5F5F5;
                --color-card: #FFFFFF;
                --color-texto: #1A1A1A;
                --color-texto-suave: #565656;
                --color-borde: #E3E3E3;
            }

            html, body, [class*="css"] {
                font-family: sans-serif;
            }

            .stApp {
                background: var(--color-fondo);
                color: var(--color-texto);
            }

            .stApp p,
            .stApp span,
            .stApp label,
            .stApp div,
            .stApp h1,
            .stApp h2,
            .stApp h3 {
                color: var(--color-texto);
            }

            [data-testid="stHeader"] {
                background: transparent;
                border-bottom: none;
            }

            [data-testid="stSidebar"] {
                background: #ECECEC;
                border-right: 1px solid var(--color-borde);
            }

            [data-testid="stSidebar"] * {
                color: var(--color-texto);
            }

            [data-testid="stSidebar"] h3 {
                color: var(--color-primario) !important;
                font-weight: 800;
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            .app-header {
                background: linear-gradient(90deg, #D52B1E 0%, #003893 100%);
                border: none;
                border-radius: 0 0 24px 24px;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
                padding: 2.25rem 2rem;
                margin: -2rem 0 1.75rem;
            }

            .app-title {
                color: #FFFFFF !important;
                font-size: 2.8rem;
                font-weight: 800;
                line-height: 1;
                margin: 0;
            }

            .app-subtitle {
                color: rgba(255, 255, 255, 0.85) !important;
                font-size: 1.08rem;
                margin-top: 0.5rem;
                margin-bottom: 0;
            }

            .metric-card {
                background: var(--color-card);
                border: 1px solid #E6E6E6;
                border-top: 4px solid var(--color-primario);
                border-radius: 14px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                padding: 1.15rem 1.25rem;
                min-height: 128px;
            }

            .metric-label {
                color: var(--color-texto-suave) !important;
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0;
                text-transform: uppercase;
                margin-bottom: 0.65rem;
            }

            .metric-value {
                color: var(--color-primario) !important;
                font-size: 2rem;
                font-weight: 800;
                line-height: 1.15;
            }

            .section-title {
                color: var(--color-primario) !important;
                font-size: 1.25rem;
                font-weight: 800;
                margin: 1.6rem 0 0.85rem;
            }

            .content-card {
                background: var(--color-card);
                border: 1px solid #E6E6E6;
                border-radius: 14px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                padding: 1rem;
            }

            div[data-testid="stMetricValue"] {
                color: var(--color-primario);
            }

            [data-testid="stCaptionContainer"],
            [data-testid="stCaptionContainer"] * {
                color: var(--color-texto-suave) !important;
            }

            input,
            textarea,
            [data-baseweb="input"] input {
                color: var(--color-texto) !important;
                -webkit-text-fill-color: var(--color-texto) !important;
            }

            input::placeholder,
            textarea::placeholder {
                color: #7A8076 !important;
                opacity: 1;
            }

            [data-baseweb="input"],
            [data-baseweb="select"] > div {
                background: #FFFFFF;
                border-color: #D6D6D6;
            }

            [data-baseweb="tag"] {
                background: #FBE8E6;
                border: 1px solid #F1B7B2;
            }

            [data-baseweb="tag"] span {
                color: var(--color-primario) !important;
                font-weight: 700;
            }

            .stSlider [data-baseweb="slider"] div {
                color: var(--color-primario);
            }

            [data-testid="stDataFrame"] {
                color: var(--color-texto);
            }

            .chart-card {
                background: var(--color-card);
                border: 1px solid #E6E6E6;
                border-radius: 14px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                padding: 1rem;
            }

            div[role="tooltip"],
            div[role="tooltip"] * {
                color: #FFFFFF !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def cargar_precios():
    """Carga todos los registros de precios desde SQLite."""
    if not RUTA_DB.exists():
        return pd.DataFrame(
            columns=[
                "supermercado",
                "nombre_producto",
                "precio",
                "unidad",
                "fecha_registro",
            ]
        )

    with sqlite3.connect(RUTA_DB) as conexion:
        precios = pd.read_sql_query("SELECT * FROM precios", conexion)

    precios["precio"] = pd.to_numeric(precios["precio"], errors="coerce")
    precios["fecha_registro"] = precios["fecha_registro"].astype(str)
    return precios.dropna(subset=["precio"])


def formatear_guaranies(precio):
    """Formatea precios con separador de miles paraguayo."""
    return f"₲ {int(round(precio)):,.0f}".replace(",", ".")


def filtrar_precios(precios, supermercados, texto_busqueda, rango_precio):
    """Aplica todos los filtros seleccionados por el usuario."""
    if not supermercados:
        return precios.iloc[0:0]

    precio_minimo, precio_maximo = rango_precio
    filtrados = precios[precios["supermercado"].isin(supermercados)]
    filtrados = filtrados[
        (filtrados["precio"] >= precio_minimo)
        & (filtrados["precio"] <= precio_maximo)
    ]

    if texto_busqueda:
        filtrados = filtrados[
            filtrados["nombre_producto"].str.contains(
                texto_busqueda,
                case=False,
                na=False,
            )
        ]

    return filtrados


def obtener_rango_precios(precios):
    """Obtiene el rango real de precios para el slider."""
    if precios.empty:
        return 0, 0

    return int(precios["precio"].min()), int(precios["precio"].max())


def mostrar_header():
    """Muestra el encabezado principal del dashboard."""
    st.markdown(
        """
        <div class="app-header">
            <p class="app-title">🛒 PreciosPY</p>
            <p class="app-subtitle">
                Monitoreamos los precios de los supermercados del Paraguay
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mostrar_metricas(precios):
    """Muestra las métricas principales en cards."""
    total_productos = len(precios)
    total_supermercados = precios["supermercado"].nunique()
    ultima_actualizacion = precios["fecha_registro"].max()

    columnas = st.columns(3)
    metricas = [
        ("Productos monitoreados", f"{total_productos:,}".replace(",", ".")),
        ("Entidades", total_supermercados),
        ("Última actualización", ultima_actualizacion),
    ]

    for columna, (etiqueta, valor) in zip(columnas, metricas):
        columna.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{etiqueta}</div>
                <div class="metric-value">{valor}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def mostrar_filtros(precios):
    """Muestra filtros en la barra lateral y retorna sus valores."""
    supermercados = sorted(precios["supermercado"].dropna().unique())
    precio_minimo, precio_maximo = obtener_rango_precios(precios)

    st.sidebar.markdown("### Filtros")
    supermercados_seleccionados = st.sidebar.multiselect(
        "Supermercado",
        supermercados,
        default=supermercados,
    )
    texto_busqueda = st.sidebar.text_input("Buscar por nombre")
    rango_precio = st.sidebar.slider(
        "Rango de precios",
        min_value=precio_minimo,
        max_value=precio_maximo,
        value=(precio_minimo, precio_maximo),
        format="₲ %d",
    )

    return supermercados_seleccionados, texto_busqueda, rango_precio


def preparar_tabla(precios):
    """Prepara columnas visibles y precio formateado para la tabla."""
    tabla = precios[
        ["nombre_producto", "supermercado", "precio", "fecha_registro"]
    ].copy()
    tabla["precio"] = tabla["precio"].map(formatear_guaranies)
    tabla = tabla.rename(
        columns={
            "nombre_producto": "Producto",
            "supermercado": "Supermercado",
            "precio": "Precio",
            "fecha_registro": "Fecha",
        }
    )
    return tabla


def mostrar_grafico(precios):
    """Muestra los 15 productos más baratos del filtro actual."""
    st.markdown(
        '<div class="section-title">15 productos más baratos</div>',
        unsafe_allow_html=True,
    )

    if precios.empty:
        st.info("No hay productos para graficar con los filtros actuales.")
        return

    baratos = precios.nsmallest(15, "precio").copy()
    baratos["precio_formateado"] = baratos["precio"].map(formatear_guaranies)

    # Plotly permite controlar con precisión fondo, grilla, ejes y colores.
    grafico = px.bar(
        baratos,
        x="precio",
        y="nombre_producto",
        orientation="h",
        text="precio_formateado",
        labels={
            "precio": "Precio",
            "nombre_producto": "Producto",
        },
        custom_data=[
            "nombre_producto",
            "supermercado",
            "precio_formateado",
            "fecha_registro",
        ],
    )

    grafico.update_traces(
        marker_color="#D52B1E",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Supermercado: %{customdata[1]}<br>"
            "Precio: %{customdata[2]}<br>"
            "Fecha: %{customdata[3]}<extra></extra>"
        ),
    )
    grafico.update_layout(
        height=460,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={
            "family": "sans-serif",
            "color": "#1A1A1A",
            "size": 13,
        },
        margin={"l": 16, "r": 72, "t": 10, "b": 48},
        xaxis={
            "gridcolor": "#E8E8E8",
            "linecolor": "#DADADA",
            "tickcolor": "#DADADA",
            "title": {"font": {"color": "#1A1A1A"}},
        },
        yaxis={
            "gridcolor": "#FFFFFF",
            "linecolor": "#DADADA",
            "tickcolor": "#DADADA",
            "title": {"font": {"color": "#1A1A1A"}},
            "autorange": "reversed",
        },
        hoverlabel={
            "bgcolor": "#1A1A1A",
            "font_color": "#FFFFFF",
            "bordercolor": "#003893",
        },
    )

    st.plotly_chart(grafico, width="stretch", theme=None)


def mostrar_tabla(precios):
    """Muestra la tabla final sin índice visible."""
    st.markdown(
        '<div class="section-title">Productos filtrados</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(
        preparar_tabla(precios),
        hide_index=True,
        width="stretch",
    )


def mostrar_dashboard():
    """Renderiza el dashboard completo de PreciosPY."""
    aplicar_estilos()
    mostrar_header()

    precios = cargar_precios()

    if precios.empty:
        st.info("Todavía no hay productos guardados en la base de datos.")
        return

    mostrar_metricas(precios)
    filtros = mostrar_filtros(precios)
    precios_filtrados = filtrar_precios(precios, *filtros)

    st.caption(
        f"Mostrando {len(precios_filtrados):,} de {len(precios):,} registros".replace(
            ",",
            ".",
        )
    )

    mostrar_grafico(precios_filtrados)
    mostrar_tabla(precios_filtrados)


if __name__ == "__main__":
    mostrar_dashboard()
