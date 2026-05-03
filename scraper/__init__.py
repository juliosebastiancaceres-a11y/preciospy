from datetime import datetime
import time

import requests
from bs4 import BeautifulSoup


URL_SUPERSEIS = "https://www.superseis.com.py/"
CATEGORIAS_SUPERSEIS = [
    ("https://www.superseis.com.py/catalog/almacen/arroces", "Almacén - Arroces"),
    ("https://www.superseis.com.py/catalog/almacen/aceites", "Almacén - Aceites"),
    (
        "https://www.superseis.com.py/catalog/almacen/azucar-y-endulzantes",
        "Almacén - Azúcar",
    ),
    ("https://www.superseis.com.py/catalog/bebidas-sin-alcohol", "Bebidas sin alcohol"),
    ("https://www.superseis.com.py/catalog/lacteos/leches", "Lácteos - Leches"),
    ("https://www.superseis.com.py/catalog/lacteos/yogures", "Lácteos - Yogures"),
    ("https://www.superseis.com.py/catalog/limpieza", "Limpieza"),
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
    """Scrapea una categoría de Superseis y retorna sus productos."""
    try:
        respuesta = requests.get(url, headers=obtener_headers(), timeout=15)
        respuesta.raise_for_status()
    except requests.RequestException as error:
        print(f"Error al scrapear {nombre_categoria}: {error}")
        return []

    productos = extraer_productos(respuesta.text)
    print(f"{nombre_categoria}: {len(productos)} productos encontrados")
    return productos


def scrapear_todas_las_categorias():
    """Scrapea todas las categorías configuradas de Superseis."""
    todos_los_productos = []

    for url, nombre_categoria in CATEGORIAS_SUPERSEIS:
        productos = scrapear_categoria(url, nombre_categoria)
        todos_los_productos.extend(productos)
        time.sleep(2)

    return todos_los_productos
