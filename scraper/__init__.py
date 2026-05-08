from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import re
import time

import requests
from bs4 import BeautifulSoup


URL_SUPERSEIS = "https://www.superseis.com.py/"
URL_STOCK = "https://www.stock.com.py/"
REQUEST_TIMEOUT = 20
PAUSA_ENTRE_PAGINAS = 1
RUTA_CATEGORIAS_STOCK = (
    Path(__file__).resolve().parent.parent / "stock_categorias_urls.txt"
)
CATEGORIAS_SUPERSEIS = [
    ("https://www.superseis.com.py/catalog/almacen", "Almacen"),
    ("https://www.superseis.com.py/catalog/bebidas-sin-alcohol", "Bebidas sin alcohol"),
    ("https://www.superseis.com.py/catalog/lacteos/leches", "Lacteos - Leches"),
    ("https://www.superseis.com.py/catalog/lacteos/yogures", "Lacteos - Yogures"),
    ("https://www.superseis.com.py/catalog/limpieza", "Limpieza"),
    ("https://www.superseis.com.py/catalog/hogar-y-bazar", "Hogar y Bazar"),
    ("https://www.superseis.com.py/catalog/carnes", "Carnes"),
    ("https://www.superseis.com.py/catalog/Congelados", "Congelados"),
    ("https://www.superseis.com.py/catalog/frescos", "Frescos"),
    ("https://www.superseis.com.py/catalog/bebes", "Bebes"),
    ("https://www.superseis.com.py/catalog/panaderia", "Panaderia"),
    ("https://www.superseis.com.py/catalog/ferreteria", "Ferreteria"),
    ("https://www.superseis.com.py/catalog/electrodomesticos", "Electrodomesticos"),
    ("https://www.superseis.com.py/catalog/mascotas", "Mascotas"),
    ("https://www.superseis.com.py/catalog/pastas", "Pastas"),
    ("https://www.superseis.com.py/catalog/perfumeria", "Perfumeria"),
    ("https://www.superseis.com.py/catalog/reposteria", "Reposteria"),
]


def obtener_headers():
    """Retorna headers basicos para simular un navegador."""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-PY,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "DNT": "1",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }


def crear_sesion():
    """Crea una sesion HTTP reutilizable para reducir overhead."""
    sesion = requests.Session()
    sesion.headers.update(obtener_headers())
    return sesion


def limpiar_precio(precio_texto):
    """Convierte texto de precio paraguayo a entero o None si es invalido."""
    if not precio_texto:
        return None

    precio_limpio = str(precio_texto).strip()
    precio_limpio = re.sub(r"(?i)\bgs\.?\b|pyg|₲", "", precio_limpio)
    precio_limpio = precio_limpio.split(",", 1)[0]
    precio_limpio = (
        precio_limpio.replace(".", "")
        .replace("\xa0", "")
        .replace(" ", "")
        .strip()
    )

    if not precio_limpio.isdigit():
        return None

    return int(precio_limpio)


def limpiar_precio_stock(precio_texto):
    """Alias de compatibilidad para precios de Stock."""
    return limpiar_precio(precio_texto)


def normalizar_nombre_producto(nombre):
    """Normaliza espacios y evita nombres vacios."""
    return " ".join(str(nombre or "").split()).strip()


def fecha_registro_actual():
    return datetime.today().strftime("%Y-%m-%d")


def fecha_hora_registro_actual():
    return datetime.now().isoformat(timespec="seconds")


def construir_producto(
    supermercado,
    nombre,
    precio_texto,
    categoria=None,
    url_producto=None,
    unidad="unidad",
):
    """Construye un producto valido o retorna None si faltan datos criticos."""
    nombre_producto = normalizar_nombre_producto(nombre)
    precio = limpiar_precio(precio_texto)

    if not nombre_producto or precio is None:
        return None

    return {
        "supermercado": supermercado,
        "nombre_producto": nombre_producto,
        "precio": precio,
        "unidad": unidad,
        "fecha_registro": fecha_registro_actual(),
        "categoria": categoria,
        "url_producto": url_producto,
        "moneda": "PYG",
        "fecha_hora_registro": fecha_hora_registro_actual(),
    }


def extraer_url_producto(contenedor, base_url):
    enlace = contenedor.select_one("a[href]")
    if not enlace:
        return None
    return urljoin(base_url, enlace.get("href"))


def extraer_productos(html, categoria=None, url_categoria=URL_SUPERSEIS):
    """Extrae productos desde el HTML de una pagina de Superseis."""
    soup = BeautifulSoup(html, "html.parser")
    productos_html = soup.find_all("div", class_="product-thumb")
    productos = []

    for producto_html in productos_html:
        try:
            nombre_html = producto_html.find("h4")
            precio_html = producto_html.select_one("span.price-normal")

            if not nombre_html or not precio_html:
                continue

            producto = construir_producto(
                supermercado="Superseis",
                nombre=nombre_html.get_text(" ", strip=True),
                precio_texto=precio_html.get_text(" ", strip=True),
                categoria=categoria,
                url_producto=extraer_url_producto(producto_html, url_categoria),
            )

            if producto:
                productos.append(producto)
        except Exception as error:
            print(f"Producto de Superseis omitido por error de lectura: {error}")

    return productos


def construir_url_pagina(url, pagina):
    """Agrega el parametro de pagina a una URL de categoria."""
    separador = "&" if "?" in url else "?"
    return f"{url}{separador}page={pagina}"


