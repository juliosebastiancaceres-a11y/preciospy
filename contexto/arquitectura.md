# Arquitectura resumida

Entradas principales:

- `main.py`: CLI para ejecutar scrapers por supermercado.
- `scraper/__init__.py`: scrapers y normalizacion de nombres/productos.
- `database/__init__.py`: SQLite, Supabase, deduplicacion y persistencia.
- `dashboard.py`: dashboard Streamlit, filtros, graficos, monitoreo, oportunidades, comparacion y exportacion.
- `scripts/run_daily_scraper.sh`: corrida diaria por systemd.
- `scripts/sync_sqlite_to_supabase.py`: reparacion/sync de historicos faltantes desde SQLite a Supabase.

Persistencia:

- SQLite local guarda historico completo en `data/preciospy.db`.
- SQLite mantiene una tabla auxiliar `precios_ultimos` con el ultimo precio por producto/supermercado.
- SQLite crea indices para acelerar filtros por fecha, supermercado, nombre y supermercado+fecha.
- Supabase se usa para datos remotos/dashboard cuando aplica.
- Clave natural de precio: `(supermercado, nombre_producto, fecha_registro)`.

Dashboard:

- Carga datos desde SQLite local si existe; si no, intenta Supabase.
- Por defecto carga solo `Últimos 10 días`; puede ampliarse a `Todo el histórico`.
- Usa `precios_ultimos` para vistas actuales cuando esta disponible.
- Prepara exportaciones pesadas bajo demanda.
- Secciones importantes:
  - monitoreo diario,
  - oportunidades de compra,
  - tabla de productos,
  - evolucion historica,
  - comparacion entre supermercados,
  - alertas de cambios,
  - exportaciones.

Matching:

- Usa nombre normalizado, clave flexible y categoria comparable.
- Las coincidencias flexibles requieren categoria comparable.
- Las exactas pueden pasar aunque falte categoria.
- `descartable` se omite como atributo de packaging para comparar contra nombres genericos; `retornable` se conserva como variante distinta.
- La vista `Oportunidades` reutiliza la comparacion para preparar:
  - mejores compras,
  - resumen por categoria,
  - ranking de supermercados.
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
