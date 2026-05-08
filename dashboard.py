import os
import sqlite3
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client


RUTA_DB = Path(__file__).resolve().parent / "data" / "preciospy.db"
RUTA_ENV = Path(__file__).resolve().parent / ".env"
TAMANO_LOTE_SUPABASE = 1000
COLUMNAS_PRECIOS = [
    "supermercado",
    "nombre_producto",
    "precio",
    "unidad",
    "fecha_registro",
    "categoria",
    "url_producto",
    "moneda",
    "fecha_hora_registro",
]


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
                --py-red: #D52B1E;
                --py-red-deep: #A61D18;
                --py-blue: #0038A8;
                --py-blue-soft: #DCEAFF;
                --py-white: #FFFFFF;
                --py-bg: #F5F7FB;
                --py-surface: rgba(255, 255, 255, 0.88);
                --py-text: #172033;
                --py-muted: #667085;
                --py-border: #E4E7EC;
                --py-success: #12805C;
                --py-warning: #C47A00;
                --py-gold: #F2C94C;
                --py-shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
            }

            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(12px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @keyframes cardLiftIn {
                from {
                    opacity: 0;
                    transform: translateY(16px) scale(0.985);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            @keyframes progress-blue-sweep {
                from {
                    transform: translateX(-110%);
                    opacity: 0.9;
                }
                to {
                    transform: translateX(110%);
                    opacity: 0;
                }
            }

            html,
            body {
                font-family:
                    Inter, ui-sans-serif, system-ui, -apple-system,
                    BlinkMacSystemFont, "Segoe UI", sans-serif;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(213, 43, 30, 0.08), transparent 34rem),
                    radial-gradient(circle at top right, rgba(0, 56, 168, 0.10), transparent 38rem),
                    linear-gradient(180deg, #F8FAFF 0%, var(--py-bg) 42%, #F7F8FB 100%);
                color: var(--py-text);
            }

            header[data-testid="stHeader"],
            [data-testid="stHeader"] {
                background: transparent !important;
                display: none !important;
                height: 0 !important;
                min-height: 0 !important;
                visibility: hidden !important;
            }

            [data-testid="stToolbar"],
            [data-testid="stDecoration"],
            #MainMenu,
            footer {
                display: none !important;
                visibility: hidden !important;
            }

            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(247, 249, 253, 0.96));
                border-right: 1px solid var(--py-border);
            }

            [data-testid="stSidebar"] h3 {
                color: var(--py-text);
                font-weight: 750;
            }

            [data-testid="stWidgetLabel"],
            [data-testid="stWidgetLabel"] *,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] label * {
                color: var(--py-text) !important;
                font-weight: 680;
                opacity: 1 !important;
            }

            [data-testid="stSidebar"] .stButton > button {
                background: linear-gradient(135deg, var(--py-red), var(--py-blue));
                border: 0;
                border-radius: 10px;
                color: var(--py-white);
                font-weight: 750;
                transition:
                    box-shadow 160ms ease,
                    transform 160ms ease;
            }

            [data-testid="stSidebar"] .stButton > button:hover {
                box-shadow: 0 12px 24px rgba(0, 56, 168, 0.18);
                color: var(--py-white);
                transform: translateY(-1px);
            }

            [data-testid="stSidebar"] .stButton > button * {
                color: var(--py-white) !important;
            }

            [data-baseweb="tag"] {
                background: rgba(220, 234, 255, 0.88);
                border: 1px solid rgba(0, 56, 168, 0.16);
            }

            [data-baseweb="tag"] span {
                color: var(--py-blue) !important;
                font-weight: 750;
            }

            .block-container {
                animation: fadeInUp 420ms ease-out both;
                max-width: 1260px;
                padding-top: 1.2rem;
                padding-bottom: 2.4rem;
            }

            .py-hero {
                animation: fadeInUp 500ms ease-out both;
                background:
                    linear-gradient(135deg, rgba(213, 43, 30, 0.96) 0%, rgba(166, 29, 24, 0.96) 38%, rgba(0, 56, 168, 0.96) 100%);
                border: 1px solid rgba(255, 255, 255, 0.38);
                border-radius: 18px;
                box-shadow: 0 22px 54px rgba(0, 56, 168, 0.22);
                color: var(--py-white);
                overflow: hidden;
                padding: 1.5rem 1.6rem;
                position: relative;
                margin: 0 0 1.25rem;
            }

            .py-hero::before {
                background:
                    linear-gradient(90deg, var(--py-red) 0 33%, var(--py-white) 33% 66%, var(--py-blue) 66% 100%);
                content: "";
                height: 5px;
                inset: 0 0 auto;
                position: absolute;
            }

            .py-hero::after {
                background:
                    radial-gradient(circle, rgba(255,255,255,0.20) 0 2px, transparent 2px);
                background-size: 20px 20px;
                content: "";
                inset: 0;
                opacity: 0.16;
                pointer-events: none;
                position: absolute;
            }

            .hero-content {
                position: relative;
                z-index: 1;
            }

            .hero-kicker {
                align-items: center;
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin-bottom: 0.65rem;
            }

            .py-badge {
                background: rgba(255, 255, 255, 0.16);
                border: 1px solid rgba(255, 255, 255, 0.28);
                border-radius: 999px;
                color: rgba(255, 255, 255, 0.94) !important;
                display: inline-flex;
                font-size: 0.78rem;
                font-weight: 750;
                padding: 0.34rem 0.72rem;
            }

            .py-badge.light {
                background: rgba(255, 255, 255, 0.92);
                color: var(--py-blue) !important;
            }

            .app-title {
                color: var(--py-white) !important;
                font-size: 2.35rem;
                font-weight: 850;
                line-height: 1.1;
                margin: 0;
            }

            .app-subtitle {
                color: rgba(255, 255, 255, 0.86) !important;
                font-size: 1.02rem;
                margin-top: 0.5rem;
                margin-bottom: 0;
            }

            .metric-card {
                animation: cardLiftIn 620ms cubic-bezier(0.22, 1, 0.36, 1) both;
                background: var(--py-surface);
                border: 1px solid rgba(228, 231, 236, 0.95);
                border-radius: 14px;
                box-shadow: var(--py-shadow);
                min-height: 126px;
                overflow: hidden;
                padding: 1rem 1.05rem;
                position: relative;
                transform: translateY(0);
                transition:
                    border-color 160ms ease,
                    box-shadow 160ms ease,
                    transform 160ms ease;
            }

            .metric-delay-1 { animation-delay: 60ms; }
            .metric-delay-2 { animation-delay: 120ms; }
            .metric-delay-3 { animation-delay: 180ms; }
            .metric-delay-4 { animation-delay: 240ms; }
            .metric-delay-5 { animation-delay: 300ms; }

            .metric-card::before {
                background: linear-gradient(90deg, var(--py-red), var(--py-white), var(--py-blue));
                content: "";
                height: 4px;
                inset: 0 0 auto;
                position: absolute;
            }

            .metric-card::after {
                background: linear-gradient(
                    115deg,
                    transparent 0%,
                    rgba(255, 255, 255, 0.55) 48%,
                    transparent 100%
                );
                content: "";
                inset: 0;
                opacity: 0;
                pointer-events: none;
                position: absolute;
                transform: translateX(-120%);
                transition:
                    opacity 180ms ease,
                    transform 520ms ease;
            }

            .metric-card:hover {
                border-color: rgba(0, 56, 168, 0.28);
                box-shadow: 0 20px 42px rgba(0, 56, 168, 0.18);
                transform: translateY(-7px) scale(1.012);
            }

            .metric-card:hover::after {
                opacity: 1;
                transform: translateX(125%);
            }

            .metric-topline {
                align-items: center;
                display: flex;
                gap: 0.55rem;
                margin-bottom: 0.55rem;
            }

            .metric-icon {
                align-items: center;
                background: var(--py-blue-soft);
                border-radius: 10px;
                color: var(--py-blue);
                display: inline-flex;
                font-size: 1rem;
                height: 2rem;
                justify-content: center;
                width: 2rem;
                transition:
                    background 160ms ease,
                    color 160ms ease,
                    transform 180ms ease;
            }

            .metric-card:hover .metric-icon {
                background: var(--py-blue);
                color: var(--py-white);
                transform: rotate(-4deg) scale(1.08);
            }

            .metric-label {
                color: var(--py-muted) !important;
                font-size: 0.74rem;
                font-weight: 700;
                letter-spacing: 0;
                text-transform: uppercase;
                margin-bottom: 0.55rem;
            }

            .metric-value {
                color: var(--py-red-deep) !important;
                font-size: 1.78rem;
                font-weight: 850;
                line-height: 1.15;
            }

            .metric-desc {
                color: var(--py-muted) !important;
                font-size: 0.78rem;
                line-height: 1.35;
                margin-top: 0.35rem;
            }

            .section-title {
                color: var(--py-text) !important;
                font-size: 1.15rem;
                font-weight: 800;
                margin: 0;
            }

            .section-heading {
                align-items: flex-end;
                display: flex;
                justify-content: space-between;
                gap: 1rem;
                margin: 1.75rem 0 0.85rem;
            }

            .section-copy {
                color: var(--py-muted) !important;
                font-size: 0.9rem;
                margin-top: 0.2rem;
            }

            .section-pill {
                background: #FFF8E1;
                border: 1px solid rgba(242, 201, 76, 0.35);
                border-radius: 999px;
                color: #8A5A00 !important;
                font-size: 0.78rem;
                font-weight: 750;
                padding: 0.35rem 0.7rem;
            }

            .content-card {
                animation: fadeInUp 520ms ease-out both;
                background: var(--py-surface);
                border: 1px solid var(--py-border);
                border-radius: 16px;
                box-shadow: var(--py-shadow);
                padding: 1rem;
                transform: translateY(0);
                transition:
                    border-color 160ms ease,
                    box-shadow 160ms ease,
                    transform 160ms ease;
            }

            .content-card:hover {
                border-color: rgba(0, 56, 168, 0.22);
                box-shadow: 0 18px 38px rgba(0, 56, 168, 0.13);
                transform: translateY(-3px);
            }

            .filter-summary {
                align-items: center;
                background: rgba(255, 255, 255, 0.76);
                border: 1px solid var(--py-border);
                border-radius: 12px;
                color: var(--py-muted) !important;
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-top: 1rem;
                padding: 0.75rem 0.9rem;
                transform: translateY(0);
                transition:
                    border-color 160ms ease,
                    box-shadow 160ms ease,
                    transform 160ms ease;
            }

            .filter-summary:hover {
                border-color: rgba(0, 56, 168, 0.22);
                box-shadow: 0 14px 30px rgba(0, 56, 168, 0.10);
                transform: translateY(-2px);
            }

            .filter-chip {
                background: var(--py-blue-soft);
                border-radius: 999px;
                color: var(--py-blue) !important;
                font-size: 0.78rem;
                font-weight: 750;
                padding: 0.25rem 0.6rem;
            }

            [data-testid="stCaptionContainer"],
            [data-testid="stCaptionContainer"] * {
                color: var(--py-muted) !important;
            }

            [data-testid="stVegaLiteChart"] {
                animation: fadeInUp 520ms ease-out both;
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid var(--py-border);
                border-radius: 16px;
                box-shadow: var(--py-shadow);
                padding: 0.85rem;
                transform: translateY(0);
                transition:
                    border-color 160ms ease,
                    box-shadow 160ms ease,
                    transform 160ms ease;
            }

            [data-testid="stVegaLiteChart"]:hover,
            [data-testid="stDataFrame"]:hover,
            [data-testid="stVerticalBlockBorderWrapper"]:hover {
                border-color: rgba(0, 56, 168, 0.24) !important;
                box-shadow: 0 18px 38px rgba(0, 56, 168, 0.13);
                transform: translateY(-2px);
            }

            [data-testid="stDataFrame"],
            [data-testid="stVerticalBlockBorderWrapper"] {
                animation: fadeInUp 520ms ease-out both;
                border-radius: 16px;
                transform: translateY(0);
                transition:
                    border-color 160ms ease,
                    box-shadow 160ms ease,
                    transform 160ms ease;
            }

            [data-testid="stProgress"] [role="progressbar"] {
                overflow: hidden;
                position: relative;
            }

            [data-testid="stProgress"] [role="progressbar"]::after {
                animation: progress-blue-sweep 520ms ease-out 1;
                background: linear-gradient(
                    90deg,
                    transparent 0%,
                    rgba(139, 183, 255, 0.28) 40%,
                    rgba(139, 183, 255, 0.62) 50%,
                    rgba(139, 183, 255, 0.28) 60%,
                    transparent 100%
                );
                content: "";
                inset: 0;
                pointer-events: none;
                position: absolute;
            }

            @media (prefers-reduced-motion: reduce) {
                .block-container,
                .py-hero,
                .metric-card,
                .content-card,
                [data-testid="stVegaLiteChart"],
                [data-testid="stDataFrame"],
                [data-testid="stVerticalBlockBorderWrapper"],
                [data-testid="stProgress"] [role="progressbar"]::after {
                    animation: none;
                }

                .metric-card,
                .content-card,
                .filter-summary,
                [data-testid="stVegaLiteChart"],
                [data-testid="stDataFrame"],
                [data-testid="stVerticalBlockBorderWrapper"] {
                    transition: none;
                    transform: none;
                }
            }

            @media (max-width: 980px) {
                .app-title {
                    font-size: 2rem;
                }
            }

            @media (max-width: 720px) {
                .section-heading {
                    align-items: flex-start;
                    flex-direction: column;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalizar_precios(precios):
    """Normaliza columnas y tipos esperados por el dashboard."""
    for columna in COLUMNAS_PRECIOS:
        if columna not in precios.columns:
            precios[columna] = None

    precios["precio"] = pd.to_numeric(precios["precio"], errors="coerce")
    precios["fecha_registro"] = precios["fecha_registro"].astype(str)
    precios["fecha_registro_dt"] = pd.to_datetime(
        precios["fecha_registro"],
        errors="coerce",
    )
    return precios.dropna(subset=["precio", "nombre_producto", "supermercado"])


def cargar_precios_sqlite():
    """Carga todos los registros de precios desde SQLite."""
    if not RUTA_DB.exists():
        return pd.DataFrame(columns=COLUMNAS_PRECIOS)

    try:
        with sqlite3.connect(RUTA_DB) as conexion:
            precios = pd.read_sql_query("SELECT * FROM precios", conexion)
    except Exception:
        return pd.DataFrame(columns=COLUMNAS_PRECIOS)

    return normalizar_precios(precios)


def cargar_precios_supabase():
    """Carga precios desde Supabase si esta configurado."""
    load_dotenv(RUTA_ENV)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        return pd.DataFrame(columns=COLUMNAS_PRECIOS)

    try:
        supabase = create_client(url, key)
        registros = []
        inicio = 0

        while True:
            fin = inicio + TAMANO_LOTE_SUPABASE - 1
            respuesta = (
                supabase.table("precios")
                .select(",".join(COLUMNAS_PRECIOS))
                .order("fecha_registro", desc=True)
                .range(inicio, fin)
                .execute()
            )
            lote = respuesta.data or []

            if not lote:
                break

            registros.extend(lote)

            if len(lote) < TAMANO_LOTE_SUPABASE:
                break

            inicio += TAMANO_LOTE_SUPABASE
    except Exception:
        return pd.DataFrame(columns=COLUMNAS_PRECIOS)

    return normalizar_precios(pd.DataFrame(registros))


@st.cache_data(show_spinner=False, ttl=300)
def cargar_precios():
    """Carga precios desde Supabase y usa SQLite local como respaldo."""
    precios = cargar_precios_supabase()

    if not precios.empty:
        return precios

    return cargar_precios_sqlite()


def formatear_guaranies(precio):
    """Formatea precios con separador de miles paraguayo."""
    return f"₲ {int(round(precio)):,.0f}".replace(",", ".")


def obtener_colores_supermercados(supermercados):
    """Asigna colores consistentes a cada supermercado del grafico."""
    colores_fijos = {
        "stock": "#0038A8",
        "superseis": "#2E7D32",
    }
    paleta_respaldo = ["#0038A8", "#12805C", "#7C3AED", "#C47A00"]
    dominio = []
    colores = []

    for supermercado in supermercados:
        nombre = str(supermercado)
        dominio.append(nombre)
        clave = nombre.strip().lower()
        color = colores_fijos.get(clave)

        if color is None:
            color = paleta_respaldo[len(colores) % len(paleta_respaldo)]

        colores.append(color)

    return dominio, colores


def filtrar_precios(
    precios,
    supermercados,
    texto_busqueda,
    rango_precio,
    rango_fecha=None,
):
    """Aplica todos los filtros seleccionados por el usuario."""
    if not supermercados:
        return precios.iloc[0:0]

    precio_minimo, precio_maximo = rango_precio
    filtrados = precios[precios["supermercado"].isin(supermercados)]
    filtrados = filtrados[
        (filtrados["precio"] >= precio_minimo)
        & (filtrados["precio"] <= precio_maximo)
    ]

    texto_busqueda = texto_busqueda.strip()
    if texto_busqueda:
        filtrados = filtrados[
            filtrados["nombre_producto"].str.contains(
                texto_busqueda,
                case=False,
                na=False,
                regex=False,
            )
        ]

    if rango_fecha and "fecha_registro_dt" in filtrados.columns:
        fecha_inicio, fecha_fin = rango_fecha
        fechas = filtrados["fecha_registro_dt"]
        filtrados = filtrados[
            (fechas >= pd.Timestamp(fecha_inicio))
            & (fechas <= pd.Timestamp(fecha_fin))
        ]

    return filtrados


def obtener_rango_precios(precios):
    """Obtiene el rango real de precios para el slider."""
    if precios.empty:
        return 0, 0

    return int(precios["precio"].min()), int(precios["precio"].max())


def obtener_rango_fechas(precios):
    """Obtiene fechas minima y maxima validas para el filtro temporal."""
    fechas = pd.to_datetime(precios.get("fecha_registro"), errors="coerce").dropna()

    if fechas.empty:
        return None

    return fechas.min().date(), fechas.max().date()


def mostrar_encabezado_seccion(titulo, descripcion, etiqueta=None):
    """Renderiza encabezados de seccion con jerarquia consistente."""
    etiqueta_html = f'<span class="section-pill">{escape(etiqueta)}</span>' if etiqueta else ""
    st.markdown(
        f"""
        <div class="section-heading">
            <div>
                <div class="section-title">{escape(titulo)}</div>
                <div class="section-copy">{escape(descripcion)}</div>
            </div>
            {etiqueta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def mostrar_header():
    """Muestra el encabezado principal del dashboard."""
    st.markdown(
        """
        <div class="py-hero">
            <div class="hero-content">
                <div class="hero-kicker">
                    <span class="py-badge light">🗺️ Hecho en Paraguay</span>
                    <span class="py-badge">📊 Datos actualizados diariamente</span>
                    <span class="py-badge">🔍 +14.000 productos monitoreados</span>
                </div>
                <p class="app-title">PreciosPY</p>
                <p class="app-subtitle">
                    Compará precios de supermercados en Paraguay con datos claros,
                    históricos y fáciles de explorar.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mostrar_metricas(precios):
    """Muestra metricas sin confundir productos con registros historicos."""
    total_registros = len(precios)
    productos_unicos = (
        precios[["nombre_producto", "supermercado"]].drop_duplicates().shape[0]
    )
    supermercados = precios["supermercado"].nunique()
    dias_registrados = precios["fecha_registro"].nunique()
    ultima_actualizacion = precios["fecha_registro"].max()

    columnas = st.columns(5)
    metricas = [
        (
            "🛒",
            "Productos únicos",
            f"{productos_unicos:,}".replace(",", "."),
            "Producto + supermercado",
        ),
        (
            "📈",
            "Registros históricos",
            f"{total_registros:,}".replace(",", "."),
            "Precios guardados",
        ),
        ("🏬", "Supermercados", supermercados, "Fuentes monitoreadas"),
        ("📅", "Días monitoreados", dias_registrados, "Fechas con datos"),
        ("✓", "Última actualización", ultima_actualizacion, "Dato más reciente"),
    ]

    for indice, (columna, (icono, etiqueta, valor, descripcion)) in enumerate(
        zip(columnas, metricas),
        start=1,
    ):
        columna.markdown(
            f"""
            <div class="metric-card metric-delay-{indice}">
                <div class="metric-topline">
                    <div class="metric-icon">{icono}</div>
                    <div class="metric-label">{etiqueta}</div>
                </div>
                <div class="metric-value">{valor}</div>
                <div class="metric-desc">{descripcion}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def mostrar_filtros(precios):
    """Muestra filtros en la barra lateral y retorna sus valores."""
    supermercados = sorted(precios["supermercado"].dropna().unique())
    precio_minimo, precio_maximo = obtener_rango_precios(precios)
    rango_fechas = obtener_rango_fechas(precios)

    st.sidebar.markdown("### Filtros")
    st.sidebar.caption("Encontrá precios por producto, supermercado y período.")

    if st.sidebar.button("Limpiar filtros", use_container_width=True):
        st.session_state["filtro_supermercados"] = supermercados
        st.session_state["filtro_busqueda"] = ""
        st.session_state["filtro_precio"] = (precio_minimo, precio_maximo)
        if rango_fechas:
            st.session_state["filtro_fechas"] = rango_fechas

    st.session_state.setdefault("filtro_supermercados", supermercados)
    st.session_state.setdefault("filtro_busqueda", "")
    st.session_state.setdefault("filtro_precio", (precio_minimo, precio_maximo))

    if rango_fechas:
        st.session_state.setdefault("filtro_fechas", rango_fechas)

    supermercados_seleccionados = st.sidebar.multiselect(
        "Supermercado",
        supermercados,
        key="filtro_supermercados",
    )
    texto_busqueda = st.sidebar.text_input(
        "Filtrar por producto",
        placeholder="Ej. arroz, aceite, leche",
        key="filtro_busqueda",
    )
    rango_precio = st.sidebar.slider(
        "Rango de precios",
        min_value=precio_minimo,
        max_value=precio_maximo,
        key="filtro_precio",
        format="₲ %d",
    )

    rango_fecha = None
    if rango_fechas:
        valor_fecha = st.sidebar.date_input(
            "Período",
            min_value=rango_fechas[0],
            max_value=rango_fechas[1],
            key="filtro_fechas",
        )

        if isinstance(valor_fecha, tuple) and len(valor_fecha) == 2:
            rango_fecha = valor_fecha
        elif isinstance(valor_fecha, list) and len(valor_fecha) == 2:
            rango_fecha = tuple(valor_fecha)

    return supermercados_seleccionados, texto_busqueda, rango_precio, rango_fecha


def preparar_tabla(precios):
    """Prepara columnas visibles y precio formateado para la tabla."""
    columnas = [
        "supermercado",
        "nombre_producto",
        "precio",
        "unidad",
        "fecha_registro",
    ]
    columnas_existentes = [
        columna for columna in columnas if columna in precios.columns
    ]
    tabla = (
        precios.sort_values("fecha_registro", ascending=False)
        .drop_duplicates(subset=["nombre_producto", "supermercado"])
        [columnas_existentes]
        .copy()
    )
    tabla["precio"] = tabla["precio"].map(formatear_guaranies)
    tabla = tabla.fillna("")
    tabla = tabla.rename(
        columns={
            "supermercado": "Supermercado",
            "nombre_producto": "Producto",
            "precio": "Precio",
            "unidad": "Unidad",
            "fecha_registro": "Fecha",
        }
    )
    return tabla


def mostrar_resumen_filtros(precios_filtrados, total_precios, filtros):
    """Muestra un resumen visible de los filtros activos."""
    supermercados, texto_busqueda, rango_precio, rango_fecha = filtros
    chips = [
        f"{len(precios_filtrados):,} de {total_precios:,} registros".replace(",", "."),
        f"{len(supermercados)} supermercado(s)",
        f"{formatear_guaranies(rango_precio[0])} - {formatear_guaranies(rango_precio[1])}",
    ]

    if texto_busqueda.strip():
        chips.append(f'Producto: "{texto_busqueda.strip()}"')

    if rango_fecha:
        chips.append(f"{rango_fecha[0]} a {rango_fecha[1]}")

    chips_html = "".join(
        f'<span class="filter-chip">{escape(str(chip))}</span>' for chip in chips
    )
    st.markdown(
        f"""
        <div class="filter-summary">
            <strong>Filtros activos</strong>
            {chips_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def obtener_ultimos_precios(precios):
    """Retorna el registro mas reciente por producto y supermercado."""
    if precios.empty:
        return precios.copy()

    ordenados = precios.copy()
    ordenados["fecha_orden"] = pd.to_datetime(
        ordenados["fecha_registro"],
        errors="coerce",
    )
    ordenados = ordenados.sort_values(
        ["fecha_orden", "fecha_hora_registro"],
        na_position="first",
    )
    return ordenados.drop_duplicates(
        subset=["nombre_producto", "supermercado"],
        keep="last",
    )


def abreviar_texto(texto, limite=58):
    """Recorta textos largos para que el grafico mantenga buena lectura."""
    texto = str(texto).strip()

    if len(texto) <= limite:
        return texto

    return f"{texto[: limite - 3].rstrip()}..."


def mostrar_grafico(precios):
    """Muestra un grafico de precios para los productos filtrados."""
    mostrar_encabezado_seccion(
        "Gráfico de precios",
        "Compará visualmente los precios de los productos que coinciden con tu búsqueda.",
        "Comparación",
    )

    if precios.empty:
        st.info("No encontramos productos con esos filtros.")
        return

    ultimos_precios = obtener_ultimos_precios(precios)
    datos_grafico = (
        ultimos_precios.sort_values("precio", ascending=True)
        .drop_duplicates(subset=["nombre_producto", "supermercado"])
        .head(20)
        .copy()
    )
    datos_grafico = datos_grafico.sort_values("precio", ascending=True)

    if datos_grafico.empty:
        st.info("No hay productos suficientes para graficar con esos filtros.")
        return

    datos_grafico["producto_grafico"] = datos_grafico.apply(
        lambda fila: abreviar_texto(
            f"{fila['nombre_producto']} · {fila['supermercado']}"
        ),
        axis=1,
    )
    datos_grafico["precio_formateado"] = datos_grafico["precio"].map(
        formatear_guaranies
    )
    datos_grafico["fecha_registro"] = datos_grafico["fecha_registro"].astype(str)
    dominio_colores, colores_supermercado = obtener_colores_supermercados(
        sorted(datos_grafico["supermercado"].dropna().unique())
    )

    altura = max(300, min(620, len(datos_grafico) * 34))
    especificacion = {
        "background": "transparent",
        "height": altura,
        "config": {
            "view": {"stroke": None},
            "axis": {
                "labelColor": "#172033",
                "labelFontSize": 13,
                "labelFontWeight": 650,
                "titleColor": "#172033",
                "titleFontSize": 13,
                "titleFontWeight": 750,
                "domainColor": "#98A2B3",
                "gridColor": "#D0D5DD",
                "tickColor": "#98A2B3",
            },
            "legend": {
                "labelColor": "#172033",
                "labelFontSize": 13,
                "labelFontWeight": 650,
                "titleColor": "#172033",
                "titleFontSize": 13,
                "titleFontWeight": 750,
                "orient": "bottom",
            },
        },
        "encoding": {
            "x": {
                "field": "precio",
                "type": "quantitative",
                "title": "Precio",
                "axis": {
                    "format": ",.0f",
                    "labelColor": "#172033",
                    "titleColor": "#172033",
                },
            },
            "y": {
                "field": "producto_grafico",
                "type": "nominal",
                "title": None,
                "sort": {"field": "precio", "order": "ascending"},
                "axis": {
                    "labelColor": "#172033",
                    "labelLimit": 380,
                    "labelPadding": 10,
                    "labelFontWeight": 700,
                },
            },
        },
        "layer": [
            {
                "mark": {
                    "type": "bar",
                    "cornerRadiusEnd": 6,
                    "height": {"band": 0.62},
                },
                "encoding": {
                    "color": {
                        "field": "supermercado",
                        "type": "nominal",
                        "title": "Supermercado",
                        "scale": {
                            "domain": dominio_colores,
                            "range": colores_supermercado,
                        },
                    },
                    "tooltip": [
                        {"field": "nombre_producto", "type": "nominal", "title": "Producto"},
                        {"field": "supermercado", "type": "nominal", "title": "Supermercado"},
                        {"field": "precio_formateado", "type": "nominal", "title": "Precio"},
                        {"field": "fecha_registro", "type": "nominal", "title": "Fecha"},
                    ],
                },
            },
            {
                "mark": {
                    "type": "text",
                    "align": "left",
                    "baseline": "middle",
                    "dx": 6,
                    "color": "#0F172A",
                    "fontSize": 13,
                    "fontWeight": 800,
                },
                "encoding": {"text": {"field": "precio_formateado", "type": "nominal"}},
            },
        ],
    }

    st.vega_lite_chart(
        datos_grafico,
        especificacion,
        use_container_width=True,
    )
    st.caption("Se muestran hasta 20 resultados para mantener el gráfico legible.")

    st.markdown("### Tabla de productos")
    tabla_productos = datos_grafico[
        ["nombre_producto", "supermercado", "precio", "fecha_registro"]
    ].copy()
    tabla_productos["precio"] = tabla_productos["precio"].map(formatear_guaranies)
    st.dataframe(
        tabla_productos.head(100),
        hide_index=True,
        height=400,
    )


def mostrar_evolucion_precios(precios):
    """Muestra la evolucion historica de un producto por supermercado."""
    mostrar_encabezado_seccion(
        "Evolución de precios",
        "Elegí un producto y compará cómo se movió su precio en el tiempo.",
        "Histórico",
    )

    if precios.empty:
        st.info("No encontramos productos con esos filtros.")
        return

    productos = sorted(precios["nombre_producto"].dropna().unique())
    if not productos:
        st.info("No hay productos disponibles para analizar.")
        return

    with st.container(border=True):
        producto_seleccionado = st.selectbox(
            "Producto para analizar",
            productos,
            help="Seleccioná un producto para ver su precio en el tiempo.",
        )
    historial = precios[precios["nombre_producto"] == producto_seleccionado].copy()
    historial["fecha"] = pd.to_datetime(
        historial["fecha_registro"],
        errors="coerce",
    ).dt.normalize()
    historial = historial.dropna(subset=["fecha", "precio"])

    if historial["fecha"].nunique() < 2:
        st.info("No hay suficientes datos históricos para mostrar una evolución.")
        return

    agrupado = (
        historial.groupby(["fecha", "supermercado"], as_index=False)["precio"]
        .mean()
        .sort_values("fecha")
    )
    grafico = px.line(
        agrupado,
        x="fecha",
        y="precio",
        color="supermercado",
        template="plotly_white",
    )

    with st.container(border=True):
        st.plotly_chart(grafico, width="stretch")


def mostrar_tabla(precios):
    """Muestra la tabla final sin indice visible."""
    mostrar_encabezado_seccion(
        "Tabla completa",
        "Explorá todos los productos filtrados, ordenados de menor a mayor precio.",
        "Productos encontrados",
    )
    tabla = preparar_tabla(precios)
    st.dataframe(
        tabla,
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
    mostrar_resumen_filtros(precios_filtrados, len(precios), filtros)

    mostrar_grafico(precios_filtrados)
    mostrar_evolucion_precios(precios_filtrados)
    mostrar_tabla(precios_filtrados)


if __name__ == "__main__":
    mostrar_dashboard()
