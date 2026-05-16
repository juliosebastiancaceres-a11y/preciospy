from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import os
import re
import time
import unicodedata

import requests
from bs4 import BeautifulSoup


URL_SUPERSEIS = "https://www.superseis.com.py/"
URL_STOCK = "https://www.stock.com.py/"
URL_LOS_JARDINES = "https://www.losjardinesonline.com.py/"
URL_CASA_RICA = "https://www.casarica.com.py/"
URL_BIGGIE = "https://www.biggie.com.py/"
URL_ARETE = "https://www.arete.com.py/"
URL_API_BIGGIE = "https://api.app.biggie.com.py/api/"
TAMANO_PAGINA_BIGGIE = 24


def leer_entero_entorno(nombre, defecto):
    """Lee un entero desde entorno sin romper si viene invalido."""
    try:
        return int(os.getenv(nombre, defecto))
    except (TypeError, ValueError):
        return defecto


def leer_float_entorno(nombre, defecto):
    """Lee un decimal desde entorno sin romper si viene invalido."""
    try:
        return float(os.getenv(nombre, defecto))
    except (TypeError, ValueError):
        return defecto


REQUEST_TIMEOUT = leer_entero_entorno("PRECIOSPY_REQUEST_TIMEOUT", 20)
REQUEST_REINTENTOS = leer_entero_entorno("PRECIOSPY_REQUEST_REINTENTOS", 3)
PAUSA_ENTRE_PAGINAS = leer_float_entorno("PRECIOSPY_PAUSA_ENTRE_PAGINAS", 1)
PAUSA_REINTENTO = leer_float_entorno("PRECIOSPY_PAUSA_REINTENTO", 5)
INTERVALO_PROGRESO_PAGINAS = leer_entero_entorno(
    "PRECIOSPY_INTERVALO_PROGRESO_PAGINAS",
    25,
)
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
CATEGORIAS_LOS_JARDINES = [
    ("https://www.losjardinesonline.com.py/catalogo/almacen-c2", "Almacen"),
    ("https://www.losjardinesonline.com.py/catalogo/delicatessen-c95", "Delicatessen"),
    ("https://www.losjardinesonline.com.py/catalogo/carnes-c48", "Carnes"),
    (
        "https://www.losjardinesonline.com.py/catalogo/frutas-y-verduras-c1",
        "Frutas y Verduras",
    ),
    ("https://www.losjardinesonline.com.py/catalogo/lacteos-c58", "Lacteos"),
    (
        "https://www.losjardinesonline.com.py/catalogo/nuestra-panaderia-c6",
        "Nuestra Panaderia",
    ),
    ("https://www.losjardinesonline.com.py/catalogo/panaderia-c116", "Panaderia"),
    ("https://www.losjardinesonline.com.py/catalogo/fiambreria-c7", "Fiambreria"),
    ("https://www.losjardinesonline.com.py/catalogo/congelados-c53", "Congelados"),
    (
        "https://www.losjardinesonline.com.py/catalogo/bebidas-sin-alcohol-c78",
        "Bebidas sin alcohol",
    ),
    (
        "https://www.losjardinesonline.com.py/catalogo/bebidas-con-alcohol-c4",
        "Bebidas con alcohol",
    ),
    ("https://www.losjardinesonline.com.py/catalogo/perfumeria-c3", "Perfumeria"),
    ("https://www.losjardinesonline.com.py/catalogo/limpieza-c5", "Limpieza"),
    ("https://www.losjardinesonline.com.py/catalogo/veterinaria-c69", "Veterinaria"),
    ("https://www.losjardinesonline.com.py/catalogo/ferreteria-c87", "Ferreteria"),
    ("https://www.losjardinesonline.com.py/catalogo/jugueteria-c89", "Jugueteria"),
    ("https://www.losjardinesonline.com.py/catalogo/libreria-c90", "Libreria"),
    ("https://www.losjardinesonline.com.py/catalogo/hogar-c96", "Hogar"),
]
CATEGORIAS_CASA_RICA = [
    ("https://www.casarica.com.py/catalogo/almacen-c1", "Almacen"),
    ("https://www.casarica.com.py/catalogo/bazar-c342", "Bazar"),
    ("https://www.casarica.com.py/catalogo/bebes-c288", "Bebes"),
    (
        "https://www.casarica.com.py/catalogo/bebidas-con-alcohol-c20",
        "Bebidas con alcohol",
    ),
    (
        "https://www.casarica.com.py/catalogo/bebidas-sin-alcohol-c46",
        "Bebidas sin alcohol",
    ),
    ("https://www.casarica.com.py/catalogo/carniceria-c56", "Carniceria"),
    (
        "https://www.casarica.com.py/catalogo/chocolates-y-golosinas-c65",
        "Chocolates y golosinas",
    ),
    (
        "https://www.casarica.com.py/catalogo/condimentos-salsas-c79",
        "Condimentos y salsas",
    ),
    ("https://www.casarica.com.py/catalogo/confiteria-c92", "Confiteria"),
    ("https://www.casarica.com.py/catalogo/congelados-c103", "Congelados"),
    ("https://www.casarica.com.py/catalogo/conservados-c116", "Conservados"),
    (
        "https://www.casarica.com.py/catalogo/cuidado-del-hogar-c123",
        "Cuidado del hogar",
    ),
    (
        "https://www.casarica.com.py/catalogo/cuidado-personal-c144",
        "Cuidado personal",
    ),
    ("https://www.casarica.com.py/catalogo/desayuno-c165", "Desayuno"),
    ("https://www.casarica.com.py/catalogo/fiambreria-c193", "Fiambreria"),
    ("https://www.casarica.com.py/catalogo/helados-c339", "Helados"),
    ("https://www.casarica.com.py/catalogo/lacteos-c209", "Lacteos"),
    ("https://www.casarica.com.py/catalogo/mascotas-c314", "Mascotas"),
    ("https://www.casarica.com.py/catalogo/panaderia-c225", "Panaderia"),
    ("https://www.casarica.com.py/catalogo/pastas-frescas-c237", "Pastas frescas"),
    ("https://www.casarica.com.py/catalogo/queseria-c247", "Queseria"),
    ("https://www.casarica.com.py/catalogo/rotiseria-c323", "Rotiseria"),
    ("https://www.casarica.com.py/catalogo/snacks-c271", "Snacks"),
    (
        "https://www.casarica.com.py/catalogo/verduleria-fruteria-c280",
        "Verduleria y fruteria",
    ),
]
CATEGORIAS_ARETE = [
    ("https://www.arete.com.py/catalogo/almacen-c273", "Almacen"),
    ("https://www.arete.com.py/catalogo/bazar-c414", "Bazar"),
    (
        "https://www.arete.com.py/catalogo/bebidas-con-alcohol-c266",
        "Bebidas con alcohol",
    ),
    (
        "https://www.arete.com.py/catalogo/bebidas-sin-alcohol-c297",
        "Bebidas sin alcohol",
    ),
    ("https://www.arete.com.py/catalogo/carnes-y-pescados-c261", "Carnes y pescados"),
    (
        "https://www.arete.com.py/catalogo/chocolate-y-golosinas-c398",
        "Chocolate y golosinas",
    ),
    ("https://www.arete.com.py/catalogo/confiteria-c420", "Confiteria"),
    ("https://www.arete.com.py/catalogo/congelados-c274", "Congelados"),
    (
        "https://www.arete.com.py/catalogo/cuidado-del-hogar-c309",
        "Cuidado del hogar",
    ),
    (
        "https://www.arete.com.py/catalogo/cuidado-personal-c322",
        "Cuidado personal",
    ),
    ("https://www.arete.com.py/catalogo/desayuno-c287", "Desayuno"),
    ("https://www.arete.com.py/catalogo/fiambres-c298", "Fiambres"),
    (
        "https://www.arete.com.py/catalogo/frutas-y-verduras-c367",
        "Frutas y verduras",
    ),
    ("https://www.arete.com.py/catalogo/electrodomesticos-c407", "Electrodomesticos"),
    ("https://www.arete.com.py/catalogo/lacteos-c364", "Lacteos"),
    ("https://www.arete.com.py/catalogo/mascotas-c399", "Mascotas"),
    ("https://www.arete.com.py/catalogo/panaderia-c395", "Panaderia"),
    ("https://www.arete.com.py/catalogo/pastas-frescas-c385", "Pastas frescas"),
    ("https://www.arete.com.py/catalogo/quesos-c366", "Quesos"),
    ("https://www.arete.com.py/catalogo/rotiseria-c464", "Rotiseria"),
    ("https://www.arete.com.py/catalogo/snacks-c475", "Snacks"),
    ("https://www.arete.com.py/catalogo/tienda-c402", "Tienda"),
    ("https://www.arete.com.py/catalogo/jugueteria-c519", "Jugueteria"),
    (
        "https://www.arete.com.py/catalogo/ferreteria-y-jardin-c520",
        "Ferreteria y jardin",
    ),
    ("https://www.arete.com.py/catalogo/cotillon-c521", "Cotillon"),
    ("https://www.arete.com.py/catalogo/libreria-c522", "Libreria"),
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


def crear_slug(texto):
    """Crea un slug simple compatible con URLs de catalogo."""
    texto = _quitar_acentos(normalizar_nombre_producto(texto)).lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")


def _quitar_acentos(texto):
    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caracter)
    )


