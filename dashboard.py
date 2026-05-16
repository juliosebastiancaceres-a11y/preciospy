import os
import re
import sqlite3
from datetime import timedelta
from io import BytesIO
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from scraper import (
    normalizar_nombre_comparable,
    obtener_clave_matching_producto,
    obtener_etiqueta_matching_producto,
)
from supabase import create_client


RUTA_DB = Path(__file__).resolve().parent / "data" / "preciospy.db"
RUTA_ENV = Path(__file__).resolve().parent / ".env"
RUTA_LOGS = Path(__file__).resolve().parent / "logs"
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

            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] textarea,
            [data-testid="stSidebar"] [data-baseweb="input"],
            [data-testid="stSidebar"] [data-baseweb="input"] *,
            [data-testid="stSidebar"] [data-baseweb="select"],
            [data-testid="stSidebar"] [data-baseweb="select"] * {
                background-color: #FFFFFF !important;
                color: var(--py-text) !important;
                caret-color: var(--py-blue) !important;
            }

            [data-testid="stSidebar"] input::placeholder,
            [data-testid="stSidebar"] textarea::placeholder {
                color: #667085 !important;
                opacity: 1 !important;
            }

            [data-testid="stSelectbox"] [data-baseweb="select"],
            [data-testid="stMultiSelect"] [data-baseweb="select"],
            [data-baseweb="select"],
            [data-baseweb="select"] > div,
            [data-baseweb="select"] input,
            [data-baseweb="input"],
            [data-baseweb="input"] input {
                background-color: #FFFFFF !important;
                border-color: #D0D5DD !important;
                color: #101828 !important;
                -webkit-text-fill-color: #101828 !important;
                caret-color: var(--py-blue) !important;
            }

            [data-baseweb="select"] svg,
            [data-testid="stSelectbox"] svg,
            [data-testid="stMultiSelect"] svg {
                color: #344054 !important;
                fill: #344054 !important;
            }

            [data-baseweb="popover"],
            [data-baseweb="menu"],
            [role="listbox"] {
                background-color: #FFFFFF !important;
                border-color: #D0D5DD !important;
                color: #101828 !important;
            }

            [data-baseweb="option"],
            [data-baseweb="option"] *,
            [role="option"],
            [role="option"] * {
                background-color: #FFFFFF !important;
                color: #101828 !important;
            }

            [data-baseweb="option"]:hover,
            [role="option"]:hover {
                background-color: #EAF2FF !important;
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

            .health-grid {
                display: grid;
                gap: 0.85rem;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                margin-top: 1rem;
            }

            .health-card {
                animation: fadeInUp 520ms ease-out both;
                background: rgba(255, 255, 255, 0.82);
                border: 1px solid var(--py-border);
                border-radius: 14px;
                box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
                padding: 0.9rem 1rem;
                transition:
                    border-color 160ms ease,
                    box-shadow 160ms ease,
                    transform 160ms ease;
            }

            .health-card:hover {
                border-color: rgba(0, 56, 168, 0.22);
                box-shadow: 0 16px 34px rgba(0, 56, 168, 0.12);
                transform: translateY(-3px);
            }

            .health-label {
                color: var(--py-muted) !important;
                font-size: 0.72rem;
                font-weight: 760;
                text-transform: uppercase;
            }

            .health-value {
                color: var(--py-text) !important;
                font-size: 1rem;
                font-weight: 820;
                margin-top: 0.35rem;
            }

            .health-status-ok {
                color: var(--py-success) !important;
            }

            .health-status-warn {
                color: var(--py-warning) !important;
            }

            .health-card {
                animation: fadeInUp 420ms ease-out both;
                background: #FFFFFF;
                border: 1px solid var(--py-border);
                border-radius: 10px;
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
                min-height: 118px;
                padding: 0.9rem 0.95rem;
            }

            .health-label {
                color: #344054 !important;
                font-size: 0.74rem;
                font-weight: 760;
                line-height: 1.2;
                margin-bottom: 0.4rem;
            }

            .health-value {
                color: #101828 !important;
                font-size: clamp(1.05rem, 1.45vw, 1.35rem);
                font-weight: 820;
                line-height: 1.18;
                margin-bottom: 0.45rem;
                overflow-wrap: anywhere;
            }

            .health-desc {
                color: #475467 !important;
                font-size: 0.76rem;
                font-weight: 650;
                line-height: 1.28;
                overflow-wrap: anywhere;
            }

            [data-testid="stCaptionContainer"],
            [data-testid="stCaptionContainer"] * {
                color: #475467 !important;
            }

            .stApp p,
            .stApp span,
            .stApp label,
            .stApp div,
            .stApp h1,
            .stApp h2,
            .stApp h3,
            .stApp h4,
            .stApp h5,
            .stApp h6,
            [data-testid="stMetric"],
            [data-testid="stMetric"] *,
            [data-testid="stMarkdownContainer"],
            [data-testid="stMarkdownContainer"] *,
            [data-testid="stDataFrame"],
            [data-testid="stDataFrame"] *,
            [data-testid="stSelectbox"],
            [data-testid="stSelectbox"] *,
            [data-testid="stTextInput"],
            [data-testid="stTextInput"] *,
            [data-testid="stDateInput"],
            [data-testid="stDateInput"] *,
            [data-testid="stSlider"],
            [data-testid="stSlider"] * {
                color: var(--py-text) !important;
            }

            .py-hero,
            .py-hero *,
            .py-badge,
            .app-title,
            .app-subtitle,
            [data-testid="stSidebar"] .stButton > button,
            [data-testid="stSidebar"] .stButton > button * {
                color: var(--py-white) !important;
            }

            .py-badge.light,
            .py-badge.light * {
                color: var(--py-blue) !important;
            }

            [data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid var(--py-border);
                border-radius: 14px;
                padding: 0.85rem 1rem;
            }

            [data-testid="stMetricValue"],
            [data-testid="stMetricValue"] * {
                color: var(--py-text) !important;
                font-size: clamp(1rem, 1.7vw, 1.45rem) !important;
                font-weight: 780 !important;
                line-height: 1.15 !important;
                overflow: visible !important;
                text-overflow: clip !important;
                white-space: normal !important;
                word-break: break-word !important;
            }

            [data-testid="stMetricLabel"],
            [data-testid="stMetricLabel"] * {
                color: var(--py-muted) !important;
                font-size: 0.75rem !important;
                font-weight: 760 !important;
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
                .health-card,
                [data-testid="stProgress"] [role="progressbar"]::after {
                    animation: none;
                }

                .metric-card,
                .content-card,
                .filter-summary,
                [data-testid="stVegaLiteChart"],
                [data-testid="stDataFrame"],
                [data-testid="stVerticalBlockBorderWrapper"],
                .health-card {
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

                .health-grid {
                    grid-template-columns: 1fr;
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

    precios = precios.dropna(subset=["nombre_producto", "supermercado"]).copy()
    precios["precio"] = pd.to_numeric(precios["precio"], errors="coerce")
    precios["fecha_registro"] = precios["fecha_registro"].astype(str)
    precios["fecha_registro_dt"] = pd.to_datetime(
        precios["fecha_registro"],
        errors="coerce",
    )
    nombres_unicos = precios["nombre_producto"].dropna().unique()
    nombres_normalizados = {
        nombre: normalizar_nombre_comparable(nombre) for nombre in nombres_unicos
    }
    claves_matching = {
        nombre: obtener_clave_matching_producto(nombre) for nombre in nombres_unicos
    }
    etiquetas_matching = {
        nombre: obtener_etiqueta_matching_producto(nombre) for nombre in nombres_unicos
    }
    precios["nombre_normalizado"] = precios["nombre_producto"].map(nombres_normalizados)
    precios["clave_matching"] = precios["nombre_producto"].map(claves_matching)
    precios["etiqueta_matching"] = precios["nombre_producto"].map(etiquetas_matching)
    return precios.dropna(subset=["precio"])


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


def obtener_configuracion_secreta(nombre):
    """Lee configuracion desde entorno local o secretos de Streamlit Cloud."""
    valor = os.getenv(nombre)

    if valor:
        return valor

    try:
        return st.secrets.get(nombre)
    except Exception:
        return None


def cargar_precios_supabase():
    """Carga precios desde Supabase si esta configurado."""
    load_dotenv(RUTA_ENV)
    url = obtener_configuracion_secreta("SUPABASE_URL")
    key = obtener_configuracion_secreta("SUPABASE_KEY")

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
def cargar_precios_con_fuente():
    """Carga precios y retorna la fuente activa."""
    precios = cargar_precios_sqlite()

    if not precios.empty:
        return precios, "SQLite local"

    return cargar_precios_supabase(), "Supabase"


def cargar_precios():
    """Carga precios desde la fuente disponible."""
    precios, _ = cargar_precios_con_fuente()
    return precios


def formatear_guaranies(precio):
    """Formatea precios con separador de miles paraguayo."""
    return f"₲ {int(round(precio)):,.0f}".replace(",", ".")


def reconciliar_supermercados_seleccionados(
    seleccion_guardada,
    supermercados,
    supermercados_anteriores=None,
):
    """Conserva seleccion valida y agrega solo supermercados recien detectados."""
    if seleccion_guardada is None:
        return list(supermercados)

    seleccion_valida = [
        supermercado
        for supermercado in seleccion_guardada
        if supermercado in supermercados
    ]
    supermercados_anteriores_lista = list(supermercados_anteriores or supermercados)
    supermercados_anteriores = set(supermercados_anteriores_lista)
    seleccion_era_total = bool(supermercados_anteriores) and supermercados_anteriores.issubset(
        set(seleccion_guardada)
    )

    supermercados_nuevos = [
        supermercado
        for supermercado in supermercados
        if supermercado not in supermercados_anteriores
    ]

    if seleccion_era_total:
        return seleccion_valida + supermercados_nuevos

    return seleccion_valida + supermercados_nuevos


def obtener_colores_supermercados(supermercados):
    """Asigna colores consistentes a cada supermercado del grafico."""
    colores_fijos = {
        "stock": "#0038A8",
        "superseis": "#2E7D32",
        "biggie": "#C6051D",
        "los jardines": "#D6A300",
        "casa rica": "#101828",
        "areté": "#38BDF8",
        "arete": "#38BDF8",
    }
    paleta_respaldo = ["#0038A8", "#12805C", "#7C3AED", "#C47A00", "#38BDF8"]
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


def preparar_terminos_busqueda(texto_busqueda):
    """Convierte una busqueda vaga en terminos normalizados independientes."""
    texto_normalizado = normalizar_nombre_comparable(texto_busqueda)

    if not texto_normalizado:
        return []

    tokens = texto_normalizado.split()
    unidades = {"L", "ml", "g", "kg"}
    terminos = []
    indice = 0

    while indice < len(tokens):
        token = tokens[indice]
        siguiente = tokens[indice + 1] if indice + 1 < len(tokens) else ""

        if siguiente in unidades:
            terminos.append(f"{token} {siguiente}")
            indice += 2
            continue

        terminos.append(token)
        indice += 1

    return terminos


def filtrar_por_busqueda_inteligente(precios, texto_busqueda):
    """Busca por nombre usando terminos separados y nombres normalizados."""
    texto_busqueda = str(texto_busqueda or "").strip()

    if not texto_busqueda or precios.empty:
        return precios

    columnas_busqueda = [
        "nombre_producto",
        "nombre_normalizado",
        "clave_matching",
        "etiqueta_matching",
    ]
    columnas_busqueda = [
        columna for columna in columnas_busqueda if columna in precios.columns
    ]

    if not columnas_busqueda:
        return precios

    terminos = preparar_terminos_busqueda(texto_busqueda)
    filtro = precios["nombre_producto"].str.contains(
        texto_busqueda,
        case=False,
        na=False,
        regex=False,
    )

    if terminos:
        filtro_terminos = pd.Series(True, index=precios.index)
        for termino in terminos:
            filtro_termino = pd.Series(False, index=precios.index)
            for columna in columnas_busqueda:
                filtro_termino = filtro_termino | precios[columna].astype(
                    str
                ).str.contains(
                    termino,
                    case=False,
                    na=False,
                    regex=False,
                )
            filtro_terminos = filtro_terminos & filtro_termino

        filtro = filtro | filtro_terminos

    return precios[filtro].copy()


def aplicar_estilo_plotly_legible(grafico):
    """Refuerza contraste de textos, ejes y tooltips en graficos Plotly."""
    color_texto = "#101828"
    color_secundario = "#344054"
    color_grilla = "#D0D5DD"

    grafico.update_layout(
        font=dict(color=color_texto, size=13),
        title_font=dict(color=color_texto, size=16),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        legend=dict(
            bgcolor="rgba(255,255,255,0.94)",
            bordercolor="#E4E7EC",
            borderwidth=1,
            font=dict(color=color_texto, size=12),
            title_font=dict(color=color_texto, size=12),
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#98A2B3",
            font=dict(color=color_texto, size=12),
        ),
    )
    grafico.update_xaxes(
        color=color_texto,
        gridcolor=color_grilla,
        linecolor="#98A2B3",
        tickcolor="#98A2B3",
        tickfont=dict(color=color_texto, size=12),
        title_font=dict(color=color_secundario, size=13),
        zerolinecolor="#98A2B3",
    )
    grafico.update_yaxes(
        color=color_texto,
        gridcolor=color_grilla,
        linecolor="#98A2B3",
        tickcolor="#98A2B3",
        tickfont=dict(color=color_texto, size=12),
        title_font=dict(color=color_secundario, size=13),
        zerolinecolor="#98A2B3",
    )
    grafico.update_traces(
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#98A2B3",
            font=dict(color=color_texto),
        )
    )
    return grafico


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
        filtrados = filtrar_por_busqueda_inteligente(filtrados, texto_busqueda)

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


def formatear_fecha_hora(valor):
    """Formatea una fecha/hora para mostrarla en el dashboard."""
    if not valor:
        return "Sin datos"

    fecha = pd.to_datetime(valor, errors="coerce")

    if pd.isna(fecha):
        return str(valor)

    return fecha.strftime("%Y-%m-%d %H:%M")


def obtener_ultima_sincronizacion(precios):
    """Obtiene la ultima fecha/hora disponible en los datos cargados."""
    if precios.empty:
        return "Sin datos"

    if "fecha_hora_registro" in precios.columns:
        fechas_hora = pd.to_datetime(
            precios["fecha_hora_registro"],
            errors="coerce",
        ).dropna()

        if not fechas_hora.empty:
            return formatear_fecha_hora(fechas_hora.max())

    fecha_registro = pd.to_datetime(precios["fecha_registro"], errors="coerce").dropna()

    if fecha_registro.empty:
        return "Sin datos"

    return fecha_registro.max().strftime("%Y-%m-%d")


def obtener_estado_monitoreo(precios, hoy=None):
    """Resume continuidad del monitoreo entre la primera fecha registrada y hoy."""
    if precios.empty or "fecha_registro" not in precios.columns:
        return {
            "primera_fecha": None,
            "ultima_fecha": None,
            "dias_registrados": 0,
            "dias_calendario": 0,
            "dias_faltantes": [],
            "dias_sin_datos": 0,
            "al_dia": False,
        }

    fechas = pd.to_datetime(precios["fecha_registro"], errors="coerce").dropna()

    if fechas.empty:
        return {
            "primera_fecha": None,
            "ultima_fecha": None,
            "dias_registrados": 0,
            "dias_calendario": 0,
            "dias_faltantes": [],
            "dias_sin_datos": 0,
            "al_dia": False,
        }

    fechas_registradas = {fecha.date() for fecha in fechas}
    primera_fecha = min(fechas_registradas)
    ultima_fecha = max(fechas_registradas)
    hoy = hoy or pd.Timestamp.today().date()
    hoy = pd.Timestamp(hoy).date()
    fecha_final = max(hoy, ultima_fecha)
    rango_esperado = pd.date_range(primera_fecha, fecha_final, freq="D")
    dias_faltantes = [
        fecha.date()
        for fecha in rango_esperado
        if fecha.date() not in fechas_registradas
    ]
    dias_sin_datos = max((hoy - ultima_fecha).days, 0)

    return {
        "primera_fecha": primera_fecha,
        "ultima_fecha": ultima_fecha,
        "dias_registrados": len(fechas_registradas),
        "dias_calendario": len(rango_esperado),
        "dias_faltantes": dias_faltantes,
        "dias_sin_datos": dias_sin_datos,
        "al_dia": not dias_faltantes and dias_sin_datos == 0,
    }


def obtener_estado_monitoreo_supermercados(precios, hoy=None):
    """Resume continuidad del monitoreo de forma independiente por supermercado."""
    if (
        precios.empty
        or "fecha_registro" not in precios.columns
        or "supermercado" not in precios.columns
    ):
        return []

    datos = precios[["supermercado", "fecha_registro"]].copy()
    datos["fecha"] = pd.to_datetime(datos["fecha_registro"], errors="coerce").dt.date
    datos["supermercado"] = datos["supermercado"].fillna("").astype(str).str.strip()
    datos = datos[(datos["supermercado"] != "") & datos["fecha"].notna()]

    if datos.empty:
        return []

    hoy = hoy or pd.Timestamp.today().date()
    hoy = pd.Timestamp(hoy).date()
    estados = []

    for supermercado, grupo in datos.groupby("supermercado"):
        fechas_registradas = set(grupo["fecha"])
        primera_fecha = min(fechas_registradas)
        ultima_fecha = max(fechas_registradas)
        fecha_final = max(hoy, ultima_fecha)
        rango_esperado = pd.date_range(primera_fecha, fecha_final, freq="D")
        dias_faltantes = [
            fecha.date()
            for fecha in rango_esperado
            if fecha.date() not in fechas_registradas
        ]

        estados.append(
            {
                "supermercado": supermercado,
                "primera_fecha": primera_fecha,
                "ultima_fecha": ultima_fecha,
                "dias_registrados": len(fechas_registradas),
                "dias_calendario": len(rango_esperado),
                "dias_faltantes": dias_faltantes,
                "dias_sin_datos": max((hoy - ultima_fecha).days, 0),
                "al_dia": not dias_faltantes and ultima_fecha >= hoy,
            }
        )

    return sorted(estados, key=lambda estado: estado["supermercado"].lower())


def preparar_tabla_monitoreo_supermercados(estados):
    """Prepara una tabla legible de continuidad por supermercado."""
    filas = []

    for estado in estados:
        filas.append(
            {
                "Supermercado": estado["supermercado"],
                "Primera fecha": estado["primera_fecha"].strftime("%Y-%m-%d"),
                "Última fecha": estado["ultima_fecha"].strftime("%Y-%m-%d"),
                "Días con datos": estado["dias_registrados"],
                "Días faltantes": len(estado["dias_faltantes"]),
                "Días sin datos": estado["dias_sin_datos"],
                "Fechas faltantes": formatear_fechas_faltantes(
                    estado["dias_faltantes"],
                    limite=6,
                ),
            }
        )

    return pd.DataFrame(filas)


def formatear_fechas_faltantes(fechas, limite=4):
    """Formatea fechas faltantes para mostrarlas en una tarjeta compacta."""
    if len(fechas) == 0:
        return "Sin faltantes"

    fechas_texto = [fecha.strftime("%Y-%m-%d") for fecha in fechas[:limite]]
    faltantes_extra = len(fechas) - limite

    if faltantes_extra > 0:
        fechas_texto.append(f"+{faltantes_extra} más")

    return ", ".join(fechas_texto)


def extraer_primer_valor_log(patron, contenido, defecto=""):
    """Extrae el primer valor textual de un bloque de log."""
    match = re.search(patron, contenido, flags=re.MULTILINE)
    return match.group(1).strip() if match else defecto


def extraer_ultimo_valor_log(patron, contenido, defecto=""):
    """Extrae el ultimo valor textual de un bloque de log."""
    matches = re.findall(patron, contenido, flags=re.MULTILINE)
    return matches[-1].strip() if matches else defecto


def sumar_valores_log(patron, contenido):
    """Suma valores numericos presentes en un bloque de log."""
    return sum(int(valor) for valor in re.findall(patron, contenido, flags=re.MULTILINE))


def calcular_segundos_corrida(inicio, fin):
    """Calcula la duracion en segundos de un paso del scraper."""
    if not inicio or not fin:
        return None

    inicio_fecha = pd.to_datetime(inicio, errors="coerce", utc=True)
    fin_fecha = pd.to_datetime(fin, errors="coerce", utc=True)

    if pd.isna(inicio_fecha) or pd.isna(fin_fecha):
        return None

    duracion = fin_fecha - inicio_fecha
    if duracion < timedelta(0):
        return None

    return int(duracion.total_seconds())


def formatear_duracion_segundos(segundos):
    """Formatea una duracion en segundos para mostrarla en el dashboard."""
    if segundos is None:
        return "Sin dato"

    horas, resto = divmod(segundos, 3600)
    minutos, segundos = divmod(resto, 60)

    if horas:
        return f"{horas} h {minutos} min"
    if minutos:
        return f"{minutos} min {segundos} s"
    return f"{segundos} s"


def formatear_duracion_corrida(inicio, fin):
    """Calcula y formatea la duracion de un paso del scraper."""
    return formatear_duracion_segundos(calcular_segundos_corrida(inicio, fin))


def parsear_secciones_log_scraper(contenido):
    """Extrae el detalle por supermercado o paso desde un log del scraper."""
    secciones = []
    seccion_actual = None

    for linea in contenido.splitlines():
        titulo_match = re.match(r"^==\s*(.+?)\s*==$", linea.strip())
        if titulo_match:
            if seccion_actual:
                secciones.append(seccion_actual)
            seccion_actual = {"nombre": titulo_match.group(1).strip(), "lineas": []}
            continue

        if seccion_actual is not None:
            seccion_actual["lineas"].append(linea)

    if seccion_actual:
        secciones.append(seccion_actual)

    detalles = []
    for seccion in secciones:
        bloque = "\n".join(seccion["lineas"])
        inicio = extraer_primer_valor_log(r"Inicio:\s*(.+)", bloque)
        fin = extraer_ultimo_valor_log(r"Fin:\s*(.+)", bloque)
        duracion_segundos = calcular_segundos_corrida(inicio, fin)
        codigo_texto = extraer_ultimo_valor_log(r"Codigo de salida:\s*(\d+)", bloque)
        codigo = int(codigo_texto) if codigo_texto else None
        ok = codigo == 0
        lineas_error = [
            linea.strip()
            for linea in seccion["lineas"]
            if "Error " in linea or "Traceback" in linea or "Client Error" in linea
        ]
        errores = [] if ok else lineas_error
        advertencias = lineas_error if ok else []

        detalles.append(
            {
                "nombre": seccion["nombre"],
                "inicio": inicio,
                "fin": fin,
                "codigo": codigo,
                "estado": "OK" if ok else "Error",
                "duracion": formatear_duracion_segundos(duracion_segundos),
                "duracion_segundos": duracion_segundos,
                "scrapeados": sumar_valores_log(
                    r"Productos scrapeados:\s*(\d+)", bloque
                ),
                "sqlite": sumar_valores_log(
                    r"Productos guardados en SQLite:\s*(\d+)", bloque
                ),
                "supabase": sumar_valores_log(
                    r"Productos sincronizados con Supabase:\s*(\d+)", bloque
                ),
                "sqlite_revisados": sumar_valores_log(
                    r"Registros validos en SQLite:\s*(\d+)", bloque
                ),
                "supabase_existentes": sumar_valores_log(
                    r"Claves existentes en Supabase:\s*(\d+)", bloque
                ),
                "historicos": sumar_valores_log(
                    r"Historicos enviados a Supabase:\s*(\d+)", bloque
                ),
                "duplicados": sumar_valores_log(
                    r"Productos duplicados omitidos antes de Supabase:\s*(\d+)",
                    bloque,
                ),
                "faltantes": sumar_valores_log(
                    r"Registros faltantes detectados:\s*(\d+)", bloque
                ),
                "errores": len(errores),
                "advertencias": len(advertencias),
                "ultimo_error": errores[-1][:180] if errores else "",
            }
        )

    return detalles


def preparar_tabla_ultima_corrida(log):
    """Prepara una tabla tecnica con el resultado del ultimo scraper."""
    filas = []

    for seccion in log.get("secciones", []):
        filas.append(
            {
                "Paso": seccion["nombre"],
                "Estado": seccion["estado"],
                "Scrapeados": seccion["scrapeados"],
                "SQLite": seccion["sqlite"],
                "Supabase": seccion["supabase"],
                "SQLite revisados": seccion["sqlite_revisados"],
                "Supabase existentes": seccion["supabase_existentes"],
                "Históricos": seccion["historicos"],
                "Duplicados": seccion["duplicados"],
                "Faltantes": seccion["faltantes"],
                "Avisos": seccion["advertencias"],
                "Errores": seccion["errores"],
                "Código": "" if seccion["codigo"] is None else seccion["codigo"],
                "Duración": seccion["duracion"],
                "Inicio": seccion["inicio"],
                "Fin": seccion["fin"],
            }
        )

    return pd.DataFrame(filas)


def obtener_estado_visual_corrida(seccion):
    """Devuelve un estado simple para leer rapido el monitoreo."""
    if seccion["errores"] > 0 or seccion["estado"] != "OK":
        return "Error"
    if seccion["advertencias"] > 0:
        return "OK con avisos"
    return "OK"


def simplificar_nombre_paso_corrida(nombre):
    """Acorta nombres tecnicos del log para la vista de monitoreo."""
    if nombre == "Sincronizar faltantes SQLite -> Supabase":
        return "Sync final"
    return nombre


def preparar_tabla_monitoreo_corrida(log):
    """Prepara una tabla compacta para usuarios del dashboard."""
    filas = []

    for seccion in log.get("secciones", []):
        sincronizados = seccion["supabase"] + seccion["historicos"]
        if seccion["nombre"] == "Sincronizar faltantes SQLite -> Supabase":
            sincronizados = seccion["sqlite_revisados"]

        filas.append(
            {
                "Paso": simplificar_nombre_paso_corrida(seccion["nombre"]),
                "Estado": obtener_estado_visual_corrida(seccion),
                "Scrapeados": seccion["scrapeados"],
                "Sincronizados": sincronizados,
                "Duración": seccion["duracion"],
                "Avisos": seccion["advertencias"],
                "Pendientes": seccion["faltantes"],
            }
        )

    return pd.DataFrame(filas)


def colorear_tabla_monitoreo_corrida(fila):
    """Aplica colores de semaforo a la tabla de monitoreo."""
    estado = fila.get("Estado")
    if estado == "Error":
        fondo = "background-color: #FEE4E2; color: #7A271A;"
    elif estado == "OK con avisos":
        fondo = "background-color: #FEF0C7; color: #7A4E00;"
    else:
        fondo = "background-color: #D1FADF; color: #054F31;"

    return [fondo if columna == "Estado" else "" for columna in fila.index]


def obtener_umbral_duracion_corrida(nombre):
    """Define umbrales simples para alertar duraciones anormales."""
    if nombre == "Casa Rica":
        return 6 * 60 * 60
    if nombre == "Areté":
        return 2 * 60 * 60
    if nombre == "Sincronizar faltantes SQLite -> Supabase":
        return 15 * 60
    return 60 * 60


def preparar_alertas_monitoreo_corrida(log):
    """Genera alertas accionables sobre la ultima corrida del scraper."""
    alertas = []

    for seccion in log.get("secciones", []):
        nombre = simplificar_nombre_paso_corrida(seccion["nombre"])
        es_sync_final = seccion["nombre"] == "Sincronizar faltantes SQLite -> Supabase"

        if seccion["estado"] != "OK" or seccion["errores"] > 0:
            detalle = seccion["ultimo_error"] or "El paso terminó con error."
            alertas.append(
                {
                    "nivel": "error",
                    "titulo": f"{nombre} falló",
                    "detalle": detalle,
                }
            )
            continue

        if not es_sync_final and seccion["scrapeados"] == 0:
            alertas.append(
                {
                    "nivel": "warning",
                    "titulo": f"{nombre} no trajo productos",
                    "detalle": "Revisá si cambió la página o si el sitio no respondió.",
                }
            )

        if seccion["advertencias"] > 0:
            alertas.append(
                {
                    "nivel": "warning",
                    "titulo": f"{nombre} terminó con avisos",
                    "detalle": f"{seccion['advertencias']} aviso(s) recuperados durante la corrida.",
                }
            )

        umbral = obtener_umbral_duracion_corrida(seccion["nombre"])
        duracion = seccion["duracion_segundos"]
        if duracion is not None and duracion > umbral:
            alertas.append(
                {
                    "nivel": "warning",
                    "titulo": f"{nombre} tardó más de lo esperado",
                    "detalle": f"Duración: {seccion['duracion']}.",
                }
            )

    if not alertas and log.get("ok"):
        alertas.append(
            {
                "nivel": "success",
                "titulo": "Última corrida sin alertas",
                "detalle": "Todos los pasos terminaron dentro de los valores esperados.",
            }
        )

    return alertas


def mostrar_alertas_monitoreo_corrida(log):
    """Muestra alertas operativas de la ultima corrida."""
    alertas = preparar_alertas_monitoreo_corrida(log)

    for alerta in alertas[:5]:
        mensaje = f"{alerta['titulo']}: {alerta['detalle']}"
        if alerta["nivel"] == "error":
            st.error(mensaje)
        elif alerta["nivel"] == "warning":
            st.warning(mensaje)
        else:
            st.success(mensaje)

    if len(alertas) > 5:
        st.caption(f"{len(alertas) - 5} alerta(s) más en la tabla de monitoreo.")


def parsear_log_scraper(ruta_log, lineas_detalle=40):
    """Extrae resumen operativo de un archivo de log del scraper."""
    contenido = ruta_log.read_text(encoding="utf-8", errors="replace")
    lineas = contenido.splitlines()
    secciones = parsear_secciones_log_scraper(contenido)
    estado_match = re.search(r"Estado final:\s*(\d+)", contenido)
    codigos = [int(valor) for valor in re.findall(r"Codigo de salida:\s*(\d+)", contenido)]
    scrapeados = sum(
        int(valor) for valor in re.findall(r"Productos scrapeados:\s*(\d+)", contenido)
    )
    guardados_sqlite = sum(
        int(valor)
        for valor in re.findall(r"Productos guardados en SQLite:\s*(\d+)", contenido)
    )
    sincronizados = sum(
        int(valor)
        for valor in re.findall(r"Productos sincronizados con Supabase:\s*(\d+)", contenido)
    )
    errores_detectados = [
        linea.strip()
        for linea in lineas
        if "Error " in linea or "Traceback" in linea or "Client Error" in linea
    ]
    fecha_match = re.search(r"Fecha:\s*(.+)", contenido)
    inicio_match = re.search(r"Inicio:\s*(.+)", contenido)
    fin_matches = re.findall(r"Fin:\s*(.+)", contenido)
    estado = estado_match.group(1) if estado_match else "desconocido"
    ok = estado == "0" and all(codigo == 0 for codigo in codigos)
    errores = [] if ok else errores_detectados
    advertencias = errores_detectados if ok else []

    if errores:
        ultimo_error = errores[-1][:180]
    elif advertencias:
        ultimo_error = f"Sin errores críticos ({len(advertencias)} aviso(s) recuperados)"
    else:
        ultimo_error = "Sin errores"

    return {
        "archivo": ruta_log.name,
        "fecha": fecha_match.group(1).strip() if fecha_match else "",
        "inicio": inicio_match.group(1).strip() if inicio_match else "",
        "fin": fin_matches[-1].strip() if fin_matches else "",
        "estado": f"OK ({estado})" if estado == "0" else f"Error ({estado})",
        "scrapeados": scrapeados,
        "sqlite": guardados_sqlite,
        "supabase": sincronizados,
        "errores": len(errores),
        "advertencias": len(advertencias),
        "ultimo_error": ultimo_error,
        "detalle": "\n".join(lineas[-lineas_detalle:]),
        "secciones": secciones,
        "ok": ok,
    }


def obtener_logs_scraper(limite=5):
    """Lee los ultimos logs locales del scraper."""
    logs = sorted(RUTA_LOGS.glob("scraper-*.log"), reverse=True)[:limite]
    registros = []

    for ruta_log in logs:
        try:
            registros.append(parsear_log_scraper(ruta_log))
        except OSError as error:
            registros.append(
                {
                    "archivo": ruta_log.name,
                    "fecha": "",
                    "inicio": "",
                    "fin": "",
                    "estado": "Error lectura",
                    "scrapeados": 0,
                    "sqlite": 0,
                    "supabase": 0,
                    "errores": 1,
                    "advertencias": 0,
                    "ultimo_error": str(error),
                    "detalle": "",
                    "secciones": [],
                    "ok": False,
                }
            )

    return registros


def obtener_salud_scraper():
    """Lee el ultimo log local del scraper y extrae datos operativos."""
    logs = obtener_logs_scraper(limite=1)

    if not logs:
        return {
            "ultimo_log": "Sin logs",
            "estado": "Sin datos",
            "sincronizados": "Sin datos",
            "errores": "Sin logs locales",
            "ok": False,
        }

    ultimo_log = logs[0]

    return {
        "ultimo_log": ultimo_log["archivo"].replace("scraper-", "").replace(".log", ""),
        "estado": ultimo_log["estado"],
        "sincronizados": f"{ultimo_log['supabase']:,}".replace(",", "."),
        "errores": ultimo_log["ultimo_error"],
        "ok": ultimo_log["ok"],
    }


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


def mostrar_salud_sistema(precios, fuente):
    """Muestra una mini vista de salud operativa del sistema."""
    salud = obtener_salud_scraper()
    logs_scraper = obtener_logs_scraper(limite=1)
    ultimo_log_scraper = logs_scraper[0] if logs_scraper else None
    monitoreo = obtener_estado_monitoreo(precios)
    monitoreo_supermercados = obtener_estado_monitoreo_supermercados(precios)
    supermercados_con_huecos = [
        estado
        for estado in monitoreo_supermercados
        if estado["dias_faltantes"] or estado["dias_sin_datos"] > 0
    ]
    faltantes_texto = formatear_fechas_faltantes(monitoreo["dias_faltantes"])
    tarjetas = [
        ("Fuente actual", fuente, "Datos activos del dashboard"),
        (
            "Última sincronización",
            obtener_ultima_sincronizacion(precios),
            "Fecha/hora más reciente en datos",
        ),
        (
            "Último scraper local",
            salud["estado"],
            salud["ultimo_log"],
        ),
        (
            "Productos sincronizados",
            salud["sincronizados"],
            salud["errores"],
        ),
        (
            "Días sin datos",
            monitoreo["dias_sin_datos"],
            faltantes_texto,
        ),
        (
            "Huecos por súper",
            len(supermercados_con_huecos),
            "Supermercados con días faltantes",
        ),
    ]
    columnas = st.columns(6)

    for columna, (etiqueta, valor, descripcion) in zip(columnas, tarjetas):
        columna.markdown(
            f"""
            <div class="health-card">
                <div class="health-label">{escape(str(etiqueta))}</div>
                <div class="health-value">{escape(str(valor))}</div>
                <div class="health-desc">{escape(str(descripcion))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if monitoreo_supermercados:
        tabla_monitoreo = preparar_tabla_monitoreo_supermercados(
            monitoreo_supermercados
        )
        with st.expander("Cobertura de monitoreo por supermercado", expanded=False):
            st.dataframe(
                tabla_monitoreo,
                hide_index=True,
                width="stretch",
                height=min(260, 86 + len(tabla_monitoreo) * 36),
            )

    if ultimo_log_scraper:
        tabla_corrida = preparar_tabla_monitoreo_corrida(ultimo_log_scraper)
        if not tabla_corrida.empty:
            with st.expander("Última corrida del scraper", expanded=True):
                st.caption(
                    f"{ultimo_log_scraper['archivo']} · "
                    f"{ultimo_log_scraper['estado']} · "
                    f"Inicio: {ultimo_log_scraper['inicio'] or 'Sin dato'} · "
                    f"Fin: {ultimo_log_scraper['fin'] or 'Sin dato'}"
                )
                mostrar_alertas_monitoreo_corrida(ultimo_log_scraper)
                st.dataframe(
                    tabla_corrida.style.apply(
                        colorear_tabla_monitoreo_corrida,
                        axis=1,
                    ),
                    hide_index=True,
                    width="stretch",
                    height=min(320, 86 + len(tabla_corrida) * 36),
                )


def mostrar_logs_scraper():
    """Muestra una vista resumida de los ultimos logs locales del scraper."""
    logs = obtener_logs_scraper(limite=8)

    if not logs:
        with st.expander("Logs del scraper"):
            st.info("Todavía no hay logs locales del scraper para mostrar.")
        return

    resumen = pd.DataFrame(
        [
            {
                "Archivo": log["archivo"],
                "Estado": log["estado"],
                "Fecha": log["fecha"],
                "Productos scrapeados": log["scrapeados"],
                "SQLite": log["sqlite"],
                "Supabase": log["supabase"],
                "Errores": log["errores"],
                "Último error": log["ultimo_error"],
            }
            for log in logs
        ]
    )

    with st.expander("Logs técnicos del scraper"):
        st.dataframe(
            resumen,
            hide_index=True,
            width="stretch",
            height=min(320, 86 + len(resumen) * 36),
        )

        for log in logs[:3]:
            etiqueta = (
                f"{log['estado']} · {log['archivo']} · "
                f"Supabase: {log['supabase']:,}".replace(",", ".")
            )
            with st.expander(etiqueta):
                st.caption(
                    f"Inicio: {log['inicio'] or 'Sin dato'} · "
                    f"Fin: {log['fin'] or 'Sin dato'}"
                )
                st.code(log["detalle"] or "Sin detalle disponible.", language="text")


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

    st.session_state["filtro_supermercados"] = (
        reconciliar_supermercados_seleccionados(
            st.session_state.get("filtro_supermercados"),
            supermercados,
            st.session_state.get("filtro_supermercados_disponibles"),
        )
    )
    st.session_state["filtro_supermercados_disponibles"] = supermercados

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


def preparar_exportacion_historico(precios):
    """Prepara registros historicos filtrados para descarga."""
    columnas = [
        "supermercado",
        "nombre_producto",
        "nombre_normalizado",
        "clave_matching",
        "precio",
        "unidad",
        "fecha_registro",
        "fecha_hora_registro",
        "moneda",
    ]
    columnas_existentes = [columna for columna in columnas if columna in precios.columns]
    historico = precios[columnas_existentes].copy()

    if historico.empty:
        return historico

    historico["precio_formateado"] = historico["precio"].map(formatear_guaranies)
    columnas_orden = [
        columna
        for columna in ["fecha_registro", "supermercado", "nombre_producto"]
        if columna in historico.columns
    ]

    if columnas_orden:
        historico = historico.sort_values(
            columnas_orden,
            ascending=[False] + [True] * (len(columnas_orden) - 1),
        )

    return historico.rename(
        columns={
            "supermercado": "Supermercado",
            "nombre_producto": "Producto",
            "nombre_normalizado": "Nombre normalizado",
            "clave_matching": "Clave matching",
            "precio": "Precio",
            "precio_formateado": "Precio formateado",
            "unidad": "Unidad",
            "fecha_registro": "Fecha",
            "fecha_hora_registro": "Fecha hora",
            "moneda": "Moneda",
        }
    ).fillna("")


def convertir_a_csv(dataframe):
    """Convierte un dataframe a CSV compatible con planillas."""
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def convertir_a_excel(hojas):
    """Convierte varias tablas a un archivo Excel en memoria."""
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as escritor:
        for nombre_hoja, dataframe in hojas.items():
            hoja = str(nombre_hoja)[:31]
            dataframe.to_excel(escritor, sheet_name=hoja, index=False)
            worksheet = escritor.sheets[hoja]

            for indice, columna in enumerate(dataframe.columns):
                ancho = max(
                    len(str(columna)),
                    dataframe[columna].astype(str).str.len().max()
                    if not dataframe.empty
                    else 0,
                )
                worksheet.set_column(indice, indice, min(max(ancho + 2, 12), 42))

    return buffer.getvalue()


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


def obtener_ultimos_precios_comparables(precios):
    """Retorna el ultimo precio por nombre normalizado y supermercado."""
    if precios.empty:
        return precios.copy()

    comparables = precios.copy()

    if "nombre_normalizado" not in comparables.columns:
        comparables["nombre_normalizado"] = comparables["nombre_producto"].apply(
            normalizar_nombre_comparable
        )
    if "clave_matching" not in comparables.columns:
        comparables["clave_matching"] = comparables["nombre_producto"].apply(
            obtener_clave_matching_producto
        )
    if "etiqueta_matching" not in comparables.columns:
        comparables["etiqueta_matching"] = comparables["nombre_producto"].apply(
            obtener_etiqueta_matching_producto
        )

    comparables = comparables[
        comparables["clave_matching"].fillna("").astype(str).str.len() > 0
    ].copy()
    comparables["fecha_orden"] = pd.to_datetime(
        comparables["fecha_registro"],
        errors="coerce",
    )
    comparables["fecha_hora_orden"] = pd.to_datetime(
        comparables.get("fecha_hora_registro"),
        errors="coerce",
    )
    comparables = comparables.sort_values(
        ["fecha_orden", "fecha_hora_orden", "precio"],
        ascending=[False, False, True],
        na_position="last",
    )
    return comparables.drop_duplicates(
        subset=["clave_matching", "supermercado"],
        keep="first",
    )


def preparar_comparacion_supermercados(precios):
    """Prepara coincidencias comparables entre supermercados."""
    ultimos = obtener_ultimos_precios_comparables(precios)

    if ultimos.empty or ultimos["supermercado"].nunique() < 2:
        return pd.DataFrame()

    filas = []
    supermercados = sorted(ultimos["supermercado"].dropna().unique())

    for clave_matching, grupo in ultimos.groupby("clave_matching"):
        if grupo["supermercado"].nunique() < 2:
            continue

        grupo = grupo.sort_values("precio", ascending=True)
        mejor = grupo.iloc[0]
        mayor = grupo.iloc[-1]
        diferencia = mayor["precio"] - mejor["precio"]
        porcentaje = (diferencia / mayor["precio"]) * 100 if mayor["precio"] else 0
        coincidencia = (
            "Exacta" if grupo["nombre_normalizado"].nunique() == 1 else "Flexible"
        )
        fila = {
            "Producto comparable": mejor["etiqueta_matching"] or clave_matching,
            "Producto mejor precio": mejor["nombre_producto"],
            "Supermercado más barato": mejor["supermercado"],
            "Coincidencia": coincidencia,
            "Mejor precio": mejor["precio"],
            "Diferencia": diferencia,
            "Ahorro %": porcentaje,
            "Fecha": max(grupo["fecha_registro"].astype(str)),
        }

        for supermercado in supermercados:
            precios_supermercado = grupo[grupo["supermercado"] == supermercado]
            fila[supermercado] = (
                precios_supermercado.iloc[0]["precio"]
                if not precios_supermercado.empty
                else None
            )

        filas.append(fila)

    if not filas:
        return pd.DataFrame()

    return pd.DataFrame(filas).sort_values(
        ["Diferencia", "Mejor precio"],
        ascending=[False, True],
    )


def preparar_alertas_precios(precios, umbral_porcentaje=5):
    """Detecta cambios relevantes contra el precio anterior disponible."""
    if precios.empty:
        return pd.DataFrame()

    columnas_requeridas = {"supermercado", "nombre_producto", "precio", "fecha_registro"}
    if not columnas_requeridas.issubset(precios.columns):
        return pd.DataFrame()

    datos = precios.copy()
    if "nombre_normalizado" not in datos.columns:
        datos["nombre_normalizado"] = datos["nombre_producto"].apply(
            normalizar_nombre_comparable
        )
    if "clave_matching" not in datos.columns:
        datos["clave_matching"] = datos["nombre_producto"].apply(
            obtener_clave_matching_producto
        )

    datos["fecha"] = pd.to_datetime(datos["fecha_registro"], errors="coerce").dt.normalize()
    datos["precio"] = pd.to_numeric(datos["precio"], errors="coerce")
    datos = datos.dropna(subset=["fecha", "precio", "nombre_producto", "supermercado"])

    if datos.empty:
        return pd.DataFrame()

    diarios = (
        datos.groupby(["supermercado", "nombre_producto", "fecha"], as_index=False)
        .agg(
            precio=("precio", "mean"),
            fecha_registro=("fecha_registro", "max"),
            nombre_normalizado=("nombre_normalizado", "first"),
            clave_matching=("clave_matching", "first"),
        )
        .sort_values(["supermercado", "nombre_producto", "fecha"])
    )
    filas = []

    for (supermercado, producto), grupo in diarios.groupby(
        ["supermercado", "nombre_producto"]
    ):
        grupo = grupo.sort_values("fecha")

        if len(grupo) < 2:
            continue

        actual = grupo.iloc[-1]
        anterior = grupo.iloc[-2]

        if anterior["precio"] <= 0:
            continue

        variacion = actual["precio"] - anterior["precio"]
        variacion_porcentaje = (variacion / anterior["precio"]) * 100
        precio_minimo_historico = actual["precio"] <= grupo["precio"].min()
        alerta = None
        prioridad = 99

        if variacion < 0 and precio_minimo_historico:
            alerta = "Mínimo histórico"
            prioridad = 0
        elif variacion_porcentaje <= -umbral_porcentaje:
            alerta = "Bajó"
            prioridad = 1
        elif variacion_porcentaje >= umbral_porcentaje:
            alerta = "Subió"
            prioridad = 2

        if alerta is None:
            continue

        filas.append(
            {
                "Alerta": alerta,
                "Supermercado": supermercado,
                "Producto": producto,
                "Nombre normalizado": actual.get("nombre_normalizado", ""),
                "Clave matching": actual.get("clave_matching", ""),
                "Precio anterior": anterior["precio"],
                "Precio actual": actual["precio"],
                "Variación": variacion,
                "Variación %": variacion_porcentaje,
                "Fecha anterior": anterior["fecha"].date().isoformat(),
                "Fecha actual": actual["fecha"].date().isoformat(),
                "_prioridad": prioridad,
            }
        )

    if not filas:
        return pd.DataFrame()

    alertas = pd.DataFrame(filas)
    alertas["_variacion_abs"] = alertas["Variación %"].abs()
    alertas = alertas.sort_values(
        ["_prioridad", "_variacion_abs", "Producto"],
        ascending=[True, False, True],
    )
    return alertas.drop(columns=["_prioridad", "_variacion_abs"])


def formatear_variacion_guaranies(valor):
    """Formatea diferencias de precio con signo."""
    signo = "+" if valor > 0 else "-" if valor < 0 else ""
    return f"{signo}{formatear_guaranies(abs(valor))}"


def preparar_tabla_alertas(alertas):
    """Prepara alertas para mostrar o exportar."""
    if alertas.empty:
        return alertas.copy()

    tabla = alertas.copy()

    for columna in ["Precio anterior", "Precio actual"]:
        tabla[columna] = tabla[columna].map(formatear_guaranies)

    tabla["Variación"] = tabla["Variación"].map(formatear_variacion_guaranies)
    tabla["Variación %"] = tabla["Variación %"].map(lambda valor: f"{valor:+.1f}%")
    return tabla.fillna("")


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
    mapa_colores = dict(zip(dominio_colores, colores_supermercado))
    grafico = px.bar(
        datos_grafico,
        x="precio",
        y="producto_grafico",
        color="supermercado",
        orientation="h",
        text="precio_formateado",
        color_discrete_map=mapa_colores,
        hover_data={
            "nombre_producto": True,
            "supermercado": True,
            "precio_formateado": True,
            "fecha_registro": True,
            "precio": False,
            "producto_grafico": False,
        },
        template="plotly_white",
    )
    grafico.update_layout(
        height=altura,
        xaxis_title="Precio",
        yaxis_title=None,
        legend_title_text="Supermercado",
        margin=dict(l=12, r=96, t=12, b=12),
        yaxis=dict(
            categoryorder="total ascending",
        ),
    )
    aplicar_estilo_plotly_legible(grafico)
    grafico.update_traces(
        textposition="outside",
        textfont_color="#101828",
        textfont_size=12,
        cliponaxis=False,
        marker_line_width=0,
    )

    st.plotly_chart(
        grafico,
        width="stretch",
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


def mostrar_comparacion_supermercados(precios):
    """Muestra productos equivalentes encontrados entre supermercados."""
    mostrar_encabezado_seccion(
        "Comparación entre supermercados",
        "Detectamos productos equivalentes por nombre normalizado y mostramos dónde conviene comprar.",
        "Matching",
    )

    comparacion = preparar_comparacion_supermercados(precios)

    if comparacion.empty:
        st.info(
            "Todavía no hay coincidencias suficientes entre supermercados con estos filtros."
        )
        return

    tabla = comparacion.head(50).copy()
    columnas_precio = [
        columna
        for columna in tabla.columns
        if columna
        not in {
            "Producto comparable",
            "Producto mejor precio",
            "Supermercado más barato",
            "Coincidencia",
            "Ahorro %",
            "Fecha",
        }
    ]

    for columna in columnas_precio:
        tabla[columna] = tabla[columna].map(
            lambda valor: "" if pd.isna(valor) else formatear_guaranies(valor)
        )

    tabla["Ahorro %"] = tabla["Ahorro %"].map(lambda valor: f"{valor:.1f}%")
    st.dataframe(
        tabla,
        hide_index=True,
        width="stretch",
        height=360,
    )


def mostrar_exportaciones(precios):
    """Muestra descargas para los datos filtrados del dashboard."""
    mostrar_encabezado_seccion(
        "Exportar datos",
        "Descargá los resultados filtrados para analizarlos fuera del dashboard.",
        "CSV / Excel",
    )

    if precios.empty:
        st.info("No hay datos filtrados para exportar.")
        return

    productos = preparar_tabla(precios)
    comparacion = preparar_comparacion_supermercados(precios)
    alertas = preparar_tabla_alertas(preparar_alertas_precios(precios))
    historico = preparar_exportacion_historico(precios)
    hojas_excel = {
        "Productos filtrados": productos,
        "Comparacion": comparacion,
        "Alertas": alertas,
        "Historico": historico,
    }

    with st.container(border=True):
        st.caption(
            "El CSV descarga cada vista por separado. El Excel incluye productos, "
            "comparación e histórico en hojas distintas."
        )
        columnas = st.columns(5)
        columnas[0].download_button(
            "Productos CSV",
            data=convertir_a_csv(productos),
            file_name="preciospy_productos_filtrados.csv",
            mime="text/csv",
            use_container_width=True,
        )
        columnas[1].download_button(
            "Comparación CSV",
            data=convertir_a_csv(comparacion),
            file_name="preciospy_comparacion_supermercados.csv",
            mime="text/csv",
            disabled=comparacion.empty,
            use_container_width=True,
        )
        columnas[2].download_button(
            "Alertas CSV",
            data=convertir_a_csv(alertas),
            file_name="preciospy_alertas_precios.csv",
            mime="text/csv",
            disabled=alertas.empty,
            use_container_width=True,
        )
        columnas[3].download_button(
            "Histórico CSV",
            data=convertir_a_csv(historico),
            file_name="preciospy_historico_filtrado.csv",
            mime="text/csv",
            use_container_width=True,
        )
        columnas[4].download_button(
            "Excel completo",
            data=convertir_a_excel(hojas_excel),
            file_name="preciospy_exportacion.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
        )


def mostrar_alertas_precios(precios):
    """Muestra alertas de subidas, bajadas y minimos historicos."""
    mostrar_encabezado_seccion(
        "Alertas de cambios de precio",
        "Detectamos productos que cambiaron de forma relevante contra su registro anterior.",
        "Monitoreo",
    )

    alertas = preparar_alertas_precios(precios)

    if alertas.empty:
        st.info("No hay cambios relevantes de precio con los filtros actuales.")
        return

    cantidad_minimos = (alertas["Alerta"] == "Mínimo histórico").sum()
    cantidad_bajadas = alertas["Alerta"].isin(["Mínimo histórico", "Bajó"]).sum()
    cantidad_subidas = (alertas["Alerta"] == "Subió").sum()
    columnas = st.columns(3)
    columnas[0].metric("Bajadas detectadas", cantidad_bajadas)
    columnas[1].metric("Mínimos históricos", cantidad_minimos)
    columnas[2].metric("Subidas detectadas", cantidad_subidas)

    tabla = preparar_tabla_alertas(alertas.head(80))
    st.dataframe(
        tabla,
        hide_index=True,
        width="stretch",
        height=360,
    )


def preparar_opciones_evolucion(precios):
    """Prepara productos equivalentes disponibles para evolucion historica."""
    if precios.empty:
        return pd.DataFrame()

    datos = precios.copy()

    if "clave_matching" not in datos.columns:
        datos["clave_matching"] = datos["nombre_producto"].apply(
            obtener_clave_matching_producto
        )
    if "etiqueta_matching" not in datos.columns:
        datos["etiqueta_matching"] = datos["nombre_producto"].apply(
            obtener_etiqueta_matching_producto
        )

    datos = datos[datos["clave_matching"].fillna("").astype(str).str.len() > 0].copy()

    if datos.empty:
        return pd.DataFrame()

    opciones = (
        datos.groupby("clave_matching", as_index=False)
        .agg(
            producto=("etiqueta_matching", "first"),
            supermercados=("supermercado", "nunique"),
            fechas=("fecha_registro", "nunique"),
            registros=("precio", "size"),
        )
        .sort_values(["supermercados", "fechas", "producto"], ascending=[False, False, True])
    )
    opciones["label"] = opciones.apply(
        lambda fila: (
            f"{fila['producto']} · {int(fila['supermercados'])} supermercado(s) · "
            f"{int(fila['fechas'])} día(s)"
        ),
        axis=1,
    )
    return opciones


def preparar_evolucion_producto(precios, clave_matching):
    """Agrupa la evolucion de un producto equivalente por fecha y supermercado."""
    if precios.empty or not clave_matching:
        return pd.DataFrame()

    historial = precios.copy()

    if "clave_matching" not in historial.columns:
        historial["clave_matching"] = historial["nombre_producto"].apply(
            obtener_clave_matching_producto
        )

    historial = historial[historial["clave_matching"] == clave_matching].copy()
    historial["fecha"] = pd.to_datetime(
        historial["fecha_registro"],
        errors="coerce",
    ).dt.normalize()
    historial["precio"] = pd.to_numeric(historial["precio"], errors="coerce")
    historial = historial.dropna(subset=["fecha", "precio", "supermercado"])

    if historial.empty:
        return pd.DataFrame()

    agrupado = (
        historial.groupby(["fecha", "supermercado"], as_index=False)
        .agg(
            precio=("precio", "mean"),
            producto=("nombre_producto", "first"),
            registros=("precio", "size"),
        )
        .sort_values(["fecha", "supermercado"])
    )
    agrupado["precio_formateado"] = agrupado["precio"].map(formatear_guaranies)
    return agrupado


def filtrar_evolucion_supermercados(agrupado, supermercados):
    """Filtra la evolucion por supermercados seleccionados."""
    if agrupado.empty or not supermercados:
        return pd.DataFrame(columns=agrupado.columns)

    return agrupado[agrupado["supermercado"].isin(supermercados)].copy()


def preparar_resumen_evolucion(agrupado):
    """Prepara indicadores utiles por supermercado para la evolucion."""
    if agrupado.empty:
        return pd.DataFrame()

    filas = []

    for supermercado, grupo in agrupado.groupby("supermercado"):
        grupo = grupo.sort_values("fecha")
        primero = grupo.iloc[0]
        ultimo = grupo.iloc[-1]
        precio_inicial = primero["precio"]
        precio_final = ultimo["precio"]
        variacion = precio_final - precio_inicial
        variacion_porcentaje = (
            (variacion / precio_inicial) * 100 if precio_inicial else 0
        )

        filas.append(
            {
                "Supermercado": supermercado,
                "Último precio": formatear_guaranies(precio_final),
                "Precio mínimo": formatear_guaranies(grupo["precio"].min()),
                "Precio máximo": formatear_guaranies(grupo["precio"].max()),
                "Variación": formatear_variacion_guaranies(variacion),
                "Variación %": f"{variacion_porcentaje:+.1f}%",
                "Días": grupo["fecha"].nunique(),
                "Última fecha": ultimo["fecha"].date().isoformat(),
            }
        )

    return pd.DataFrame(filas).sort_values("Supermercado")


def obtener_configuracion_evolucion(agrupado, modo, seleccion):
    """Devuelve datos y bandera de comparacion para el grafico de evolucion."""
    supermercados = sorted(agrupado["supermercado"].dropna().unique())

    if modo == "Comparar supermercados":
        seleccionados = seleccion or supermercados
        return filtrar_evolucion_supermercados(agrupado, seleccionados), True

    seleccionado = seleccion or (supermercados[0] if supermercados else None)
    if not seleccionado:
        return pd.DataFrame(columns=agrupado.columns), False

    return filtrar_evolucion_supermercados(agrupado, [seleccionado]), False


def mostrar_evolucion_precios(precios):
    """Muestra la evolucion historica de un producto por supermercado."""
    mostrar_encabezado_seccion(
        "Evolución de precios",
        "Elegí un producto equivalente y compará cómo se movió su precio en el tiempo.",
        "Histórico",
    )

    if precios.empty:
        st.info("No encontramos productos con esos filtros.")
        return

    opciones = preparar_opciones_evolucion(precios)
    if opciones.empty:
        st.info("No hay productos disponibles para analizar.")
        return

    etiquetas = dict(zip(opciones["label"], opciones["clave_matching"]))
    with st.container(border=True):
        etiqueta_seleccionada = st.selectbox(
            "Producto equivalente para analizar",
            list(etiquetas.keys()),
            help=(
                "La evolución usa matching de productos, por eso puede unir nombres "
                "equivalentes entre supermercados."
            ),
        )
    clave_seleccionada = etiquetas[etiqueta_seleccionada]
    agrupado = preparar_evolucion_producto(precios, clave_seleccionada)

    if agrupado.empty or agrupado["fecha"].nunique() < 2:
        st.info("No hay suficientes datos históricos para mostrar una evolución.")
        return

    supermercados_disponibles = sorted(agrupado["supermercado"].dropna().unique())
    with st.container(border=True):
        columnas_control = st.columns([1.1, 1.4])
        modo_evolucion = columnas_control[0].radio(
            "Vista del gráfico",
            ["Ver un supermercado", "Comparar supermercados"],
            horizontal=True,
            key="modo_evolucion_precios",
        )

        if modo_evolucion == "Comparar supermercados":
            seleccion_supermercados = columnas_control[1].multiselect(
                "Supermercados a comparar",
                supermercados_disponibles,
                default=supermercados_disponibles,
                key="supermercados_evolucion_comparar",
            )
        else:
            seleccion_supermercados = columnas_control[1].selectbox(
                "Supermercado para ver",
                supermercados_disponibles,
                key="supermercado_evolucion_unico",
            )

    evolucion_filtrada, comparar = obtener_configuracion_evolucion(
        agrupado,
        modo_evolucion,
        seleccion_supermercados,
    )

    if evolucion_filtrada.empty:
        st.info("Seleccioná al menos un supermercado para mostrar la evolución.")
        return

    if evolucion_filtrada["fecha"].nunique() < 2:
        st.info("La selección actual no tiene suficientes fechas para graficar.")
        return

    altura_grafico = 430 if comparar else 380
    dominio_colores, colores_supermercado = obtener_colores_supermercados(
        evolucion_filtrada["supermercado"].dropna().unique()
    )
    mapa_colores = dict(zip(dominio_colores, colores_supermercado))
    opciones_grafico = {
        "data_frame": evolucion_filtrada,
        "x": "fecha",
        "y": "precio",
        "color": "supermercado",
        "color_discrete_map": mapa_colores,
        "markers": True,
        "hover_data": {
            "producto": True,
            "precio_formateado": True,
            "registros": True,
            "fecha": "|%Y-%m-%d",
            "precio": False,
        },
        "template": "plotly_white",
        "height": altura_grafico,
    }

    if comparar:
        opciones_grafico.update(
            {
                "line_dash": "supermercado",
                "symbol": "supermercado",
            }
        )

    grafico = px.line(
        **opciones_grafico,
    )
    grafico.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Precio",
        legend_title_text="Supermercado",
        margin=dict(l=12, r=24, t=12, b=12),
        title=None,
        showlegend=comparar,
        hovermode="x unified" if comparar else "closest",
    )
    aplicar_estilo_plotly_legible(grafico)
    grafico.update_traces(
        line=dict(width=3),
        marker=dict(size=9, line=dict(color="#FFFFFF", width=1.5)),
    )

    with st.container(border=True):
        st.plotly_chart(grafico, width="stretch")
        tabla_resumen = preparar_resumen_evolucion(evolucion_filtrada)
        if not tabla_resumen.empty:
            st.dataframe(
                tabla_resumen,
                hide_index=True,
                width="stretch",
                height=min(260, 86 + len(tabla_resumen) * 36),
            )


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

    precios, fuente = cargar_precios_con_fuente()

    if precios.empty:
        st.info("Todavía no hay productos guardados en la base de datos.")
        return

    mostrar_metricas(precios)
    mostrar_salud_sistema(precios, fuente)
    filtros = mostrar_filtros(precios)
    precios_filtrados = filtrar_precios(precios, *filtros)
    mostrar_resumen_filtros(precios_filtrados, len(precios), filtros)

    mostrar_grafico(precios_filtrados)
    mostrar_comparacion_supermercados(precios_filtrados)
    mostrar_evolucion_precios(precios_filtrados)
    mostrar_tabla(precios_filtrados)
    mostrar_alertas_precios(precios_filtrados)
    mostrar_exportaciones(precios_filtrados)
    mostrar_logs_scraper()


if __name__ == "__main__":
    mostrar_dashboard()
