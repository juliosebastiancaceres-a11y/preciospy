#!/usr/bin/env python3
"""Deduplica registros historicos de la base SQLite local."""

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import (  # noqa: E402
    RUTA_DB,
    contar_duplicados_sqlite,
    deduplicar_precios_sqlite,
)


def parsear_argumentos():
    parser = argparse.ArgumentParser(
        description="Limpia duplicados historicos de la tabla precios en SQLite."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Ejecuta la limpieza. Sin esta opcion solo muestra un resumen.",
    )
    parser.add_argument(
        "--db",
        default=str(RUTA_DB),
        help="Ruta de la base SQLite local.",
    )
    return parser.parse_args()


def crear_backup(ruta_db):
    marca_tiempo = datetime.now().strftime("%Y%m%d-%H%M%S")
    ruta_backup = ruta_db.with_name(f"{ruta_db.name}.bak-{marca_tiempo}")
    shutil.copy2(ruta_db, ruta_backup)
    return ruta_backup


def contar_registros(ruta_db):
    with sqlite3.connect(ruta_db) as conexion:
        return conexion.execute("SELECT COUNT(*) FROM precios").fetchone()[0]


def main():
    argumentos = parsear_argumentos()
    ruta_db = Path(argumentos.db)

    if not ruta_db.exists():
        print(f"No existe la base SQLite: {ruta_db}")
        return 1

    total_antes = contar_registros(ruta_db)
    duplicados_antes = contar_duplicados_sqlite(ruta_db)
    print(f"Base SQLite: {ruta_db}")
    print(f"Registros totales: {total_antes}")
    print(f"Grupos duplicados: {duplicados_antes['grupos']}")
    print(f"Filas duplicadas sobrantes: {duplicados_antes['filas_sobrantes']}")

    if duplicados_antes["filas_sobrantes"] == 0:
        print("No hay duplicados para limpiar.")
        return 0

    if not argumentos.apply:
        print("Modo revision: no se elimino nada. Usa --apply para limpiar.")
        return 0

    ruta_backup = crear_backup(ruta_db)
    eliminados = deduplicar_precios_sqlite(ruta_db)
    duplicados_despues = contar_duplicados_sqlite(ruta_db)
    total_despues = contar_registros(ruta_db)

    print(f"Backup creado: {ruta_backup}")
    print(f"Filas eliminadas: {eliminados}")
    print(f"Registros totales despues: {total_despues}")
    print(f"Duplicados restantes: {duplicados_despues['filas_sobrantes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