def _parsear_numero(texto):
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        return None


def _parsear_numero_mililitros(texto):
    if re.fullmatch(r"\d{1,3}\.\d{3}", str(texto)):
        return float(str(texto).replace(".", ""))

    return _parsear_numero(texto)


def _formatear_numero_unidad(numero):
    if numero is None:
        return None

    if numero.is_integer():
        return str(int(numero))

    return f"{numero:g}"


def _normalizar_token_matching(token):
    sinonimos = {
        "azuc": "azucar",
        "azucares": "azucar",
        "choc": "chocolate",
        "choco": "chocolate",
        "clasica": "clasico",
        "clasicos": "clasico",
        "light": "zero",
        "originales": "original",
        "ret": "retornable",
        "retorn": "retornable",
        "desc": "descartable",
        "descart": "descartable",
        "un": "unidades",
        "uni": "unidades",
        "unidad": "unidades",
        "u": "unidades",
    }
    return sinonimos.get(token, token)


def _normalizar_tokens_productos(tokens):
    """Normaliza abreviaturas comerciales antes de comparar o buscar."""
    tokens_normalizados = []
    indice = 0

    while indice < len(tokens):
        token = tokens[indice]
        siguiente = tokens[indice + 1] if indice + 1 < len(tokens) else ""

        if token == "s" and siguiente in {"azuc", "azucar", "azucares"}:
            tokens_normalizados.append("sin")
            tokens_normalizados.append("azucar")
            indice += 2
            continue

        if token == "0" and siguiente in {"azuc", "azucar", "azucares"}:
            tokens_normalizados.append("sin")
            tokens_normalizados.append("azucar")
            indice += 2
            continue

        if token in {"sin", "zero"} and siguiente in {"azuc", "azucar", "azucares"}:
            tokens_normalizados.append("sin")
            tokens_normalizados.append("azucar")
            indice += 2
            continue

        if token == "zero":
            tokens_normalizados.append("sin")
            tokens_normalizados.append("azucar")
            indice += 1
            continue

        if token == "pack" and siguiente and _parsear_numero(siguiente) is not None:
            tokens_normalizados.append(siguiente)
            tokens_normalizados.append("unidades")
            indice += 2
            continue

        if token == "pack":
            indice += 1
            continue

        if token == "x" and siguiente and _parsear_numero(siguiente) is not None:
            tokens_normalizados.append(siguiente)
            tokens_normalizados.append("unidades")
            indice += 2
            continue

        if _parsear_numero(token) is not None and siguiente in {
            "un",
            "uni",
            "unidad",
            "unidades",
            "u",
        }:
            tokens_normalizados.append(token)
            tokens_normalizados.append("unidades")
            indice += 2
            continue

        tokens_normalizados.append(_normalizar_token_matching(token))
        indice += 1

    return tokens_normalizados


