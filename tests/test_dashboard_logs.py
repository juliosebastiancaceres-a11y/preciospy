from dashboard import (
    obtener_logs_scraper,
    parsear_log_scraper,
    preparar_alertas_monitoreo_corrida,
    preparar_tabla_monitoreo_corrida,
    preparar_tabla_ultima_corrida,
)


def test_parsear_log_scraper_resume_ejecucion_exitosa(tmp_path):
    ruta_log = tmp_path / "scraper-2026-05-08_06-00-00.log"
    ruta_log.write_text(
        """
PreciosPY scraper diario
Fecha: 2026-05-08 06:00:00 -03

== Stock ==
Inicio: 2026-05-08 06:00:00 -03
Productos scrapeados: 20
Productos guardados en SQLite: 5
Productos sincronizados con Supabase: 20
Fin: 2026-05-08 06:00:20 -03
Codigo de salida: 0

== Superseis ==
Inicio: 2026-05-08 06:00:20 -03
Productos scrapeados: 10
Productos guardados en SQLite: 3
Productos sincronizados con Supabase: 10
Fin: 2026-05-08 06:00:30 -03
Codigo de salida: 0

Estado final: 0
""".strip(),
        encoding="utf-8",
    )

    log = parsear_log_scraper(ruta_log)

    assert log["archivo"] == "scraper-2026-05-08_06-00-00.log"
    assert log["estado"] == "OK (0)"
    assert log["scrapeados"] == 30
    assert log["sqlite"] == 8
    assert log["supabase"] == 30
    assert log["errores"] == 0
    assert log["ultimo_error"] == "Sin errores"
    assert log["ok"] is True
    assert len(log["secciones"]) == 2
    assert log["secciones"][0]["nombre"] == "Stock"
    assert log["secciones"][0]["scrapeados"] == 20
    assert log["secciones"][0]["sqlite"] == 5
    assert log["secciones"][0]["supabase"] == 20
    assert log["secciones"][0]["estado"] == "OK"
    assert log["secciones"][0]["duracion"] == "20 s"
    assert log["secciones"][0]["duracion_segundos"] == 20

    tabla = preparar_tabla_ultima_corrida(log)

    assert tabla["Paso"].tolist() == ["Stock", "Superseis"]
    assert tabla.loc[0, "Scrapeados"] == 20
    assert tabla.loc[1, "SQLite"] == 3
    assert tabla.loc[1, "Duración"] == "10 s"

    tabla_monitoreo = preparar_tabla_monitoreo_corrida(log)

    assert tabla_monitoreo.columns.tolist() == [
        "Paso",
        "Estado",
        "Scrapeados",
        "Sincronizados",
        "Reparados",
        "Duración",
        "Avisos",
        "Pendientes",
    ]
    assert tabla_monitoreo["Estado"].tolist() == ["OK", "OK"]

    alertas = preparar_alertas_monitoreo_corrida(log)

    assert alertas == [
        {
            "nivel": "success",
            "titulo": "Última corrida sin alertas",
            "detalle": "Todos los pasos terminaron dentro de los valores esperados.",
        }
    ]


def test_parsear_log_scraper_detecta_error(tmp_path):
    ruta_log = tmp_path / "scraper-2026-05-08_07-00-00.log"
    ruta_log.write_text(
        """
PreciosPY scraper diario
Fecha: 2026-05-08 07:00:00 -03
Inicio: 2026-05-08 07:00:00 -03
Error al scrapear Stock: 403 Client Error: Forbidden
Productos scrapeados: 0
Productos sincronizados con Supabase: 0
Fin: 2026-05-08 07:00:05 -03
Codigo de salida: 1
Estado final: 1
""".strip(),
        encoding="utf-8",
    )

    log = parsear_log_scraper(ruta_log)

    assert log["estado"] == "Error (1)"
    assert log["errores"] == 1
    assert "403 Client Error" in log["ultimo_error"]
    assert log["ok"] is False


