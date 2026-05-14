import argparse
import sys

from database import guardar_en_supabase, guardar_productos, inicializar_db
from scraper import (
    scrapear_casa_rica,
    scrapear_los_jardines,
    scrapear_stock,
    scrapear_todas_las_categorias,
)


def parsear_argumentos():
    """Lee opciones de ejecucion para correr scrapers de forma parcial."""
    parser = argparse.ArgumentParser(description="Scraper de precios de supermercados")
    parser.add_argument(
        "--supermercado",
        choices=("todos", "superseis", "stock", "losjardines", "casarica"),
        default="todos",
        help="Supermercado a scrapear. Por defecto corre todos.",
    )
    parser.add_argument(
        "--sin-supabase",
        action="store_true",
        help="Guarda solo en SQLite local y no envia datos a Supabase.",
    )
    parser.add_argument(
        "--limite-categorias",
        type=int,
        help="Cantidad maxima de categorias a scrapear. Util para pruebas.",
    )
    parser.add_argument(
        "--limite-paginas",
        type=int,
        help="Cantidad maxima de paginas por categoria. Util para pruebas.",
    )
    return parser.parse_args()


def obtener_productos(supermercado, limite_categorias=None, limite_paginas=None):
    """Ejecuta los scrapers pedidos y combina sus resultados."""
    productos = []

    if supermercado in ("todos", "superseis"):
        productos.extend(
            scrapear_todas_las_categorias(
                limite_categorias=limite_categorias,
                limite_paginas=limite_paginas or 100,
            )
        )

    if supermercado in ("todos", "stock"):
        productos.extend(
            scrapear_stock(
                limite_categorias=limite_categorias,
                limite_paginas=limite_paginas or 50,
            )
        )

    if supermercado in ("todos", "losjardines"):
        productos.extend(
            scrapear_los_jardines(
                limite_categorias=limite_categorias,
                limite_paginas=limite_paginas or 250,
            )
        )

    if supermercado in ("todos", "casarica"):
        productos.extend(
            scrapear_casa_rica(
                limite_categorias=limite_categorias,
                limite_paginas=limite_paginas or 250,
            )
        )

    return productos


def main():
    argumentos = parsear_argumentos()
    inicializar_db()
    print("Base de datos inicializada correctamente.")

    productos = obtener_productos(
        argumentos.supermercado,
        limite_categorias=argumentos.limite_categorias,
        limite_paginas=argumentos.limite_paginas,
    )
    print(f"Productos scrapeados: {len(productos)}")

    if not productos:
        print("No se encontraron productos validos. No se guarda nada.")
        return 1

    guardar_productos(productos)

    if argumentos.sin_supabase:
        print("Supabase omitido por opcion --sin-supabase.")
        return 0

    productos_supabase = guardar_en_supabase(productos)

    if productos_supabase == 0:
        print("No se sincronizaron productos con Supabase.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