def _extraer_tokens_matching(nombre):
    nombre_comparable = normalizar_nombre_comparable(nombre)

    if not nombre_comparable:
        return [], []

    tokens = _normalizar_tokens_productos(nombre_comparable.split())
    unidades_medida = {"L", "ml", "g", "kg"}
    palabras_omitidas = {
        "a",
        "al",
        "bot",
        "botella",
        "botellas",
        "de",
        "del",
        "el",
        "envase",
        "gaseosa",
        "la",
        "las",
        "los",
        "marca",
        "pet",
        "producto",
        "sabor",
        "tipo",
    }
    tokens_producto = []
    unidades = []
    indice = 0

    while indice < len(tokens):
        token = tokens[indice]
        siguiente = tokens[indice + 1] if indice + 1 < len(tokens) else ""

        if _parsear_numero(token) is not None and siguiente in unidades_medida:
            unidades.append(f"{token} {siguiente}")
            indice += 2
            continue

        if token not in palabras_omitidas:
            tokens_producto.append(token)

        indice += 1

    return list(dict.fromkeys(tokens_producto)), list(dict.fromkeys(unidades))


def normalizar_nombre_comparable(nombre):
    """Normaliza nombres para busqueda y comparacion entre supermercados."""
    nombre_limpio = normalizar_nombre_producto(nombre)

    if not nombre_limpio:
        return ""

    texto = _quitar_acentos(nombre_limpio).lower()
    texto = re.sub(r"(\d)([a-z])", r"\1 \2", texto)
    texto = re.sub(r"([a-z])(\d)", r"\1 \2", texto)
    texto = re.sub(r"[^a-z0-9,.]+", " ", texto)
    tokens = [token.strip(".,") for token in texto.split()]
    tokens = [token for token in tokens if token]
    tokens = _normalizar_tokens_productos(tokens)

    unidades_litro = {"l", "lt", "lts", "litro", "litros"}
    unidades_mililitro = {"ml", "mililitro", "mililitros", "cc"}
    unidades_gramo = {"g", "gr", "grs", "gramo", "gramos"}
    unidades_kilo = {"kg", "kgs", "kilo", "kilos", "kilogramo", "kilogramos"}
    unidades_conocidas = (
        unidades_litro | unidades_mililitro | unidades_gramo | unidades_kilo
    )
    tokens_normalizados = []
    indice = 0

    while indice < len(tokens):
        token = tokens[indice]
        siguiente = tokens[indice + 1] if indice + 1 < len(tokens) else ""
        numero = _parsear_numero(token)

        if numero is not None and siguiente in unidades_litro:
            tokens_normalizados.extend([_formatear_numero_unidad(numero), "L"])
            indice += 2
            continue

        if numero is not None and siguiente in unidades_mililitro:
            numero_ml = _parsear_numero_mililitros(token)

            if numero_ml >= 1000:
                tokens_normalizados.extend(
                    [_formatear_numero_unidad(numero_ml / 1000), "L"]
                )
            else:
                tokens_normalizados.extend(
                    [_formatear_numero_unidad(numero_ml), "ml"]
                )
            indice += 2
            continue

        if numero is not None and siguiente in unidades_gramo:
            tokens_normalizados.extend([_formatear_numero_unidad(numero), "g"])
            indice += 2
            continue

        if numero is not None and siguiente in unidades_kilo:
            tokens_normalizados.extend([_formatear_numero_unidad(numero), "kg"])
            indice += 2
            continue

        if token not in unidades_conocidas:
            tokens_normalizados.append(token)

        indice += 1

    return " ".join(tokens_normalizados)