def test_parsear_log_scraper_no_muestra_error_recuperado_como_fallo(tmp_path):
    ruta_log = tmp_path / "scraper-2026-05-13_11-10-22.log"
    ruta_log.write_text(
        """
PreciosPY scraper diario
Fecha: 2026-05-13 11:10:22 -03
Inicio: 2026-05-13 11:10:22 -03
Error al sincronizar lote en Supabase: APIError
Productos sincronizados con Supabase: 200
Fin: 2026-05-13 11:11:24 -03
Codigo de salida: 0
Inicio: 2026-05-13 11:12:00 -03
Historicos enviados a Supabase: 233
Fin: 2026-05-13 11:12:13 -03
Codigo de salida: 0
Estado final: 0
""".strip(),
        encoding="utf-8",
    )

    log = parsear_log_scraper(ruta_log)

    assert log["estado"] == "OK (0)"
    assert log["errores"] == 0
    assert log["advertencias"] == 1
    assert log["ultimo_error"] == "Sin errores críticos (1 aviso(s) recuperados)"
    assert log["ok"] is True


def test_parsear_log_scraper_marca_sync_final_con_reparacion(tmp_path):
    ruta_log = tmp_path / "scraper-2026-05-22_08-12-37.log"
    ruta_log.write_text(
        """
PreciosPY scraper diario
Fecha: 2026-05-22 08:12:37 -03

== Sincronizar faltantes SQLite -> Supabase ==
Inicio: 2026-05-22 08:47:49 -03
Registros validos en SQLite: 332780
Claves existentes en Supabase: 208018
Registros faltantes detectados: 127095
Productos sincronizados con Supabase: 127095
Historicos enviados a Supabase: 127095
Fin: 2026-05-22 09:00:45 -03
Codigo de salida: 0

Estado final: 0
""".strip(),
        encoding="utf-8",
    )

    log = parsear_log_scraper(ruta_log)
    tabla = preparar_tabla_monitoreo_corrida(log)
    alertas = preparar_alertas_monitoreo_corrida(log)

    assert tabla.loc[0, "Paso"] == "Sync final"
    assert tabla.loc[0, "Estado"] == "OK con reparación"
    assert tabla.loc[0, "Reparados"] == 127095
    assert tabla.loc[0, "Pendientes"] == 127095
    assert alertas == [
        {
            "nivel": "warning",
            "titulo": "Sync final reparó Supabase",
            "detalle": "Se enviaron 127095 histórico(s) faltante(s) después del scrapeo.",
        }
    ]


def test_parsear_log_scraper_resume_avisos_por_supermercado(tmp_path):
    ruta_log = tmp_path / "scraper-2026-05-15_10-11-31.log"
    ruta_log.write_text(
        """
PreciosPY scraper diario
Fecha: 2026-05-15 10:11:31 -03

== Casa Rica ==
Inicio: 2026-05-15 10:42:00 -03
Error temporal al scrapear Casa Rica Bebidas, pagina 3: fallo de conexion
Productos scrapeados: 10496
Productos guardados en SQLite: 10472
Productos duplicados omitidos antes de Supabase: 24
Productos sincronizados con Supabase: 10472
Fin: 2026-05-15 11:03:00 -03
Codigo de salida: 0

== Sincronizar faltantes SQLite -> Supabase ==
Inicio: 2026-05-15 11:04:00 -03
Registros validos en SQLite: 81997
Claves existentes en Supabase: 86586
Registros faltantes detectados: 0
Fin: 2026-05-15 11:05:00 -03
Codigo de salida: 0

Estado final: 0
""".strip(),
        encoding="utf-8",
    )

    log = parsear_log_scraper(ruta_log)
    casa_rica = log["secciones"][0]
    sync_final = log["secciones"][1]

    assert casa_rica["estado"] == "OK"
    assert casa_rica["advertencias"] == 1
    assert casa_rica["errores"] == 0
    assert casa_rica["duplicados"] == 24
    assert sync_final["nombre"] == "Sincronizar faltantes SQLite -> Supabase"
    assert sync_final["sqlite_revisados"] == 81997
    assert sync_final["supabase_existentes"] == 86586
    assert sync_final["faltantes"] == 0

    tabla_monitoreo = preparar_tabla_monitoreo_corrida(log)

    assert tabla_monitoreo.loc[0, "Estado"] == "OK con avisos"
    assert tabla_monitoreo.loc[0, "Duración"] == "21 min 0 s"
    assert tabla_monitoreo.loc[1, "Paso"] == "Sync final"
    assert tabla_monitoreo.loc[1, "Sincronizados"] == 81997
    assert tabla_monitoreo.loc[1, "Duración"] == "1 min 0 s"

    alertas = preparar_alertas_monitoreo_corrida(log)

    assert len(alertas) == 1
    assert alertas[0]["nivel"] == "warning"
    assert alertas[0]["titulo"] == "Casa Rica terminó con avisos"


