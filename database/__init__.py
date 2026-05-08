import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client
from supabase.client import ClientOptions


RUTA_DB = Path(__file__).resolve().parent.parent / "data" / "preciospy.db"
RUTA_ENV = Path(__file__).resolve().parent.parent / ".env"
TIMEOUT_SUPABASE = 30
TAMANO_LOTE_SUPABASE = 100
PAUSA_ENTRE_LOTES = 0.25
CLAVE_UNICA = ("supermercado", "nombre_producto", "fecha_registro")
COLUMNAS_BASE = (
    "supermercado",
    "nombre_producto",
    "precio",
    "unidad",
    "fecha_registro",
)
COLUMNAS_EXTRA = (
    "categoria",
    "url_producto",
    "moneda",
    "fecha_hora_registro",
)


def inicializar_db():
    """Crea o actualiza la base SQLite sin borrar datos existentes."""
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
                fecha_registro TEXT NOT NULL,
                categoria TEXT,
                url_producto TEXT,
                moneda TEXT DEFAULT 'PYG',
                fecha_hora_registro TEXT,
                UNIQUE(supermercado, nombre_producto, fecha_registro)
            )
            """
        )
        _agregar_columnas_faltantes(cursor)
        _asegurar_control_de_duplicados(cursor)
        conexion.commit()


def _agregar_columnas_faltantes(cursor):
    """Agrega columnas nuevas a bases SQLite creadas por versiones anteriores."""
    columnas = {fila[1] for fila in cursor.execute("PRAGMA table_info(precios)")}
    columnas_faltantes = {
        "categoria": "TEXT",
        "url_producto": "TEXT",
        "moneda": "TEXT DEFAULT 'PYG'",
        "fecha_hora_registro": "TEXT",
    }

    for columna, definicion in columnas_faltantes.items():
        if columna not in columnas:
            cursor.execute(f"ALTER TABLE precios ADD COLUMN {columna} {definicion}")


def _asegurar_control_de_duplicados(cursor):
    """Protege nuevas inserciones aunque una base vieja ya tenga duplicados."""
    try:
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_precios_unico_producto_fecha
            ON precios (supermercado, nombre_producto, fecha_registro)
            """
        )
    except sqlite3.IntegrityError:
        print(
            "Aviso: la base local ya contiene duplicados historicos; "
            "no se borraron datos. Se instala un trigger para evitar "
            "nuevos duplicados."
        )

    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS trg_precios_evitar_duplicados
        BEFORE INSERT ON precios
        WHEN EXISTS (
            SELECT 1
            FROM precios
            WHERE supermercado = NEW.supermercado
              AND nombre_producto = NEW.nombre_producto
              AND fecha_registro = NEW.fecha_registro
        )
        BEGIN
            SELECT RAISE(IGNORE);
        END;
        """
    )


def preparar_producto(producto):
    """Normaliza un producto antes de persistirlo."""
    nombre = str(producto.get("nombre_producto") or "").strip()
    supermercado = str(producto.get("supermercado") or "").strip()
    fecha_registro = str(
        producto.get("fecha_registro") or datetime.today().strftime("%Y-%m-%d")
    ).strip()

    if not nombre or not supermercado or not fecha_registro:
        return None

    try:
        precio = float(producto.get("precio"))
    except (TypeError, ValueError):
        return None

    if precio <= 0:
        return None

    if precio.is_integer():
        precio = int(precio)

    return {
        "supermercado": supermercado,
        "nombre_producto": nombre,
        "precio": precio,
        "unidad": producto.get("unidad") or "unidad",
        "fecha_registro": fecha_registro,
        "categoria": producto.get("categoria"),
        "url_producto": producto.get("url_producto"),
        "moneda": producto.get("moneda") or "PYG",
        "fecha_hora_registro": producto.get("fecha_hora_registro")
        or datetime.now().isoformat(timespec="seconds"),
    }


def preparar_productos(productos):
    """Filtra productos incompletos o con precio invalido."""
    productos_limpios = []
    omitidos = 0

    for producto in productos:
        producto_limpio = preparar_producto(producto)
        if producto_limpio is None:
            omitidos += 1
            continue
        productos_limpios.append(producto_limpio)

    if omitidos:
        print(f"Productos omitidos por datos invalidos: {omitidos}")

    return productos_limpios


def guardar_productos(productos):
    """Guarda productos en SQLite usando la restriccion de duplicados."""
    inicializar_db()
    productos_limpios = preparar_productos(productos)

    if not productos_limpios:
        print("No hay productos validos para guardar en SQLite.")
        return 0

    with sqlite3.connect(RUTA_DB) as conexion:
        cambios_antes = conexion.total_changes
        cursor = conexion.cursor()
        cursor.executemany(
            """
            INSERT OR IGNORE INTO precios (
                supermercado,
                nombre_producto,
                precio,
                unidad,
                fecha_registro,
                categoria,
                url_producto,
                moneda,
                fecha_hora_registro
            )
            VALUES (
                :supermercado,
                :nombre_producto,
                :precio,
                :unidad,
                :fecha_registro,
                :categoria,
                :url_producto,
                :moneda,
                :fecha_hora_registro
            )
            """,
            productos_limpios,
        )
        conexion.commit()
        productos_guardados = conexion.total_changes - cambios_antes

    print(f"Productos guardados en SQLite: {productos_guardados}")
    return productos_guardados


def inicializar_supabase():
    """Crea el cliente de Supabase si las variables requeridas existen."""
    load_dotenv(RUTA_ENV)

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print(
            "Supabase no configurado: faltan SUPABASE_URL o SUPABASE_KEY. "
            "Se omite la sincronizacion remota."
        )
        return None

    try:
        opciones = ClientOptions(postgrest_client_timeout=TIMEOUT_SUPABASE)
        return create_client(url, key, options=opciones)
    except Exception as error:
        print(f"No se pudo inicializar Supabase: {error.__class__.__name__}")
        return None


def dividir_en_lotes(productos, tamano_lote):
    """Divide una lista de productos en lotes mas pequenos."""
    for inicio in range(0, len(productos), tamano_lote):
        yield productos[inicio : inicio + tamano_lote]


def _solo_columnas_base(producto):
    return {columna: producto.get(columna) for columna in COLUMNAS_BASE}


def guardar_en_supabase(productos):
    """Sincroniza productos con Supabase mediante upsert por clave natural."""
    supabase = inicializar_supabase()
    if supabase is None:
        return 0

    productos_limpios = preparar_productos(productos)
    if not productos_limpios:
        print("No hay productos validos para enviar a Supabase.")
        return 0

    productos_guardados = 0
    conflicto = ",".join(CLAVE_UNICA)

    for lote in dividir_en_lotes(productos_limpios, TAMANO_LOTE_SUPABASE):
        try:
            supabase.table("precios").upsert(
                lote,
                on_conflict=conflicto,
            ).execute()
            productos_guardados += len(lote)
        except Exception as error:
            print(
                "Error al hacer upsert en Supabase con columnas extendidas. "
                "Se reintenta con columnas base."
            )
            try:
                lote_base = [_solo_columnas_base(producto) for producto in lote]
                supabase.table("precios").upsert(
                    lote_base,
                    on_conflict=conflicto,
                ).execute()
                productos_guardados += len(lote_base)
            except Exception as error_base:
                print(
                    "Error al sincronizar lote en Supabase: "
                    f"{error_base.__class__.__name__}"
                )
        finally:
            time.sleep(PAUSA_ENTRE_LOTES)

    print(f"Productos sincronizados con Supabase: {productos_guardados}")
    return productos_guardados