def obtener_clave_matching_producto(nombre):
    """Crea una clave flexible para comparar productos equivalentes."""
    tokens_unicos, unidades_unicas = _extraer_tokens_matching(nombre)
    tokens_unicos = sorted(tokens_unicos)
    unidades_unicas = sorted(unidades_unicas)

    if not tokens_unicos:
        return ""

    return " ".join(tokens_unicos + unidades_unicas)


def obtener_etiqueta_matching_producto(nombre):
    """Crea una etiqueta legible para mostrar productos equivalentes."""
    tokens_unicos, unidades_unicas = _extraer_tokens_matching(nombre)

    if not tokens_unicos:
        return ""

    return " ".join(tokens_unicos + unidades_unicas)


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
        "nombre_normalizado": normalizar_nombre_comparable(nombre_producto),
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


def extraer_url_producto_dattamax(contenedor, base_url):
    enlace = contenedor.select_one("a.ecommercepro-LoopProduct-link[href]")
    if enlace:
        return urljoin(base_url, enlace.get("href"))

    return extraer_url_producto(contenedor, base_url)


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


def construir_url_pagina_los_jardines(url, pagina):
    """Construye la URL paginada que usa Los Jardines."""
    if pagina <= 1:
        return url

    url_sin_fragmento, separador_fragmento, fragmento = url.partition("#")
    url_base, separador_query, query = url_sin_fragmento.partition("?")
    url_paginada = f"{url_base}.{pagina}"

    if separador_query:
        url_paginada = f"{url_paginada}?{query}"

    if separador_fragmento:
        url_paginada = f"{url_paginada}#{fragmento}"

    return url_paginada


