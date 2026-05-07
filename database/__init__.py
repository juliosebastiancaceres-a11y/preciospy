import os
import sqlite3
import time
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client
from supabase.client import ClientOptions


RUTA_DB = Path(__file__).resolve().parent.parent / "data" / "preciospy.db"
RUTA_ENV = Path(__file__).resolve().parent.parent / ".env"
TIMEOUT_SUPABASE = 30
TAMANO_LOTE_SUPABASE = 20
PAUSA_ENTRE_LOTES = 0.5


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

    opciones = ClientOptions(postgrest_client_timeout=TIMEOUT_SUPABASE)
    return create_client(url, key, options=opciones)


def dividir_en_lotes(productos, tamano_lote):
    """Divide una lista de productos en lotes más pequeños."""
    for inicio in range(0, len(productos), tamano_lote):
        yield productos[inicio : inicio + tamano_lote]


def guardar_en_supabase(productos):
    """Guarda productos nuevos en la tabla precios de Supabase."""
    supabase = inicializar_supabase()
    productos_nuevos = []
    productos_guardados = 0

    for producto in productos:
        # Verifica si el producto ya existe para esa fecha antes de insertarlo.
        respuesta = (
            supabase.table("precios")
            .select("id")
            .eq("nombre_producto", producto["nombre_producto"])
            .eq("supermercado", producto["supermercado"])
            .eq("fecha_registro", producto["fecha_registro"])
            .execute()
        )

        if respuesta.data:
            continue

        productos_nuevos.append(producto)

    for lote in dividir_en_lotes(productos_nuevos, TAMANO_LOTE_SUPABASE):
        try:
            # Inserta en lotes chicos para no saturar la conexión a Supabase.
            supabase.table("precios").insert(lote).execute()
            productos_guardados += len(lote)
        except Exception as error:
            print(f"Error al insertar lote en Supabase: {error}")
        finally:
            # Pausa breve entre lotes para evitar demasiadas requests seguidas.
            time.sleep(PAUSA_ENTRE_LOTES)

    print(f"Productos guardados en Supabase: {productos_guardados}")
