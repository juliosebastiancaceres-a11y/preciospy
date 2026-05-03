import sqlite3
from pathlib import Path


RUTA_DB = Path(__file__).resolve().parent.parent / "data" / "preciospy.db"


def inicializar_db():
    """Crea la base de datos y la tabla de precios si no existen."""
    RUTA_DB.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(RUTA_DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS precios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supermercado TEXT NOT NULL,
                nombre_producto TEXT NOT NULL,
                precio REAL NOT NULL,
                unidad TEXT,
                fecha_registro TEXT NOT NULL
            )
            """
        )
        conexion.commit()


def guardar_productos(productos):
    """Guarda una lista de productos en la tabla de precios."""
    with sqlite3.connect(RUTA_DB) as conexion:
        cursor = conexion.cursor()
        cursor.executemany(
            """
            INSERT INTO precios (
                supermercado,
                nombre_producto,
                precio,
                unidad,
                fecha_registro
            )
            VALUES (
                :supermercado,
                :nombre_producto,
                :precio,
                :unidad,
                :fecha_registro
            )
            """,
            productos,
        )
        conexion.commit()

    print(f"Productos guardados: {len(productos)}")
