from scraper import construir_producto, limpiar_precio, normalizar_nombre_producto


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


def test_construir_producto_omite_precio_invalido():
    producto = construir_producto(
        supermercado="Stock",
        nombre="Producto valido",
        precio_texto="Precio no disponible",
    )

    assert producto is None
