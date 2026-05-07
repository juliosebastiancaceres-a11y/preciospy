from datetime import datetime
from pathlib import Path
import time

import requests
from bs4 import BeautifulSoup


URL_SUPERSEIS = "https://www.superseis.com.py/"
RUTA_CATEGORIAS_STOCK = (
    Path(__file__).resolve().parent.parent / "stock_categorias_urls.txt"
)
CATEGORIAS_SUPERSEIS = [
    ("https://www.superseis.com.py/catalog/almacen", "Almacén"),
    ("https://www.superseis.com.py/catalog/bebidas-sin-alcohol", "Bebidas sin alcohol"),
    ("https://www.superseis.com.py/catalog/lacteos/leches", "Lácteos - Leches"),
    ("https://www.superseis.com.py/catalog/lacteos/yogures", "Lácteos - Yogures"),
    ("https://www.superseis.com.py/catalog/limpieza", "Limpieza"),
    ("https://www.superseis.com.py/catalog/hogar-y-bazar", "Hogar y Bazar"),
    ("https://www.superseis.com.py/catalog/carnes", "Carnes"),
    ("https://www.superseis.com.py/catalog/Congelados", "Congelados"),
    ("https://www.superseis.com.py/catalog/frescos", "Frescos"),
    ("https://www.superseis.com.py/catalog/bebes", "Bebés"),
    ("https://www.superseis.com.py/catalog/panaderia", "Panadería"),
    ("https://www.superseis.com.py/catalog/ferreteria", "Ferretería"),
    ("https://www.superseis.com.py/catalog/electrodomesticos", "Electrodomésticos"),
    ("https://www.superseis.com.py/catalog/mascotas", "Mascotas"),
    ("https://www.superseis.com.py/catalog/pastas", "Pastas"),
    ("https://www.superseis.com.py/catalog/perfumeria", "Perfumería"),
    ("https://www.superseis.com.py/catalog/reposteria", "Repostería"),
]


def obtener_headers():
    """Retorna headers básicos para simular un navegador."""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-PY,es;q=0.9,en;q=0.8",
    }


def limpiar_precio(precio_texto):
    """Convierte un precio en texto a un número entero."""
    precio_limpio = (
        precio_texto.replace("₲", "")
        .replace(".", "")
        .replace(" ", "")
        .strip()
    )
    return int(precio_limpio)


def extraer_productos(html):
    """Extrae productos desde el HTML de una página de Superseis."""
    soup = BeautifulSoup(html, "html.parser")
    productos_html = soup.find_all("div", class_="product-thumb")
    fecha_registro = datetime.today().strftime("%Y-%m-%d")
    productos = []

    for producto_html in productos_html:
        nombre_html = producto_html.find("h4")
        precio_html = producto_html.select_one("span.price-normal")

        if not nombre_html or not precio_html:
            continue

        productos.append(
            {
                "supermercado": "Superseis",
                "nombre_producto": nombre_html.get_text(strip=True),
                "precio": limpiar_precio(precio_html.get_text(strip=True)),
                "unidad": "unidad",
                "fecha_registro": fecha_registro,
            }
        )

    return productos


def construir_url_pagina(url, pagina):
    """Agrega el parámetro de página a una URL de categoría."""
    separador = "&" if "?" in url else "?"
    return f"{url}{separador}page={pagina}"


def construir_url_pagina_stock(url, pagina):
    """Agrega el parámetro de página usado por Stock."""
    separador = "&" if "?" in url else "?"
    return f"{url}{separador}pageindex={pagina}"


def limpiar_precio_stock(precio_texto):
    """Convierte un precio de Stock a un número entero."""
    precio_limpio = (
        precio_texto.replace("Gs", "")
        .replace("₲", "")
        .replace(".", "")
        .replace(" ", "")
        .strip()
    )
    return int(precio_limpio)


