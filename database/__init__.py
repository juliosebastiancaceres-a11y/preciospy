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
        _crear_indices_consulta(cursor)
        _actualizar_tabla_ultimos_precios(cursor)
        _crear_tabla_corridas_scraper(cursor)
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


def _crear_indices_consulta(cursor):
    """Crea indices usados por dashboard, filtros y reportes historicos."""
    indices = [
        (
            "idx_precios_fecha_registro",
            "fecha_registro",
        ),
        (
            "idx_precios_supermercado",
            "supermercado",
        ),
        (
            "idx_precios_nombre_producto",
            "nombre_producto",
        ),
        (
            "idx_precios_supermercado_fecha",
            "supermercado, fecha_registro",
        ),
    ]

    for nombre, columnas in indices:
        cursor.execute(
            f"""
            CREATE INDEX IF NOT EXISTS {nombre}
            ON precios ({columnas})
            """
        )


def _actualizar_tabla_ultimos_precios(cursor):
    """Materializa el ultimo precio por producto y supermercado."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS precios_ultimos (
            supermercado TEXT NOT NULL,
            nombre_producto TEXT NOT NULL,
            precio REAL NOT NULL,
            unidad TEXT,
            fecha_registro TEXT NOT NULL,
            categoria TEXT,
            url_producto TEXT,
            moneda TEXT DEFAULT 'PYG',
            fecha_hora_registro TEXT,
            precio_id INTEGER,
            PRIMARY KEY (supermercado, nombre_producto)
        )
        """
    )
    cursor.execute("DELETE FROM precios_ultimos")
    cursor.execute(
        """
        INSERT INTO precios_ultimos (
            supermercado,
            nombre_producto,
            precio,
            unidad,
            fecha_registro,
            categoria,
            url_producto,
            moneda,
            fecha_hora_registro,
            precio_id
        )
        SELECT
            supermercado,
            nombre_producto,
            precio,
            unidad,
            fecha_registro,
            categoria,
            url_producto,
            COALESCE(NULLIF(moneda, ''), 'PYG'),
            fecha_hora_registro,
            id
        FROM (
            SELECT
                precios.*,
                ROW_NUMBER() OVER (
                    PARTITION BY supermercado, nombre_producto
                    ORDER BY
                        date(fecha_registro) DESC,
                        CASE
                            WHEN fecha_hora_registro IS NULL
                              OR fecha_hora_registro = ''
                            THEN 1
                            ELSE 0
                        END,
                        datetime(fecha_hora_registro) DESC,
                        fecha_hora_registro DESC,
                        id DESC
                ) AS orden
            FROM precios
        )
        WHERE orden = 1
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_precios_ultimos_supermercado
        ON precios_ultimos (supermercado)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_precios_ultimos_fecha
        ON precios_ultimos (fecha_registro)
        """
    )


def _crear_tabla_corridas_scraper(cursor):
    """Crea una tabla operativa para consultar corridas sin parsear logs siempre."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS corridas_scraper (
            archivo TEXT PRIMARY KEY,
            fecha TEXT,
            inicio TEXT,
            fin TEXT,
            estado TEXT,
            ok INTEGER NOT NULL DEFAULT 0,
            scrapeados INTEGER NOT NULL DEFAULT 0,
            sqlite_guardados INTEGER NOT NULL DEFAULT 0,
            supabase_sincronizados INTEGER NOT NULL DEFAULT 0,
            errores INTEGER NOT NULL DEFAULT 0,
            advertencias INTEGER NOT NULL DEFAULT 0,
            ultimo_error TEXT,
            actualizado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_corridas_scraper_fecha
        ON corridas_scraper (fecha)
        """
    )


def preparar_sqlite_para_consultas(ruta_db=RUTA_DB):
    """Asegura estructuras auxiliares para consultar una base existente."""
    ruta = Path(ruta_db)

    if not ruta.exists():
        return False

    with sqlite3.connect(ruta) as conexion:
        cursor = conexion.cursor()
        _agregar_columnas_faltantes(cursor)
        _asegurar_control_de_duplicados(cursor)
        _crear_indices_consulta(cursor)
        _actualizar_tabla_ultimos_precios(cursor)
        _crear_tabla_corridas_scraper(cursor)
        conexion.commit()

    return True


