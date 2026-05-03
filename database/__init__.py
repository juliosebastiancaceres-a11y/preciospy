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
    """Guarda productos nuevos en la tabla de precios."""
    productos_guardados = 0

    with sqlite3.connect(RUTA_DB) as conexion:
        cursor = conexion.cursor()

        for producto in productos:
            # Verifica si el producto ya fue registrado para ese supermercado y fecha.
            cursor.execute(
                """
                SELECT id
                FROM precios
                WHERE nombre_producto = :nombre_producto
                  AND supermercado = :supermercado
                  AND fecha_registro = :fecha_registro
                """,
                producto,
            )

            if cursor.fetchone():
                continue

            cursor.execute(
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
                producto,
            )
            productos_guardados += 1

        conexion.commit()

    print(f"Productos guardados: {productos_guardados}")