def construir_url_pagina_casa_rica(url, pagina):
    """Construye la URL paginada que usa Casa Rica."""
    return construir_url_pagina_los_jardines(url, pagina)


def construir_url_pagina_arete(url, pagina):
    """Construye la URL paginada que usa Areté."""
    url_pagina = construir_url_pagina_los_jardines(url, pagina)
    separador = "&" if "?" in url_pagina else "?"
    return f"{url_pagina}{separador}ajax=true"


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


def _extraer_unidad_los_jardines(contenedor):
    cantidad_html = contenedor.select_one("input.inp-quantity")
    if not cantidad_html:
        return "unidad"

    unidad = normalizar_nombre_producto(cantidad_html.get("data-modo_venta"))
    return unidad.lower() if unidad else "unidad"


def _extraer_precio_dattamax(contenedor):
    boton_carrito = contenedor.select_one("a.add_to_cart_button[data-product_price]")
    if boton_carrito:
        precio_atributo = boton_carrito.get("data-product_price")
        if precio_atributo:
            precio_texto = str(precio_atributo).split(".", 1)[0]
            if limpiar_precio(precio_texto) is not None:
                return precio_texto

    for precio_html in contenedor.select("span.price span.amount"):
        precio_texto = precio_html.get_text(" ", strip=True)
        if limpiar_precio(precio_texto) is not None:
            return precio_texto

    return None


def _extraer_productos_dattamax(
    html,
    supermercado,
    categoria,
    base_url,
    obtener_unidad,
):
    soup = BeautifulSoup(html, "html.parser")
    productos = []

    for producto_html in soup.select("div.product"):
        try:
            nombre_html = producto_html.select_one(
                "h2.ecommercepro-loop-product__title"
            )
            precio_texto = _extraer_precio_dattamax(producto_html)

            if not nombre_html or precio_texto is None:
                continue

            producto = construir_producto(
                supermercado=supermercado,
                nombre=nombre_html.get_text(" ", strip=True),
                precio_texto=precio_texto,
                categoria=categoria,
                url_producto=extraer_url_producto_dattamax(producto_html, base_url),
                unidad=obtener_unidad(producto_html),
            )

            if producto:
                productos.append(producto)
        except Exception as error:
            print(f"Producto de {supermercado} omitido por error de lectura: {error}")

    return productos


def extraer_productos_los_jardines(
    html,
    categoria=None,
    url_categoria=URL_LOS_JARDINES,
):
    """Extrae productos desde el HTML de una pagina de Los Jardines."""
    return _extraer_productos_dattamax(
        html,
        supermercado="Los Jardines",
        categoria=categoria,
        base_url=URL_LOS_JARDINES,
        obtener_unidad=_extraer_unidad_los_jardines,
    )


