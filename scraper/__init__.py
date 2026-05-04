from datetime import datetime
import time

import requests
from bs4 import BeautifulSoup


URL_SUPERSEIS = "https://www.superseis.com.py/"
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


def scrapear_superseis():
    """Scrapea productos de Superseis y retorna una lista de precios."""
    try:
        respuesta = requests.get(URL_SUPERSEIS, headers=obtener_headers(), timeout=15)
        respuesta.raise_for_status()
    except requests.RequestException as error:
        print(f"Error al scrapear Superseis: {error}")
        return []

    return extraer_productos(respuesta.text)


def scrapear_categoria(url, nombre_categoria):
    """Scrapea todas las páginas de una categoría de Superseis."""
    productos_categoria = []
    paginas_con_productos = 0

    for pagina in range(1, 101):
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


def scrapear_todas_las_categorias():
    """Scrapea todas las categorías configuradas de Superseis."""
    todos_los_productos = []

    for url, nombre_categoria in CATEGORIAS_SUPERSEIS:
        productos = scrapear_categoria(url, nombre_categoria)
        todos_los_productos.extend(productos)
        time.sleep(2)

    return todos_los_productos
