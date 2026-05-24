import sqlite3

from database import (
    contar_duplicados_sqlite,
    deduplicar_precios_sqlite,
    guardar_corridas_scraper,
    preparar_sqlite_para_consultas,
)


def crear_db_con_precios(ruta_db):
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
        conexion.commit()


def insertar_precio(
    ruta_db,
    precio,
    fecha_hora_registro,
    supermercado="Stock",
    nombre_producto="Aceite 900ml",
    fecha_registro="2026-05-08",
):
    with sqlite3.connect(ruta_db) as conexion:
        conexion.execute(
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
            (
                supermercado,
                nombre_producto,
                precio,
                fecha_registro,
                fecha_hora_registro,
            ),
        )
        conexion.commit()


def obtener_precios(ruta_db):
    with sqlite3.connect(ruta_db) as conexion:
        return conexion.execute(
            "SELECT precio FROM precios ORDER BY id"
        ).fetchall()


def test_contar_duplicados_sqlite_cuenta_grupos_y_filas_sobrantes(tmp_path):
    ruta_db = tmp_path / "precios.db"
    crear_db_con_precios(ruta_db)
    insertar_precio(ruta_db, 10000, "2026-05-08T10:00:00")
    insertar_precio(ruta_db, 11000, "2026-05-08T11:00:00")
    insertar_precio(
        ruta_db,
        12000,
        "2026-05-08T12:00:00",
        nombre_producto="Arroz 1kg",
    )

    duplicados = contar_duplicados_sqlite(ruta_db)

    assert duplicados == {"grupos": 1, "filas_sobrantes": 1}


def test_deduplicar_precios_sqlite_conserva_registro_mas_reciente(tmp_path):
    ruta_db = tmp_path / "precios.db"
    crear_db_con_precios(ruta_db)
    insertar_precio(ruta_db, 10000, "2026-05-08T10:00:00")
    insertar_precio(ruta_db, 12000, "2026-05-08T12:00:00")
    insertar_precio(ruta_db, 11000, "2026-05-08T11:00:00")

    eliminados = deduplicar_precios_sqlite(ruta_db)

    assert eliminados == 2
    assert obtener_precios(ruta_db) == [(12000.0,)]
    assert contar_duplicados_sqlite(ruta_db)["filas_sobrantes"] == 0


def test_deduplicar_precios_sqlite_no_elimina_claves_unicas(tmp_path):
    ruta_db = tmp_path / "precios.db"
    crear_db_con_precios(ruta_db)
    insertar_precio(ruta_db, 10000, "2026-05-08T10:00:00")
    insertar_precio(
        ruta_db,
        11000,
        "2026-05-08T10:00:00",
        nombre_producto="Arroz 1kg",
    )

    eliminados = deduplicar_precios_sqlite(ruta_db)

    assert eliminados == 0
    assert obtener_precios(ruta_db) == [(10000.0,), (11000.0,)]


def test_preparar_sqlite_para_consultas_crea_indices_y_ultimos_precios(tmp_path):
    ruta_db = tmp_path / "precios.db"
    crear_db_con_precios(ruta_db)
    insertar_precio(ruta_db, 10000, "2026-05-08T10:00:00")
    insertar_precio(
        ruta_db,
        12000,
        "2026-05-09T10:00:00",
        fecha_registro="2026-05-09",
    )
    insertar_precio(
        ruta_db,
        8000,
        "2026-05-08T10:00:00",
        supermercado="Superseis",
        nombre_producto="Arroz 1kg",
    )

    assert preparar_sqlite_para_consultas(ruta_db) is True

    with sqlite3.connect(ruta_db) as conexion:
        indices = {
            fila[0]
            for fila in conexion.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'index'
                """
            )
        }
        ultimos = conexion.execute(
            """
            SELECT supermercado, nombre_producto, precio, fecha_registro
            FROM precios_ultimos
            ORDER BY supermercado, nombre_producto
            """
        ).fetchall()

    assert {
        "idx_precios_fecha_registro",
        "idx_precios_supermercado",
        "idx_precios_nombre_producto",
        "idx_precios_supermercado_fecha",
    }.issubset(indices)
    assert ultimos == [
        ("Stock", "Aceite 900ml", 12000.0, "2026-05-09"),
        ("Superseis", "Arroz 1kg", 8000.0, "2026-05-08"),
    ]


def test_guardar_corridas_scraper_persiste_resumen_operativo(tmp_path):
    ruta_db = tmp_path / "precios.db"
    crear_db_con_precios(ruta_db)
    preparar_sqlite_para_consultas(ruta_db)

    guardados = guardar_corridas_scraper(
        [
            {
                "archivo": "scraper-2026-05-24_09-11-33.log",
                "fecha": "2026-05-24",
                "inicio": "2026-05-24 09:11:33",
                "fin": "2026-05-24 09:46:23",
                "estado": "OK (0)",
                "ok": True,
                "scrapeados": 33780,
                "sqlite": 33780,
                "supabase": 33780,
                "errores": 0,
                "advertencias": 1,
                "ultimo_error": "Sin errores críticos (1 aviso recuperado)",
            }
        ],
        ruta_db,
    )

    with sqlite3.connect(ruta_db) as conexion:
        fila = conexion.execute(
            """
            SELECT archivo, fecha, ok, scrapeados, sqlite_guardados, advertencias
            FROM corridas_scraper
            """
        ).fetchone()

    assert guardados == 1
    assert fila == (
        "scraper-2026-05-24_09-11-33.log",
        "2026-05-24",
        1,
        33780,
        33780,
        1,
    )
