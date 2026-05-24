from scraper import (
    crear_slug,
    construir_url_pagina_arete,
    construir_url_pagina_casa_rica,
    construir_url_pagina_los_jardines,
    construir_producto,
    descargar_html,
    extraer_categorias_biggie,
    extraer_productos_arete,
    extraer_productos_biggie,
    extraer_productos_casa_rica,
    extraer_productos_los_jardines,
    imprimir_progreso_scraper,
    leer_entero_entorno,
    leer_float_entorno,
    limpiar_precio,
    normalizar_nombre_comparable,
    normalizar_nombre_producto,
    obtener_clave_matching_producto,
    obtener_etiqueta_matching_producto,
    obtener_presentacion_matching_producto,
)
import requests


def test_limpiar_precio_valores_validos():
    assert limpiar_precio("₲ 12.500") == 12500
    assert limpiar_precio("Gs. 12.500") == 12500
    assert limpiar_precio("12.500") == 12500
    assert limpiar_precio("12 500") == 12500


def test_limpiar_precio_valores_invalidos():
    assert limpiar_precio("Precio no disponible") is None
    assert limpiar_precio("") is None
    assert limpiar_precio(None) is None


def test_normalizar_nombre_producto():
    assert normalizar_nombre_producto("  Arroz   tipo 1  ") == "Arroz tipo 1"
    assert normalizar_nombre_producto(None) == ""


def test_crear_slug():
    assert crear_slug("Lácteos y Bebidas 1 L") == "lacteos-y-bebidas-1-l"


def test_normalizar_nombre_comparable_litros():
    assert normalizar_nombre_comparable("Coca-Cola 2 Litros") == "coca cola 2 L"
    assert normalizar_nombre_comparable("COCA COLA 2L") == "coca cola 2 L"
    assert normalizar_nombre_comparable("Coca Cola 2000 ml") == "coca cola 2 L"
    assert (
        normalizar_nombre_comparable("Aceite de Girasol Natura de 1.500 ml.")
        == "aceite de girasol natura de 1.5 L"
    )


def test_normalizar_nombre_comparable_abreviaturas_comerciales():
    assert (
        normalizar_nombre_comparable("GASEOSA S/AZUC 1LT COCA-COLA")
        == "gaseosa sin azucar 1 L coca cola"
    )
    assert (
        normalizar_nombre_comparable("Coca Cola Zero 1 Litro")
        == "coca cola sin azucar 1 L"
    )
    assert (
        normalizar_nombre_comparable("Coca Cola RET 2L")
        == "coca cola retornable 2 L"
    )
    assert (
        normalizar_nombre_comparable("Pack Coca Cola x4 1L")
        == "coca cola 4 unidades 1 L"
    )
    assert (
        normalizar_nombre_comparable("Coca Cola 4U 1L")
        == "coca cola 4 unidades 1 L"
    )


def test_normalizar_nombre_comparable_con_acentos_y_peso():
    assert normalizar_nombre_comparable("Azúcar Orgánica 1 KG") == "azucar organica 1 kg"
    assert normalizar_nombre_comparable("Yerba mate 500 gramos") == "yerba mate 500 g"
    assert normalizar_nombre_comparable("Yerba mate 1000 gramos") == "yerba mate 1 kg"
    assert normalizar_nombre_comparable("Queso 0,5 kg") == "queso 500 g"


def test_normalizar_nombre_comparable_unifica_presentaciones_equivalentes():
    assert normalizar_nombre_comparable("Agua mineral 0,5 L") == "agua mineral 500 ml"
    assert normalizar_nombre_comparable("Agua mineral 500 ml") == "agua mineral 500 ml"
    assert (
        obtener_clave_matching_producto("Harina 1000 gr")
        == obtener_clave_matching_producto("Harina 1 kg")
    )
    assert obtener_presentacion_matching_producto("Pack Coca Cola x4 1L") == (
        "4 unidades + 1 L"
    )


def test_obtener_clave_matching_producto_ignora_relleno_y_orden():
    assert (
        obtener_clave_matching_producto("Gaseosa Coca Cola Original Botella 2 Litros")
        == "coca cola original 2 L"
    )
    assert (
        obtener_clave_matching_producto("Coca-Cola sabor original gaseosa 2000ml")
        == "coca cola original 2 L"
    )


def test_obtener_etiqueta_matching_producto_conserva_orden_legible():
    assert (
        obtener_etiqueta_matching_producto("Smart TV 55 pulgadas Dayo")
        == "smart tv 55 pulgadas dayo"
    )
    assert (
        obtener_etiqueta_matching_producto("Coca-Cola sabor original gaseosa 2000ml")
        == "coca cola original 2 L"
    )


def test_obtener_clave_matching_producto_evita_falsos_positivos_basicos():
    assert obtener_clave_matching_producto(
        "Coca Cola Original 2L"
    ) != obtener_clave_matching_producto("Coca Cola Zero 2L")