def leer_categorias_stock():
    """Lee las categorías de Stock desde el archivo local."""
    categorias = []

    with open(RUTA_CATEGORIAS_STOCK, encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()

            if not linea or linea.startswith("#"):
                continue

            if "\t" in linea:
                nombre_categoria, url = linea.split("\t", 1)
            else:
                nombre_categoria = linea
                url = linea

            categorias.append((nombre_categoria, url))

    return categorias


def extraer_productos_stock(html):
    """Extrae productos desde el HTML de una página de Stock."""
    soup = BeautifulSoup(html, "html.parser")
    productos_html = soup.select("h2.product-title")
    fecha_registro = datetime.today().strftime("%Y-%m-%d")
    productos = []

    for nombre_html in productos_html:
        contenedor_producto = nombre_html.find_parent()
        precio_html = None

        while contenedor_producto and not precio_html:
            precio_html = contenedor_producto.select_one("span.price-label")
            contenedor_producto = contenedor_producto.find_parent()

        if not precio_html:
            continue

        productos.append(
            {
                "supermercado": "Stock",
                "nombre_producto": nombre_html.get_text(strip=True),
                "precio": limpiar_precio_stock(precio_html.get_text(strip=True)),
                "unidad": "unidad",
                "fecha_registro": fecha_registro,
            }
        )

    return productos


def scrapear_superseis():
    """Scrapea productos de Superseis y retorna una lista de precios."""
    try:
        respuesta = requests.get(URL_SUPERSEIS, headers=obtener_headers(), timeout=15)
        respuesta.raise_for_status()
    except requests.RequestException as error:
        print(f"Error al scrapear Superseis: {error}")
        return []

    return extraer_productos(respuesta.text)


def scrapear_categoria(url, nombre_categoria, limite_paginas=100):
    """Scrapea todas las páginas de una categoría de Superseis."""
    productos_categoria = []
    paginas_con_productos = 0

    for pagina in range(1, limite_paginas + 1):
        url_pagina = construir_url_pagina(url, pagina)

        try:
            respuesta = requests.get(
                url_pagina,
                headers=obtener_headers(),
                timeout=15,
            )
            respuesta.raise_for_status()
        except requests.RequestException as error:
            print(f"Error al scrapear {nombre_categoria}, página {pagina}: {error}")
            break

        productos = extraer_productos(respuesta.text)

        if not productos:
            break

        productos_categoria.extend(productos)
        paginas_con_productos += 1
        time.sleep(2)

    print(
        f"{nombre_categoria}: {len(productos_categoria)} productos encontrados "
        f"en {paginas_con_productos} páginas"
    )
    return productos_categoria


def scrapear_todas_las_categorias(limite_categorias=None, limite_paginas=100):
    """Scrapea todas las categorías configuradas de Superseis."""
    todos_los_productos = []
    categorias = CATEGORIAS_SUPERSEIS

    if limite_categorias is not None:
        categorias = categorias[:limite_categorias]

    for url, nombre_categoria in categorias:
        productos = scrapear_categoria(url, nombre_categoria, limite_paginas)
        todos_los_productos.extend(productos)
        time.sleep(2)

    return todos_los_productos


def scrapear_stock(limite_categorias=None, limite_paginas=50):
    """Scrapea todos los productos de Stock usando el archivo de categorías."""
    todos_los_productos = []
    categorias = leer_categorias_stock()

    if limite_categorias is not None:
        categorias = categorias[:limite_categorias]

    for nombre_categoria, url in categorias:
        productos_categoria = []
        paginas_con_productos = 0

        for pagina in range(1, limite_paginas + 1):
            url_pagina = construir_url_pagina_stock(url, pagina)

            try:
                respuesta = requests.get(
                    url_pagina,
                    headers=obtener_headers(),
                    timeout=15,
                )
                respuesta.raise_for_status()
            except requests.RequestException as error:
                print(
                    f"Error al scrapear Stock {nombre_categoria}, "
                    f"página {pagina}: {error}"
                )
                break

            productos = extraer_productos_stock(respuesta.text)

            if not productos:
                break

            productos_categoria.extend(productos)
            paginas_con_productos += 1
            time.sleep(1)

        todos_los_productos.extend(productos_categoria)
        print(
            f"Stock - {nombre_categoria}: {len(productos_categoria)} productos "
            f"en {paginas_con_productos} páginas"
        )

    return todos_los_productos
