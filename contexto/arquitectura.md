# Arquitectura resumida

Entradas principales:

- `main.py`: CLI para ejecutar scrapers por supermercado.
- `scraper/__init__.py`: scrapers y normalizacion de nombres/productos.
- `database/__init__.py`: SQLite, Supabase, deduplicacion y persistencia.
- `dashboard.py`: dashboard Streamlit, filtros, graficos, monitoreo, comparacion y exportacion.
- `scripts/run_daily_scraper.sh`: corrida diaria por systemd.
- `scripts/sync_sqlite_to_supabase.py`: reparacion/sync de historicos faltantes desde SQLite a Supabase.

Persistencia:

- SQLite local guarda historico completo en `data/preciospy.db`.
- Supabase se usa para datos remotos/dashboard cuando aplica.
- Clave natural de precio: `(supermercado, nombre_producto, fecha_registro)`.

Dashboard:

- Carga datos desde SQLite local si existe; si no, intenta Supabase.
- Secciones importantes:
  - monitoreo diario,
  - tabla de productos,
  - evolucion historica,
  - comparacion entre supermercados,
  - alertas de cambios,
  - exportaciones.

Matching:

- Usa nombre normalizado, clave flexible y categoria comparable.
- Las coincidencias flexibles requieren categoria comparable.
- Las exactas pueden pasar aunque falte categoria.
- Colores de graficos:
  - Biggie rojo,
  - Los Jardines amarillo,
  - Casa Rica negro,
  - Areté celeste suave,
  - Stock azul,
  - Superseis verde.

Monitoreo:

- El dashboard parsea logs de `logs/scraper-*.log`.
- Lee reparaciones de Supabase:
  - `Historicos enviados a Supabase`
  - `Paginas Supabase leidas`
  - `Pendientes finales`
  - `Supabase verificado: sin faltantes.`