def test_obtener_clave_matching_producto_unifica_sin_azucar():
    assert (
        obtener_clave_matching_producto("GASEOSA S/AZUC 1LT COCA-COLA")
        == obtener_clave_matching_producto("Coca Cola sin azúcar 1 litro")
        == obtener_clave_matching_producto("Coca Cola Zero 1L")
    )


def test_obtener_clave_matching_producto_unifica_retornable():
    assert obtener_clave_matching_producto(
        "Gaseosa Coca Cola RET 2L"
    ) == obtener_clave_matching_producto("Coca Cola retornable 2 litros")


def test_obtener_clave_matching_producto_unifica_pack():
    assert obtener_clave_matching_producto(
        "Pack Coca Cola x4 1L"
    ) == obtener_clave_matching_producto("Coca Cola 4 unidades 1 litro")


def test_construir_producto_omite_precio_invalido():
    producto = construir_producto(
        supermercado="Stock",
        nombre="Producto valido",
        precio_texto="Precio no disponible",
    )

    assert producto is None


def test_construir_producto_agrega_nombre_normalizado():
    producto = construir_producto(
        supermercado="Stock",
        nombre="Coca-Cola 2 Litros",
        precio_texto="₲ 12.500",
    )

    assert producto["nombre_producto"] == "Coca-Cola 2 Litros"
    assert producto["nombre_normalizado"] == "coca cola 2 L"


def test_construir_url_pagina_los_jardines():
    url = "https://www.losjardinesonline.com.py/catalogo/almacen-c2"

    assert construir_url_pagina_los_jardines(url, 1) == url
    assert (
        construir_url_pagina_los_jardines(url, 2)
        == "https://www.losjardinesonline.com.py/catalogo/almacen-c2.2"
    )


def test_construir_url_pagina_casa_rica():
    url = "https://www.casarica.com.py/catalogo/almacen-c1"

    assert construir_url_pagina_casa_rica(url, 1) == url
    assert (
        construir_url_pagina_casa_rica(url, 2)
        == "https://www.casarica.com.py/catalogo/almacen-c1.2"
    )


def test_extraer_productos_los_jardines_desde_html():
    html = """
    <div class="product">
        <a href="arroz-sun-tipo-ii-azul-1-k-p12657"></a>
        <span class="price">
            <ins><span class="amount"></span></ins>
            <span class="amount">₲. 6.550</span>
        </span>
        <h2 class="ecommercepro-loop-product__title">ARROZ SUN TIPO II AZUL 1 K</h2>
        <input class="inp-quantity" data-modo_venta="Unidad">
        <a class="button add_to_cart_button"
           data-product_id="12657"
           data-product_ean="7841056000353"
           data-product_name="ARROZ SUN TIPO II AZUL 1 K"
           data-product_category="Almacén"
           data-product_price="6550.00"
           href="javascript:void(0);">Agregar al carrito</a>
    </div>
    """

    productos = extraer_productos_los_jardines(
        html,
        categoria="Almacen",
        url_categoria="https://www.losjardinesonline.com.py/catalogo/almacen-c2",
    )

    assert len(productos) == 1
    assert productos[0]["supermercado"] == "Los Jardines"
    assert productos[0]["nombre_producto"] == "ARROZ SUN TIPO II AZUL 1 K"
    assert productos[0]["precio"] == 6550
    assert productos[0]["categoria"] == "Almacen"
    assert productos[0]["unidad"] == "unidad"
    assert (
        productos[0]["url_producto"]
        == "https://www.losjardinesonline.com.py/arroz-sun-tipo-ii-azul-1-k-p12657"
    )


def test_extraer_productos_casa_rica_desde_html():
    html = """
    <div class="product">
        <a href="aceite-de-oliva-huasco-extra-virgen-500ml-p34561"></a>
        <span class="price">
            <ins><span class="amount"></span></ins>
            <span class="amount">₲. 80.000</span>
        </span>
        <h2 class="ecommercepro-loop-product__title">
            ACEITE DE OLIVA HUASCO EXTRA VIRGEN 500ML
        </h2>
        <a class="button add_to_cart_button"
           data-product_id="34561"
           href="javascript:void(0);">Agregar al carrito</a>
    </div>
    """

    productos = extraer_productos_casa_rica(
        html,
        categoria="Almacen",
        url_categoria="https://www.casarica.com.py/catalogo/almacen-c1",
    )

    assert len(productos) == 1
    assert productos[0]["supermercado"] == "Casa Rica"
    assert (
        productos[0]["nombre_producto"]
        == "ACEITE DE OLIVA HUASCO EXTRA VIRGEN 500ML"
    )
    assert productos[0]["precio"] == 80000
    assert productos[0]["categoria"] == "Almacen"
    assert productos[0]["unidad"] == "unidad"
    assert (
        productos[0]["url_producto"]
        == "https://www.casarica.com.py/aceite-de-oliva-huasco-extra-virgen-500ml-p34561"
    )


