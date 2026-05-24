import sqlite3

import dashboard
from dashboard import (
    PERIODO_CARGA_DEFAULT,
    cargar_resumen_datos_sqlite,
    cargar_ultimos_precios_sqlite,
    cargar_precios_sqlite,
    obtener_fecha_desde_periodo,
)


def crear_db_dashboard(ruta_db):
    with sqlite3.connect(ruta_db) as conexion:
        conexion.execute(
            """
            CREATE TABLE precios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supermercado TEXT NOT NULL,
                nombre_producto TEXT NOT NULL,
                precio REAL NOT NULL,
                unidad TEXT,
                fecha_registro TEXT NOT NULL,
                categoria TEXT,
                url_producto TEXT,
                moneda TEXT DEFAULT 'PYG',
                fecha_hora_registro TEXT
            )
            """
        )
        conexion.executemany(
            """
            INSERT INTO precios (
                supermercado,
                nombre_producto,
                precio,
                unidad,
                fecha_registro,
                moneda,
                fecha_hora_registro
            )
            VALUES (?, ?, ?, 'unidad', ?, 'PYG', ?)
            """,
            [
                ("Stock", "Arroz 1kg", 7000, "2026-05-01", "2026-05-01T08:00:00"),
                ("Stock", "Arroz 1kg", 7200, "2026-05-11", "2026-05-11T08:00:00"),
                ("Stock", "Arroz 1kg", 7300, "2026-05-24", "2026-05-24T08:00:00"),
            ],
        )
        conexion.commit()


def test_obtener_fecha_desde_periodo_usa_fecha_maxima_de_la_base():
    assert obtener_fecha_desde_periodo("Últimos 10 días", "2026-05-24") == "2026-05-15"
    assert obtener_fecha_desde_periodo("Últimos 14 días", "2026-05-24") == "2026-05-11"
    assert obtener_fecha_desde_periodo("Todo el histórico", "2026-05-24") is None


def test_cargar_precios_sqlite_limita_por_defecto(monkeypatch, tmp_path):
    ruta_db = tmp_path / "precios.db"
    crear_db_dashboard(ruta_db)
    monkeypatch.setattr(dashboard, "RUTA_DB", ruta_db)

    precios = cargar_precios_sqlite(PERIODO_CARGA_DEFAULT)

    assert list(precios["fecha_registro"]) == [
        "2026-05-24",
        "2026-05-11",
        "2026-05-01",
    ]


def test_cargar_precios_sqlite_permite_todo_el_historico(monkeypatch, tmp_path):
    ruta_db = tmp_path / "precios.db"
    crear_db_dashboard(ruta_db)
    monkeypatch.setattr(dashboard, "RUTA_DB", ruta_db)

    precios = cargar_precios_sqlite("Todo el histórico")

    assert list(precios["fecha_registro"]) == [
        "2026-05-24",
        "2026-05-11",
        "2026-05-01",
    ]


def test_cargar_ultimos_precios_sqlite_usa_tabla_materializada(monkeypatch, tmp_path):
    ruta_db = tmp_path / "precios.db"
    crear_db_dashboard(ruta_db)
    monkeypatch.setattr(dashboard, "RUTA_DB", ruta_db)

    actuales = cargar_ultimos_precios_sqlite()

    assert len(actuales) == 1
    assert actuales.iloc[0]["nombre_producto"] == "Arroz 1kg"
    assert actuales.iloc[0]["precio"] == 7300
    assert actuales.iloc[0]["fecha_registro"] == "2026-05-24"


def test_cargar_resumen_datos_sqlite_retorna_metricas_y_tablas(monkeypatch, tmp_path):
    ruta_db = tmp_path / "precios.db"
    crear_db_dashboard(ruta_db)
    monkeypatch.setattr(dashboard, "RUTA_DB", ruta_db)
    dashboard.preparar_sqlite_para_consultas(ruta_db)
    dashboard.guardar_corridas_scraper(
        [
            {
                "archivo": "scraper-2026-05-24_09-11-33.log",
                "fecha": "2026-05-24",
                "estado": "OK (0)",
                "ok": True,
                "scrapeados": 3,
                "sqlite": 3,
                "supabase": 3,
            }
        ],
        ruta_db,
    )

    resumen, por_supermercado, corridas = cargar_resumen_datos_sqlite()

    assert resumen["registros"] == 3
    assert resumen["productos_actuales"] == 1
    assert resumen["dias"] == 3
    assert resumen["primera_fecha"] == "2026-05-01"
    assert resumen["ultima_fecha"] == "2026-05-24"
    assert resumen["corridas"] == 1
    assert por_supermercado.iloc[0]["Productos_actuales"] == 1
    assert corridas.iloc[0]["Estado"] == "OK (0)"