def construir_url_pagina_stock(url, pagina):
    """Agrega el parametro de pagina usado por Stock."""
    separador = "&" if "?" in url else "?"
    return f"{url}{separador}pageindex={pagina}"


def leer_categorias_stock():
    """Lee las categorias de Stock desde el archivo local."""
    categorias = []

    try:
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

                nombre_categoria = normalizar_nombre_producto(nombre_categoria)
                categorias.append((nombre_categoria or "Sin categoria", url.strip()))
    except FileNotFoundError:
        print(f"No se encontro {RUTA_CATEGORIAS_STOCK}.")

    return categorias


def extraer_productos_stock(html, categoria=None, url_categoria=URL_STOCK):
    """Extrae productos desde el HTML de una pagina de Stock."""
    soup = BeautifulSoup(html, "html.parser")
    productos_html = soup.select("h2.product-title")
    productos = []

    for nombre_html in productos_html:
        try:
            contenedor_producto = nombre_html.find_parent()
            precio_html = None
            contenedor_busqueda = contenedor_producto

            while contenedor_busqueda and not precio_html:
                precio_html = contenedor_busqueda.select_one("span.price-label")
                contenedor_busqueda = contenedor_busqueda.find_parent()

            if not precio_html:
                continue

            producto = construir_producto(
                supermercado="Stock",
                nombre=nombre_html.get_text(" ", strip=True),
                precio_texto=precio_html.get_text(" ", strip=True),
                categoria=categoria,
                url_producto=extraer_url_producto(
                    contenedor_producto or nombre_html,
                    url_categoria,
                ),
            )

            if producto:
                productos.append(producto)
        except Exception as error:
            print(f"Producto de Stock omitido por error de lectura: {error}")

    return productos


def descargar_html(sesion, url, contexto):
    """Descarga una pagina y retorna HTML, o None si falla."""
    try:
        respuesta = sesion.get(url, timeout=REQUEST_TIMEOUT)
        respuesta.raise_for_status()
        return respuesta.text
    except requests.RequestException as error:
        print(f"Error al scrapear {contexto}: {error}")
        return None


def scrapear_superseis():
    """Scrapea productos destacados de Superseis y retorna una lista de precios."""
    with crear_sesion() as sesion:
        html = descargar_html(sesion, URL_SUPERSEIS, "Superseis")

    if not html:
        return []

    return extraer_productos(html, categoria="Home", url_categoria=URL_SUPERSEIS)


def scrapear_categoria(url, nombre_categoria, limite_paginas=100, sesion=None):
    """Scrapea todas las paginas de una categoria de Superseis."""
    productos_categoria = []
    paginas_con_productos = 0
    sesion_propia = sesion is None

    if sesion is None:
        sesion = crear_sesion()

    try:
        for pagina in range(1, limite_paginas + 1):
            url_pagina = construir_url_pagina(url, pagina)
            html = descargar_html(
                sesion,
                url_pagina,
                f"Superseis {nombre_categoria}, pagina {pagina}",
            )

            if not html:
                break

            productos = extraer_productos(
                html,
                categoria=nombre_categoria,
                url_categoria=url,
            )

            if not productos:
                break

            productos_categoria.extend(productos)
            paginas_con_productos += 1
            time.sleep(PAUSA_ENTRE_PAGINAS)
    finally:
        if sesion_propia:
            sesion.close()

    print(
        f"Superseis - {nombre_categoria}: {len(productos_categoria)} productos "
        f"en {paginas_con_productos} paginas"
    )
    return productos_categoria


def scrapear_todas_las_categorias(limite_categorias=None, limite_paginas=100):
    """Scrapea todas las categorias configuradas de Superseis."""
    todos_los_productos = []
    categorias = CATEGORIAS_SUPERSEIS

    if limite_categorias is not None:
        categorias = categorias[:limite_categorias]

    with crear_sesion() as sesion:
        for url, nombre_categoria in categorias:
            productos = scrapear_categoria(
                url,
                nombre_categoria,
                limite_paginas,
                sesion=sesion,
            )
            todos_los_productos.extend(productos)
            time.sleep(PAUSA_ENTRE_PAGINAS)

    return todos_los_productos


def scrapear_stock(limite_categorias=None, limite_paginas=50):
    """Scrapea todos los productos de Stock usando el archivo de categorias."""
    todos_los_productos = []
    categorias = leer_categorias_stock()

    if limite_categorias is not None:
        categorias = categorias[:limite_categorias]

    with crear_sesion() as sesion:
        for nombre_categoria, url in categorias:
            productos_categoria = []
            paginas_con_productos = 0

            for pagina in range(1, limite_paginas + 1):
                url_pagina = construir_url_pagina_stock(url, pagina)
                html = descargar_html(
                    sesion,
                    url_pagina,
                    f"Stock {nombre_categoria}, pagina {pagina}",
                )

                if not html:
                    break

                productos = extraer_productos_stock(
                    html,
                    categoria=nombre_categoria,
                    url_categoria=url,
                )

                if not productos:
                    break

                productos_categoria.extend(productos)
                paginas_con_productos += 1
                time.sleep(PAUSA_ENTRE_PAGINAS)

            todos_los_productos.extend(productos_categoria)
            print(
                f"Stock - {nombre_categoria}: {len(productos_categoria)} productos "
                f"en {paginas_con_productos} paginas"
            )

    return todos_los_productos