def test_extraer_productos_arete_desde_html():
    html = """
    <div class="product">
        <a class="ecommercepro-LoopProduct-link"
           href="aceituna-nucete-desc-premium-180-24-p127192">
            <span class="price">
                <ins><span class="amount"></span></ins>
                <span class="amount">₲. 28.500</span>
            </span>
            <h2 class="ecommercepro-loop-product__title">
                ACEITUNA NUCETE DESC/PREMIUM 180*24
            </h2>
        </a>
        <input class="inp-quantity" data-modo_venta="Unidad" />
    </div>
    """

    productos = extraer_productos_arete(
        html,
        categoria="Almacen",
        url_categoria="https://www.arete.com.py/catalogo/almacen-c273",
    )

    assert len(productos) == 1
    assert productos[0]["supermercado"] == "Areté"
    assert productos[0]["nombre_producto"] == "ACEITUNA NUCETE DESC/PREMIUM 180*24"
    assert productos[0]["precio"] == 28500
    assert productos[0]["categoria"] == "Almacen"
    assert productos[0]["unidad"] == "unidad"
    assert (
        productos[0]["url_producto"]
        == "https://www.arete.com.py/aceituna-nucete-desc-premium-180-24-p127192"
    )


def test_construir_url_pagina_arete_usa_sufijo_de_catalogo():
    url = "https://www.arete.com.py/catalogo/almacen-c273"

    assert construir_url_pagina_arete(url, 1) == f"{url}?ajax=true"
    assert construir_url_pagina_arete(url, 2) == f"{url}.2?ajax=true"


def test_extraer_categorias_biggie_desde_json():
    datos = {
        "items": [
            {"name": " Almacén   ", "slug": "almacen"},
            {"name": "", "slug": "sin-nombre"},
            {"name": "Bebidas", "slug": ""},
        ]
    }

    assert extraer_categorias_biggie(datos) == [("almacen", "Almacén")]


def test_extraer_productos_biggie_desde_json():
    datos = {
        "items": [
            {
                "id": "abc",
                "code": "7840061000051",
                "name": "Huevos Yemita Tipo A de 30 Unidades.",
                "price": 36500,
                "priceSaleOffer": 32000,
                "isOnOffer": True,
                "unitOfMeasure": "Unidades",
                "family": {
                    "classification": {
                        "name": "Almacén                                ",
                    }
                },
            }
        ],
        "count": 1,
    }

    productos = extraer_productos_biggie(datos, categoria="Almacen")

    assert len(productos) == 1
    assert productos[0]["supermercado"] == "Biggie"
    assert productos[0]["nombre_producto"] == "Huevos Yemita Tipo A de 30 Unidades."
    assert productos[0]["precio"] == 32000
    assert productos[0]["categoria"] == "Almacén"
    assert productos[0]["unidad"] == "unidades"
    assert (
        productos[0]["url_producto"]
        == "https://www.biggie.com.py/item/huevos-yemita-tipo-a-de-30-unidades-7840061000051"
    )


def test_imprimir_progreso_scraper_respeta_intervalo(capsys):
    imprimir_progreso_scraper("Los Jardines", "Almacen", 24, 480)
    assert capsys.readouterr().out == ""

    imprimir_progreso_scraper("Los Jardines", "Almacen", 25, 500)
    salida = capsys.readouterr().out

    assert "Los Jardines - Almacen: pagina 25" in salida
    assert "500 productos acumulados" in salida


class RespuestaFake:
    text = "<html>ok</html>"

    def raise_for_status(self):
        return None


class SesionIntermitente:
    def __init__(self):
        self.intentos = 0

    def get(self, url, timeout):
        self.intentos += 1

        if self.intentos == 1:
            raise requests.ConnectionError("conexion reiniciada")

        return RespuestaFake()


def test_descargar_html_reintenta_errores_temporales():
    sesion = SesionIntermitente()

    html = descargar_html(
        sesion,
        "https://example.com",
        "Prueba",
        intentos=2,
        pausa_reintento=0,
    )

    assert html == "<html>ok</html>"
    assert sesion.intentos == 2


def test_leer_entorno_numerico_usa_defecto_si_es_invalido(monkeypatch):
    monkeypatch.setenv("PRECIOSPY_TEST_ENTERO", "abc")
    monkeypatch.setenv("PRECIOSPY_TEST_FLOAT", "abc")

    assert leer_entero_entorno("PRECIOSPY_TEST_ENTERO", 25) == 25
    assert leer_float_entorno("PRECIOSPY_TEST_FLOAT", 0.2) == 0.2


def test_leer_entorno_numerico_parsea_valores(monkeypatch):
    monkeypatch.setenv("PRECIOSPY_TEST_ENTERO", "50")
    monkeypatch.setenv("PRECIOSPY_TEST_FLOAT", "0.25")

    assert leer_entero_entorno("PRECIOSPY_TEST_ENTERO", 25) == 50
    assert leer_float_entorno("PRECIOSPY_TEST_FLOAT", 1) == 0.25
