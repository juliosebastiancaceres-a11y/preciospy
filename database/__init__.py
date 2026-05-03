import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client


RUTA_DB = Path(__file__).resolve().parent.parent / "data" / "preciospy.db"
RUTA_ENV = Path(__file__).resolve().parent.parent / ".env"


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


def inicializar_supabase():
    """Crea y retorna el cliente de Supabase usando variables del archivo .env."""
    load_dotenv(RUTA_ENV)

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Faltan SUPABASE_URL o SUPABASE_KEY en el archivo .env")

    return create_client(url, key)


def guardar_en_supabase(productos):
    """Guarda productos nuevos en la tabla precios de Supabase."""
    supabase = inicializar_supabase()
    productos_guardados = 0

    for producto in productos:
        # Verifica si el producto ya existe para esa fecha antes de insertarlo.
        respuesta = (
            supabase.table("precios")
            .select("id")
            .eq("nombre_producto", producto["nombre_producto"])
            .eq("fecha_registro", producto["fecha_registro"])
            .execute()
        )

        if respuesta.data:
            continue

        supabase.table("precios").insert(producto).execute()
        productos_guardados += 1

    print(f"Productos guardados en Supabase: {productos_guardados}")
