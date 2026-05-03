from datetime import datetime

import requests
from bs4 import BeautifulSoup


URL_SUPERSEIS = "https://www.superseis.com.py/"


def limpiar_precio(precio_texto):
    """Convierte un precio en texto a un número entero."""
    precio_limpio = (
        precio_texto.replace("₲", "")
        .replace(".", "")
        .replace(" ", "")
        .strip()
    )
    return int(precio_limpio)


def scrapear_superseis():
    """Scrapea productos de Superseis y retorna una lista de precios."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-PY,es;q=0.9,en;q=0.8",
    }

    try:
        respuesta = requests.get(URL_SUPERSEIS, headers=headers, timeout=15)
        respuesta.raise_for_status()
    except requests.RequestException as error:
        print(f"Error al scrapear Superseis: {error}")
        return []

    soup = BeautifulSoup(respuesta.text, "html.parser")
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