def guardar_corridas_scraper(registros, ruta_db=RUTA_DB):
    """Guarda resumenes de logs del scraper para monitoreo historico."""
    ruta = Path(ruta_db)

    if not ruta.exists():
        return 0

    filas = []
    actualizado_en = datetime.now().isoformat(timespec="seconds")

    for registro in registros:
        archivo = str(registro.get("archivo") or "").strip()
        if not archivo:
            continue

        filas.append(
            {
                "archivo": archivo,
                "fecha": registro.get("fecha") or "",
                "inicio": registro.get("inicio") or "",
                "fin": registro.get("fin") or "",
                "estado": registro.get("estado") or "",
                "ok": 1 if registro.get("ok") else 0,
                "scrapeados": int(registro.get("scrapeados") or 0),
                "sqlite_guardados": int(registro.get("sqlite") or 0),
                "supabase_sincronizados": int(registro.get("supabase") or 0),
                "errores": int(registro.get("errores") or 0),
                "advertencias": int(registro.get("advertencias") or 0),
                "ultimo_error": registro.get("ultimo_error") or "",
                "actualizado_en": actualizado_en,
            }
        )

    if not filas:
        return 0

    with sqlite3.connect(ruta) as conexion:
        cursor = conexion.cursor()
        _crear_tabla_corridas_scraper(cursor)
        cursor.executemany(
            """
            INSERT INTO corridas_scraper (
                archivo,
                fecha,
                inicio,
                fin,
                estado,
                ok,
                scrapeados,
                sqlite_guardados,
                supabase_sincronizados,
                errores,
                advertencias,
                ultimo_error,
                actualizado_en
            )
            VALUES (
                :archivo,
                :fecha,
                :inicio,
                :fin,
                :estado,
                :ok,
                :scrapeados,
                :sqlite_guardados,
                :supabase_sincronizados,
                :errores,
                :advertencias,
                :ultimo_error,
                :actualizado_en
            )
            ON CONFLICT(archivo) DO UPDATE SET
                fecha = excluded.fecha,
                inicio = excluded.inicio,
                fin = excluded.fin,
                estado = excluded.estado,
                ok = excluded.ok,
                scrapeados = excluded.scrapeados,
                sqlite_guardados = excluded.sqlite_guardados,
                supabase_sincronizados = excluded.supabase_sincronizados,
                errores = excluded.errores,
                advertencias = excluded.advertencias,
                ultimo_error = excluded.ultimo_error,
                actualizado_en = excluded.actualizado_en
            """,
            filas,
        )
        conexion.commit()

    return len(filas)


def contar_duplicados_sqlite(ruta_db=RUTA_DB):
    """Cuenta grupos duplicados y filas sobrantes en la tabla de precios."""
    ruta = Path(ruta_db)

    if not ruta.exists():
        return {"grupos": 0, "filas_sobrantes": 0}

    with sqlite3.connect(ruta) as conexion:
        grupos = conexion.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT supermercado, nombre_producto, fecha_registro, COUNT(*) AS total
                FROM precios
                GROUP BY supermercado, nombre_producto, fecha_registro
                HAVING total > 1
            )
            """
        ).fetchone()[0]
        filas_sobrantes = conexion.execute(
            """
            SELECT COALESCE(SUM(total - 1), 0)
            FROM (
                SELECT COUNT(*) AS total
                FROM precios
                GROUP BY supermercado, nombre_producto, fecha_registro
                HAVING total > 1
            )
            """
        ).fetchone()[0]

    return {"grupos": int(grupos), "filas_sobrantes": int(filas_sobrantes)}


def deduplicar_precios_sqlite(ruta_db=RUTA_DB):
    """
    Elimina duplicados historicos conservando el registro mas reciente.

    La clave natural es supermercado, producto y fecha. Si hay varias filas para
    esa clave, se conserva la de fecha_hora_registro mas nueva y se usa id como
    desempate estable.
    """
    ruta = Path(ruta_db)

    if not ruta.exists():
        raise FileNotFoundError(f"No existe la base SQLite: {ruta}")

    duplicados_antes = contar_duplicados_sqlite(ruta)

    if duplicados_antes["filas_sobrantes"] == 0:
        return 0

    with sqlite3.connect(ruta) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            WITH ranking AS (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY supermercado, nombre_producto, fecha_registro
                        ORDER BY
                            CASE
                                WHEN fecha_hora_registro IS NULL
                                  OR fecha_hora_registro = ''
                                THEN 1
                                ELSE 0
                            END,
                            datetime(fecha_hora_registro) DESC,
                            fecha_hora_registro DESC,
                            id DESC
                    ) AS orden
                FROM precios
            )
            DELETE FROM precios
            WHERE id IN (
                SELECT id
                FROM ranking
                WHERE orden > 1
            )
            """
        )
        eliminados = cursor.rowcount
        _asegurar_control_de_duplicados(cursor)
        conexion.commit()

    return eliminados if eliminados != -1 else duplicados_antes["filas_sobrantes"]


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


def clave_natural_producto(producto):
    """Retorna la clave natural usada para evitar duplicados."""
    return tuple(str(producto.get(columna) or "").strip() for columna in CLAVE_UNICA)


def deduplicar_productos_por_clave(productos):
    """Quita duplicados en memoria antes de hacer upsert por clave natural."""
    productos_por_clave = {}

    for producto in productos:
        clave = clave_natural_producto(producto)

        if not all(clave):
            continue

        productos_por_clave[clave] = producto

    duplicados = len(productos) - len(productos_por_clave)
    if duplicados:
        print(f"Productos duplicados omitidos antes de Supabase: {duplicados}")

    return list(productos_por_clave.values())


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
        productos_guardados = conexion.total_changes - cambios_antes
        _actualizar_tabla_ultimos_precios(cursor)
        conexion.commit()

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

    productos_limpios = deduplicar_productos_por_clave(preparar_productos(productos))
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
                "Se reintenta con columnas base. "
                f"Detalle: {error.__class__.__name__}: {error}"
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
                    f"{error_base.__class__.__name__}: {error_base}"
                )
        finally:
            time.sleep(PAUSA_ENTRE_LOTES)

    print(f"Productos sincronizados con Supabase: {productos_guardados}")
    return productos_guardados
