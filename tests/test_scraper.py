from scraper import (
    construir_url_pagina_los_jardines,
    construir_producto,
    descargar_html,
    extraer_productos_los_jardines,
    limpiar_precio,
    normalizar_nombre_comparable,
    normalizar_nombre_producto,
    obtener_clave_matching_producto,
    obtener_etiqueta_matching_producto,
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


def test_normalizar_nombre_comparable_litros():
    assert normalizar_nombre_comparable("Coca-Cola 2 Litros") == "coca cola 2 L"
    assert normalizar_nombre_comparable("COCA COLA 2L") == "coca cola 2 L"
    assert normalizar_nombre_comparable("Coca Cola 2000 ml") == "coca cola 2 L"


def test_normalizar_nombre_comparable_con_acentos_y_peso():
    assert normalizar_nombre_comparable("Azúcar Orgánica 1 KG") == "azucar organica 1 kg"
    assert normalizar_nombre_comparable("Yerba mate 500 gramos") == "yerba mate 500 g"


def test_obtener_clave_matching_producto_ignora_relleno_y_orden():
    assert (
        obtener_clave_matching_producto("Gaseosa Coca Cola Original Botella 2 Litros")
        == "coca cola gaseosa original 2 L"
    )
    assert (
        obtener_clave_matching_producto("Coca-Cola sabor original gaseosa 2000ml")
        == "coca cola gaseosa original 2 L"
    )


def test_obtener_etiqueta_matching_producto_conserva_orden_legible():
    assert (
        obtener_etiqueta_matching_producto("Smart TV 55 pulgadas Dayo")
        == "smart tv 55 pulgadas dayo"
    )
    assert (
        obtener_etiqueta_matching_producto("Coca-Cola sabor original gaseosa 2000ml")
        == "coca cola original gaseosa 2 L"
    )


def test_obtener_clave_matching_producto_evita_falsos_positivos_basicos():
    assert obtener_clave_matching_producto(
        "Coca Cola Original 2L"
    ) != obtener_clave_matching_producto("Coca Cola Zero 2L")


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