def extraer_productos_casa_rica(
    html,
    categoria=None,
    url_categoria=URL_CASA_RICA,
):
    """Extrae productos desde el HTML de una pagina de Casa Rica."""
    return _extraer_productos_dattamax(
        html,
        supermercado="Casa Rica",
        categoria=categoria,
        base_url=URL_CASA_RICA,
        obtener_unidad=lambda _producto_html: "unidad",
    )


def _extraer_unidad_arete(contenedor):
    cantidad_html = contenedor.select_one("input.inp-quantity")
    if not cantidad_html:
        return "unidad"

    unidad = normalizar_nombre_producto(cantidad_html.get("data-modo_venta"))
    return unidad.lower() if unidad else "unidad"


def extraer_productos_arete(
    html,
    categoria=None,
    url_categoria=URL_ARETE,
):
    """Extrae productos desde el HTML de una pagina de Areté."""
    return _extraer_productos_dattamax(
        html,
        supermercado="Areté",
        categoria=categoria,
        base_url=URL_ARETE,
        obtener_unidad=_extraer_unidad_arete,
    )


def extraer_categorias_biggie(datos):
    """Extrae categorias Market desde la respuesta de la API de Biggie."""
    categorias = []

    for categoria in (datos or {}).get("items", []):
        nombre = normalizar_nombre_producto(categoria.get("name"))
        slug = normalizar_nombre_producto(categoria.get("slug"))

        if nombre and slug:
            categorias.append((slug, nombre))

    return categorias


def _precio_biggie(articulo):
    precio_oferta = articulo.get("priceSaleOffer")

    if articulo.get("isOnOffer") and precio_oferta:
        return precio_oferta

    return articulo.get("price")


def _url_producto_biggie(articulo):
    nombre = normalizar_nombre_producto(articulo.get("name"))
    codigo = normalizar_nombre_producto(articulo.get("code") or articulo.get("id"))
    slug = crear_slug(nombre)

    if codigo:
        slug = f"{slug}-{codigo}" if slug else codigo

    return urljoin(URL_BIGGIE, f"item/{slug}") if slug else None


def extraer_productos_biggie(datos, categoria=None):
    """Extrae productos desde una respuesta JSON de la API de Biggie."""
    productos = []

    for articulo in (datos or {}).get("items", []):
        try:
            familia = articulo.get("family") or {}
            clasificacion = familia.get("classification") or {}
            categoria_producto = normalizar_nombre_producto(
                clasificacion.get("name")
            ) or categoria

            producto = construir_producto(
                supermercado="Biggie",
                nombre=articulo.get("name"),
                precio_texto=_precio_biggie(articulo),
                categoria=categoria_producto,
                url_producto=_url_producto_biggie(articulo),
                unidad=normalizar_nombre_producto(
                    articulo.get("unitOfMeasure")
                ).lower()
                or "unidad",
            )

            if producto:
                productos.append(producto)
        except Exception as error:
            print(f"Producto de Biggie omitido por error de lectura: {error}")

    return productos


def descargar_html(
    sesion,
    url,
    contexto,
    intentos=REQUEST_REINTENTOS,
    pausa_reintento=PAUSA_REINTENTO,
):
    """Descarga una pagina y retorna HTML, o None si falla."""
    intentos = max(1, int(intentos or 1))
    ultimo_error = None

    for intento in range(1, intentos + 1):
        try:
            respuesta = sesion.get(url, timeout=REQUEST_TIMEOUT)
            respuesta.raise_for_status()
            return respuesta.text
        except requests.HTTPError as error:
            print(f"Error al scrapear {contexto}: {error}")
            return None
        except requests.RequestException as error:
            ultimo_error = error
            if intento < intentos:
                print(
                    f"Error temporal al scrapear {contexto} "
                    f"(intento {intento}/{intentos}): {error}"
                )
                time.sleep(pausa_reintento)
                continue

    print(f"Error al scrapear {contexto}: {ultimo_error}")
    return None