def test_preparar_alertas_monitoreo_corrida_detecta_ceros_y_lentitud(tmp_path):
    ruta_log = tmp_path / "scraper-2026-05-16_06-00-00.log"
    ruta_log.write_text(
        """
PreciosPY scraper diario
Fecha: 2026-05-16 06:00:00 -03

== Stock ==
Inicio: 2026-05-16 06:00:00 -03
Productos scrapeados: 0
Productos guardados en SQLite: 0
Productos sincronizados con Supabase: 0
Fin: 2026-05-16 06:00:20 -03
Codigo de salida: 0

== Biggie ==
Inicio: 2026-05-16 06:00:20 -03
Productos scrapeados: 100
Productos guardados en SQLite: 100
Productos sincronizados con Supabase: 100
Fin: 2026-05-16 07:30:20 -03
Codigo de salida: 0

Estado final: 0
""".strip(),
        encoding="utf-8",
    )

    log = parsear_log_scraper(ruta_log)
    alertas = preparar_alertas_monitoreo_corrida(log)

    titulos = [alerta["titulo"] for alerta in alertas]

    assert "Stock no trajo productos" in titulos
    assert "Biggie tardó más de lo esperado" in titulos


def test_parsear_log_scraper_no_marca_error_en_seccion_en_curso(tmp_path):
    ruta_log = tmp_path / "scraper-2026-05-16_10-50-00.log"
    ruta_log.write_text(
        """
PreciosPY scraper diario
Fecha: 2026-05-16 10:50:00 -03

== Los Jardines ==
Inicio: 2026-05-16 10:51:40 -03
Productos scrapeados: 6114
Productos guardados en SQLite: 6095
Productos sincronizados con Supabase: 6095
Fin: 2026-05-16 11:01:49 -03
Codigo de salida: 0

== Casa Rica ==
Inicio: 2026-05-16 11:01:49 -03
Error temporal al scrapear Casa Rica Bebidas, pagina 4 (intento 1/3): conexion
Casa Rica - Almacen: 1338 productos en 67 paginas
""".strip(),
        encoding="utf-8",
    )

    log = parsear_log_scraper(ruta_log)
    tabla = preparar_tabla_monitoreo_corrida(log)
    alertas = preparar_alertas_monitoreo_corrida(log)

    assert log["estado"] == "En curso"
    assert tabla.loc[0, "Paso"] == "Los Jardines"
    assert tabla.loc[0, "Estado"] == "OK"
    assert tabla.loc[1, "Paso"] == "Casa Rica"
    assert tabla.loc[1, "Estado"] == "En curso"
    assert alertas == [
        {
            "nivel": "info",
            "titulo": "Casa Rica está en curso",
            "detalle": "La corrida diaria todavía no terminó.",
        }
    ]


def test_obtener_logs_scraper_respeta_limite(tmp_path, monkeypatch):
    for indice in range(3):
        ruta_log = tmp_path / f"scraper-2026-05-08_0{indice}-00-00.log"
        ruta_log.write_text(
            f"Fecha: 2026-05-08 0{indice}:00:00 -03\nEstado final: 0",
            encoding="utf-8",
        )

    monkeypatch.setattr("dashboard.RUTA_LOGS", tmp_path)

    logs = obtener_logs_scraper(limite=2)

    assert len(logs) == 2
    assert logs[0]["archivo"] == "scraper-2026-05-08_02-00-00.log"
