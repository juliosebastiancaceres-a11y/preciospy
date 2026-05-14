from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import re
import time
import unicodedata

import requests
from bs4 import BeautifulSoup


URL_SUPERSEIS = "https://www.superseis.com.py/"
URL_STOCK = "https://www.stock.com.py/"
URL_LOS_JARDINES = "https://www.losjardinesonline.com.py/"
URL_CASA_RICA = "https://www.casarica.com.py/"
REQUEST_TIMEOUT = 20
REQUEST_REINTENTOS = 3
PAUSA_ENTRE_PAGINAS = 1
PAUSA_REINTENTO = 5
INTERVALO_PROGRESO_PAGINAS = 25
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


def _formatear_numero_unidad(numero):
    if numero is None:
        return None

    if numero.is_integer():
        return str(int(numero))

    return f"{numero:g}"


def _normalizar_token_matching(token):
    sinonimos = {
        "choc": "chocolate",
        "choco": "chocolate",
        "clasica": "clasico",
        "clasicos": "clasico",
        "originales": "original",
        "ret": "retornable",
        "desc": "descartable",
        "descart": "descartable",
    }
    return sinonimos.get(token, token)


def _extraer_tokens_matching(nombre):
    nombre_comparable = normalizar_nombre_comparable(nombre)

    if not nombre_comparable:
        return [], []

    tokens = nombre_comparable.split()
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

        token = _normalizar_token_matching(token)
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
    tokens = texto.split()

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
            if numero >= 1000 and numero % 1000 == 0:
                tokens_normalizados.extend(
                    [_formatear_numero_unidad(numero / 1000), "L"]
                )
            else:
                tokens_normalizados.extend([_formatear_numero_unidad(numero), "ml"])
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
                url_producto=extraer_url_producto(producto_html, base_url),
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
