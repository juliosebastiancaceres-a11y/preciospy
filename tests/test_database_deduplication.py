import sqlite3

from database import contar_duplicados_sqlite, deduplicar_precios_sqlite


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
