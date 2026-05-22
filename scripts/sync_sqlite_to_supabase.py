#!/usr/bin/env python3
"""Sincroniza historicos faltantes de SQLite hacia Supabase."""

import argparse
import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import (  # noqa: E402
    CLAVE_UNICA,
    COLUMNAS_BASE,
    COLUMNAS_EXTRA,
    RUTA_DB,
    TAMANO_LOTE_SUPABASE,
    dividir_en_lotes,
    guardar_en_supabase,
    inicializar_supabase,
    preparar_productos,
)

TAMANO_LOTE_LECTURA = 1000
INTERVALO_PROGRESO_SUPABASE_PAGINAS = 25
INTERVALO_PROGRESO_SQLITE = 50000
COLUMNAS_SYNC = tuple(COLUMNAS_BASE) + tuple(COLUMNAS_EXTRA)


def parsear_argumentos():
    parser = argparse.ArgumentParser(
        description="Sincroniza registros historicos faltantes desde SQLite a Supabase."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Ejecuta la sincronizacion. Sin esta opcion solo muestra un resumen.",
    )
    parser.add_argument(
        "--limite",
        type=int,
        help="Cantidad maxima de faltantes a sincronizar. Util para pruebas.",
    )
    parser.add_argument(
        "--db",
        default=str(RUTA_DB),
        help="Ruta de la base SQLite local.",
    )
    return parser.parse_args()


def clave_producto(producto):
    return tuple(str(producto.get(columna) or "").strip() for columna in CLAVE_UNICA)


def cargar_productos_sqlite(ruta_db):
    ruta = Path(ruta_db)

    if not ruta.exists():
        raise FileNotFoundError(f"No existe la base SQLite: {ruta}")

    columnas_sql = ", ".join(COLUMNAS_SYNC)

    with sqlite3.connect(ruta) as conexion:
        conexion.row_factory = sqlite3.Row
        cursor = conexion.execute(f"SELECT {columnas_sql} FROM precios")
        productos = [dict(fila) for fila in cursor.fetchall()]

    return preparar_productos(productos)


def cargar_claves_supabase(supabase):
    claves = set()
    inicio = 0
    pagina = 0

    while True:
        fin = inicio + TAMANO_LOTE_LECTURA - 1
        respuesta = (
            supabase.table("precios")
            .select(",".join(CLAVE_UNICA))
            .order("id")
            .range(inicio, fin)
            .execute()
        )
        lote = respuesta.data or []

        if not lote:
            break

        pagina += 1
        claves.update(clave_producto(producto) for producto in lote)

        if pagina == 1 or pagina % INTERVALO_PROGRESO_SUPABASE_PAGINAS == 0:
            print(
                "Supabase claves: "
                f"pagina {pagina}, {len(claves)} claves acumuladas"
            )

        if len(lote) < TAMANO_LOTE_LECTURA:
            break

        inicio += TAMANO_LOTE_LECTURA

    print(f"Paginas Supabase leidas: {pagina}")
    return claves


def detectar_faltantes(productos_sqlite, claves_supabase, limite=None):
    faltantes = []
    vistos = set()

    for indice, producto in enumerate(productos_sqlite, start=1):
        clave = clave_producto(producto)

        if clave not in claves_supabase and clave not in vistos:
            faltantes.append(producto)
            vistos.add(clave)

        if indice % INTERVALO_PROGRESO_SQLITE == 0:
            print(
                "SQLite revisados: "
                f"{indice}; faltantes acumulados: {len(faltantes)}"
            )

        if limite is not None and len(faltantes) >= limite:
            print(
                "Deteccion detenida por limite: "
                f"{len(faltantes)} faltante(s)"
            )
            break

    return faltantes


def mostrar_resumen(productos_sqlite, claves_supabase, faltantes):
    print(f"Registros validos en SQLite: {len(productos_sqlite)}")
    print(f"Claves existentes en Supabase: {len(claves_supabase)}")
    print(f"Registros faltantes detectados: {len(faltantes)}")

    if faltantes:
        print("Primeros faltantes:")
        for producto in faltantes[:5]:
            print(
                "- "
                f"{producto['fecha_registro']} | "
                f"{producto['supermercado']} | "
                f"{producto['nombre_producto']} | "
                f"{producto['precio']}"
            )


def sincronizar_faltantes(faltantes, aplicar=False):
    if not faltantes:
        print("No hay historicos faltantes para sincronizar.")
        return 0

    if not aplicar:
        print("Modo revision: no se envio nada. Usa --apply para sincronizar.")
        return 0

    total_lotes = (len(faltantes) + TAMANO_LOTE_SUPABASE - 1) // TAMANO_LOTE_SUPABASE
    print(
        "Lotes a enviar a Supabase: "
        f"{total_lotes} de hasta {TAMANO_LOTE_SUPABASE} registros"
    )
    sincronizados = guardar_en_supabase(faltantes)
    print(f"Historicos enviados a Supabase: {sincronizados}")
    return sincronizados


def verificar_sync_final(productos_sqlite, supabase, limite=None):
    if limite is not None:
        print("Validacion final omitida por --limite: sincronizacion parcial.")
        return None

    print("Validacion final: revisando Supabase despues del sync.")
    claves_finales = cargar_claves_supabase(supabase)
    pendientes = detectar_faltantes(productos_sqlite, claves_finales)
    print(f"Pendientes finales: {len(pendientes)}")

    if not pendientes:
        print("Supabase verificado: sin faltantes.")

    return len(pendientes)


def main():
    argumentos = parsear_argumentos()

    try:
        productos_sqlite = cargar_productos_sqlite(argumentos.db)
    except FileNotFoundError as error:
        print(error)
        return 1

    supabase = inicializar_supabase()
    if supabase is None:
        return 1

    claves_supabase = cargar_claves_supabase(supabase)
    faltantes = detectar_faltantes(
        productos_sqlite,
        claves_supabase,
        limite=argumentos.limite,
    )
    mostrar_resumen(productos_sqlite, claves_supabase, faltantes)
    sincronizados = sincronizar_faltantes(faltantes, aplicar=argumentos.apply)

    if argumentos.apply and faltantes:
        pendientes_finales = verificar_sync_final(
            productos_sqlite,
            supabase,
            limite=argumentos.limite,
        )
        if pendientes_finales is not None and pendientes_finales > 0:
            return 2
        if sincronizados < len(faltantes):
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
