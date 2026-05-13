from dashboard import obtener_logs_scraper, parsear_log_scraper


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
