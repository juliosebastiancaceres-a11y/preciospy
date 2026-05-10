from scraper import (
    construir_producto,
    descargar_html,
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