def descargar_json(
    sesion,
    url,
    contexto,
    params=None,
    intentos=REQUEST_REINTENTOS,
    pausa_reintento=PAUSA_REINTENTO,
):
    """Descarga JSON y retorna dict/list, o None si falla."""
    intentos = max(1, int(intentos or 1))
    ultimo_error = None

    for intento in range(1, intentos + 1):
        try:
            respuesta = sesion.get(url, params=params, timeout=REQUEST_TIMEOUT)
            respuesta.raise_for_status()
            return respuesta.json()
        except requests.HTTPError as error:
            print(f"Error al scrapear {contexto}: {error}")
            return None
        except ValueError as error:
            print(f"Error al leer JSON de {contexto}: {error}")
            return None
        except requests.RequestException as error:
            ultimo_error = error
            if intento < intentos:
                print(
                    f"Error temporal al scrapear {contexto} "
                    f"(intento {intento}/{intentos}): {error}"
                )
                time.sleep(pausa_reintento)
                continue

    print(f"Error al scrapear {contexto}: {ultimo_error}")
    return None


def imprimir_progreso_scraper(supermercado, categoria, pagina, total_productos):
    """Imprime avance periodico para logs de categorias extensas."""
    if pagina % INTERVALO_PROGRESO_PAGINAS != 0:
        return

    print(
        f"{supermercado} - {categoria}: pagina {pagina}, "
        f"{total_productos} productos acumulados"
    )


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
            imprimir_progreso_scraper(
                "Superseis",
                nombre_categoria,
                pagina,
                len(productos_categoria),
            )
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
                imprimir_progreso_scraper(
                    "Stock",
                    nombre_categoria,
                    pagina,
                    len(productos_categoria),
                )
                time.sleep(PAUSA_ENTRE_PAGINAS)

            todos_los_productos.extend(productos_categoria)
            print(
                f"Stock - {nombre_categoria}: {len(productos_categoria)} productos "
                f"en {paginas_con_productos} paginas"
            )

    return todos_los_productos


def scrapear_los_jardines(limite_categorias=None, limite_paginas=250):
    """Scrapea todos los productos de Los Jardines recorriendo su paginacion."""
    todos_los_productos = []
    categorias = CATEGORIAS_LOS_JARDINES

    if limite_categorias is not None:
        categorias = categorias[:limite_categorias]

    with crear_sesion() as sesion:
        for url, nombre_categoria in categorias:
            productos_categoria = []
            paginas_con_productos = 0

            for pagina in range(1, limite_paginas + 1):
                url_pagina = construir_url_pagina_los_jardines(url, pagina)
                html = descargar_html(
                    sesion,
                    url_pagina,
                    f"Los Jardines {nombre_categoria}, pagina {pagina}",
                )

                if not html:
                    break

                productos = extraer_productos_los_jardines(
                    html,
                    categoria=nombre_categoria,
                    url_categoria=url,
                )

                if not productos:
                    break

                productos_categoria.extend(productos)
                paginas_con_productos += 1
                imprimir_progreso_scraper(
                    "Los Jardines",
                    nombre_categoria,
                    pagina,
                    len(productos_categoria),
                )
                time.sleep(PAUSA_ENTRE_PAGINAS)

            todos_los_productos.extend(productos_categoria)
            print(
                f"Los Jardines - {nombre_categoria}: "
                f"{len(productos_categoria)} productos en "
                f"{paginas_con_productos} paginas"
            )

    return todos_los_productos


def scrapear_casa_rica(limite_categorias=None, limite_paginas=250):
    """Scrapea todos los productos de Casa Rica recorriendo su paginacion."""
    todos_los_productos = []
    categorias = CATEGORIAS_CASA_RICA

    if limite_categorias is not None:
        categorias = categorias[:limite_categorias]

    with crear_sesion() as sesion:
        for url, nombre_categoria in categorias:
            productos_categoria = []
            paginas_con_productos = 0

            for pagina in range(1, limite_paginas + 1):
                url_pagina = construir_url_pagina_casa_rica(url, pagina)
                html = descargar_html(
                    sesion,
                    url_pagina,
                    f"Casa Rica {nombre_categoria}, pagina {pagina}",
                )

                if not html:
                    break

                productos = extraer_productos_casa_rica(
                    html,
                    categoria=nombre_categoria,
                    url_categoria=url,
                )

                if not productos:
                    break

                productos_categoria.extend(productos)
                paginas_con_productos += 1
                imprimir_progreso_scraper(
                    "Casa Rica",
                    nombre_categoria,
                    pagina,
                    len(productos_categoria),
                )
                time.sleep(PAUSA_ENTRE_PAGINAS)

            todos_los_productos.extend(productos_categoria)
            print(
                f"Casa Rica - {nombre_categoria}: {len(productos_categoria)} productos "
                f"en {paginas_con_productos} paginas"
            )

    return todos_los_productos


