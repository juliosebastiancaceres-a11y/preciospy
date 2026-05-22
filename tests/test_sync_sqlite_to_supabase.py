from database import deduplicar_productos_por_clave
from scripts.sync_sqlite_to_supabase import (
    cargar_claves_supabase,
    clave_producto,
    detectar_faltantes,
    main,
    sincronizar_faltantes,
    verificar_sync_final,
)


def test_clave_producto_usa_clave_natural():
    producto = {
        "supermercado": " Stock ",
        "nombre_producto": " Arroz 1kg ",
        "fecha_registro": "2026-05-08",
        "precio": 10000,
    }

    assert clave_producto(producto) == ("Stock", "Arroz 1kg", "2026-05-08")


def test_detectar_faltantes_omite_existentes_y_duplicados():
    productos = [
        {
            "supermercado": "Stock",
            "nombre_producto": "Arroz 1kg",
            "fecha_registro": "2026-05-08",
        },
        {
            "supermercado": "Stock",
            "nombre_producto": "Aceite 900ml",
            "fecha_registro": "2026-05-08",
        },
        {
            "supermercado": "Stock",
            "nombre_producto": "Aceite 900ml",
            "fecha_registro": "2026-05-08",
        },
    ]
    claves_supabase = {("Stock", "Arroz 1kg", "2026-05-08")}

    faltantes = detectar_faltantes(productos, claves_supabase)

    assert faltantes == [productos[1]]


def test_detectar_faltantes_respeta_limite():
    productos = [
        {
            "supermercado": "Stock",
            "nombre_producto": "Producto A",
            "fecha_registro": "2026-05-08",
        },
        {
            "supermercado": "Stock",
            "nombre_producto": "Producto B",
            "fecha_registro": "2026-05-08",
        },
    ]

    faltantes = detectar_faltantes(productos, set(), limite=1)

    assert faltantes == [productos[0]]


def test_cargar_claves_supabase_pagina_con_orden_estable(monkeypatch):
    class Respuesta:
        def __init__(self, data):
            self.data = data

    class Query:
        def __init__(self, lotes, llamadas):
            self.lotes = lotes
            self.llamadas = llamadas
            self.rango = None

        def select(self, columnas):
            self.llamadas.append(("select", columnas))
            return self

        def order(self, columna):
            self.llamadas.append(("order", columna))
            return self

        def range(self, inicio, fin):
            self.rango = (inicio, fin)
            self.llamadas.append(("range", inicio, fin))
            return self

        def execute(self):
            indice = self.rango[0] // 2
            return Respuesta(self.lotes[indice])

    class SupabaseFake:
        def __init__(self):
            self.llamadas = []
            self.lotes = [
                [
                    {
                        "supermercado": "Stock",
                        "nombre_producto": "Arroz",
                        "fecha_registro": "2026-05-22",
                    },
                    {
                        "supermercado": "Superseis",
                        "nombre_producto": "Aceite",
                        "fecha_registro": "2026-05-22",
                    },
                ],
                [
                    {
                        "supermercado": "Biggie",
                        "nombre_producto": "Leche",
                        "fecha_registro": "2026-05-22",
                    }
                ],
            ]

        def table(self, nombre):
            self.llamadas.append(("table", nombre))
            return Query(self.lotes, self.llamadas)

    monkeypatch.setattr("scripts.sync_sqlite_to_supabase.TAMANO_LOTE_LECTURA", 2)
    supabase = SupabaseFake()

    claves = cargar_claves_supabase(supabase)

    assert claves == {
        ("Stock", "Arroz", "2026-05-22"),
        ("Superseis", "Aceite", "2026-05-22"),
        ("Biggie", "Leche", "2026-05-22"),
    }
    assert ("order", "id") in supabase.llamadas
    assert supabase.llamadas.index(("order", "id")) < supabase.llamadas.index(
        ("range", 0, 1)
    )


def test_deduplicar_productos_por_clave_conserva_ultimo_registro():
    productos = [
        {
            "supermercado": "Stock",
            "nombre_producto": "Aceite 900ml",
            "fecha_registro": "2026-05-13",
            "precio": 10000,
        },
        {
            "supermercado": "Stock",
            "nombre_producto": "Aceite 900ml",
            "fecha_registro": "2026-05-13",
            "precio": 10500,
        },
        {
            "supermercado": "Superseis",
            "nombre_producto": "Aceite 900ml",
            "fecha_registro": "2026-05-13",
            "precio": 11000,
        },
    ]

    deduplicados = deduplicar_productos_por_clave(productos)

    assert deduplicados == [productos[1], productos[2]]


def test_sincronizar_faltantes_modo_revision_no_envia(monkeypatch):
    llamados = []

    monkeypatch.setattr(
        "scripts.sync_sqlite_to_supabase.guardar_en_supabase",
        lambda productos: llamados.append(productos),
    )

    sincronizados = sincronizar_faltantes([{"nombre_producto": "A"}], aplicar=False)

    assert sincronizados == 0
    assert llamados == []