def scrapear_arete(limite_categorias=None, limite_paginas=250):
    """Scrapea todos los productos de Areté recorriendo su paginacion."""
    todos_los_productos = []
    categorias = CATEGORIAS_ARETE

    if limite_categorias is not None:
        categorias = categorias[:limite_categorias]

    with crear_sesion() as sesion:
        for url, nombre_categoria in categorias:
            productos_categoria = []
            paginas_con_productos = 0

            for pagina in range(1, limite_paginas + 1):
                url_pagina = construir_url_pagina_arete(url, pagina)
                html = descargar_html(
                    sesion,
                    url_pagina,
                    f"Areté {nombre_categoria}, pagina {pagina}",
                )

                if not html:
                    break

                productos = extraer_productos_arete(
                    html,
                    categoria=nombre_categoria,
                    url_categoria=url,
                )

                if not productos:
                    break

                productos_categoria.extend(productos)
                paginas_con_productos += 1
                imprimir_progreso_scraper(
                    "Areté",
                    nombre_categoria,
                    pagina,
                    len(productos_categoria),
                )
                time.sleep(PAUSA_ENTRE_PAGINAS)

            todos_los_productos.extend(productos_categoria)
            print(
                f"Areté - {nombre_categoria}: {len(productos_categoria)} productos "
                f"en {paginas_con_productos} paginas"
            )

    return todos_los_productos


def leer_categorias_biggie(sesion):
    """Lee categorias de Biggie desde su API publica."""
    datos = descargar_json(
        sesion,
        urljoin(URL_API_BIGGIE, "classifications/web"),
        "Biggie categorias",
        params={"take": -1, "storeType": "Market"},
    )

    if not datos:
        return []

    return extraer_categorias_biggie(datos)


def scrapear_biggie(limite_categorias=None, limite_paginas=250):
    """Scrapea productos de Biggie usando su API de articulos."""
    todos_los_productos = []

    with crear_sesion() as sesion:
        categorias = leer_categorias_biggie(sesion)

        if limite_categorias is not None:
            categorias = categorias[:limite_categorias]

        for slug_categoria, nombre_categoria in categorias:
            productos_categoria = []
            paginas_con_productos = 0
            total_reportado = None

            for pagina in range(1, limite_paginas + 1):
                skip = (pagina - 1) * TAMANO_PAGINA_BIGGIE
                datos = descargar_json(
                    sesion,
                    urljoin(URL_API_BIGGIE, "articles"),
                    f"Biggie {nombre_categoria}, pagina {pagina}",
                    params={
                        "take": TAMANO_PAGINA_BIGGIE,
                        "skip": skip,
                        "classificationName": slug_categoria,
                    },
                )

                if not datos:
                    break

                total_reportado = datos.get("count", total_reportado)
                productos = extraer_productos_biggie(
                    datos,
                    categoria=nombre_categoria,
                )

                if not productos:
                    break

                productos_categoria.extend(productos)
                paginas_con_productos += 1
                imprimir_progreso_scraper(
                    "Biggie",
                    nombre_categoria,
                    pagina,
                    len(productos_categoria),
                )

                if total_reportado is not None and len(productos_categoria) >= int(
                    total_reportado
                ):
                    break

                time.sleep(PAUSA_ENTRE_PAGINAS)

            todos_los_productos.extend(productos_categoria)
            detalle_total = (
                f" de {total_reportado}" if total_reportado is not None else ""
            )
            print(
                f"Biggie - {nombre_categoria}: {len(productos_categoria)}"
                f"{detalle_total} productos en {paginas_con_productos} paginas"
            )

    return todos_los_productos