def test_sincronizar_faltantes_apply_envia(monkeypatch):
    monkeypatch.setattr(
        "scripts.sync_sqlite_to_supabase.guardar_en_supabase",
        lambda productos: len(productos),
    )

    sincronizados = sincronizar_faltantes(
        [{"nombre_producto": "A"}, {"nombre_producto": "B"}],
        aplicar=True,
    )

    assert sincronizados == 2

def test_cargar_claves_supabase_muestra_progreso(monkeypatch, capsys):
    class Respuesta:
        def __init__(self, data):
            self.data = data

    class Query:
        def __init__(self, lotes):
            self.lotes = lotes
            self.rango = None

        def select(self, columnas):
            return self

        def order(self, columna):
            return self

        def range(self, inicio, fin):
            self.rango = (inicio, fin)
            return self

        def execute(self):
            indice = self.rango[0]
            return Respuesta(self.lotes[indice])

    class SupabaseFake:
        def __init__(self):
            self.lotes = [
                [
                    {
                        "supermercado": "Stock",
                        "nombre_producto": "Arroz",
                        "fecha_registro": "2026-05-22",
                    }
                ],
                [],
            ]

        def table(self, nombre):
            return Query(self.lotes)

    monkeypatch.setattr("scripts.sync_sqlite_to_supabase.TAMANO_LOTE_LECTURA", 1)
    monkeypatch.setattr(
        "scripts.sync_sqlite_to_supabase.INTERVALO_PROGRESO_SUPABASE_PAGINAS",
        1,
    )

    cargar_claves_supabase(SupabaseFake())

    salida = capsys.readouterr().out
    assert "Supabase claves: pagina 1, 1 claves acumuladas" in salida
    assert "Paginas Supabase leidas: 1" in salida


def test_detectar_faltantes_muestra_progreso(monkeypatch, capsys):
    productos = [
        {
            "supermercado": "Stock",
            "nombre_producto": "Producto A",
            "fecha_registro": "2026-05-22",
        },
        {
            "supermercado": "Stock",
            "nombre_producto": "Producto B",
            "fecha_registro": "2026-05-22",
        },
    ]
    monkeypatch.setattr("scripts.sync_sqlite_to_supabase.INTERVALO_PROGRESO_SQLITE", 1)

    detectar_faltantes(productos, set())

    salida = capsys.readouterr().out
    assert "SQLite revisados: 1; faltantes acumulados: 1" in salida
    assert "SQLite revisados: 2; faltantes acumulados: 2" in salida


def test_sincronizar_faltantes_apply_muestra_lotes(monkeypatch, capsys):
    monkeypatch.setattr(
        "scripts.sync_sqlite_to_supabase.guardar_en_supabase",
        lambda productos: len(productos),
    )

    sincronizados = sincronizar_faltantes(
        [{"nombre_producto": "A"}, {"nombre_producto": "B"}],
        aplicar=True,
    )

    salida = capsys.readouterr().out
    assert sincronizados == 2
    assert "Lotes a enviar a Supabase: 1 de hasta" in salida
    assert "Historicos enviados a Supabase: 2" in salida


def test_verificar_sync_final_confirma_sin_faltantes(monkeypatch, capsys):
    productos = [
        {
            "supermercado": "Stock",
            "nombre_producto": "Arroz",
            "fecha_registro": "2026-05-22",
            "precio": 10000,
        }
    ]
    claves = {("Stock", "Arroz", "2026-05-22")}
    monkeypatch.setattr(
        "scripts.sync_sqlite_to_supabase.cargar_claves_supabase",
        lambda supabase: claves,
    )

    pendientes = verificar_sync_final(productos, object())

    salida = capsys.readouterr().out
    assert pendientes == 0
    assert "Pendientes finales: 0" in salida
    assert "Supabase verificado: sin faltantes." in salida


def test_verificar_sync_final_omite_validacion_con_limite(capsys):
    pendientes = verificar_sync_final([], object(), limite=5)

    salida = capsys.readouterr().out
    assert pendientes is None
    assert "Validacion final omitida por --limite" in salida


def test_main_devuelve_error_si_quedan_pendientes(monkeypatch, tmp_path):
    db = tmp_path / "preciospy.db"
    db.write_text("base ficticia")
    productos = [
        {
            "supermercado": "Stock",
            "nombre_producto": "Arroz",
            "fecha_registro": "2026-05-22",
            "precio": 10000,
        }
    ]

    monkeypatch.setattr(
        "sys.argv",
        ["sync_sqlite_to_supabase.py", "--apply", "--db", str(db)],
    )
    monkeypatch.setattr(
        "scripts.sync_sqlite_to_supabase.cargar_productos_sqlite",
        lambda ruta: productos,
    )
    monkeypatch.setattr(
        "scripts.sync_sqlite_to_supabase.inicializar_supabase",
        lambda: object(),
    )
    monkeypatch.setattr(
        "scripts.sync_sqlite_to_supabase.cargar_claves_supabase",
        lambda supabase: set(),
    )
    monkeypatch.setattr(
        "scripts.sync_sqlite_to_supabase.guardar_en_supabase",
        lambda faltantes: len(faltantes),
    )
    monkeypatch.setattr(
        "scripts.sync_sqlite_to_supabase.verificar_sync_final",
        lambda productos_sqlite, supabase, limite=None: 1,
    )

    assert main() == 2

