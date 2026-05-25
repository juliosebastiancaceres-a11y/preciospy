# Estado actual

Fecha de este contexto: 2026-05-25, America/Asuncion.

Repo:

- Ruta local: `/home/juliosc/preciospy`
- Rama principal: `main`
- Remoto GitHub: `juliosebastiancaceres-a11y/preciospy`
- Ultimo commit subido conocido: `aafa84d Agregar vista de datos y exportacion bajo demanda`
- Cambios no trackeados recurrentes: `blockbench/`, `labs/`

Datos:

- SQLite local: `data/preciospy.db`
- Total al 2026-05-25 14:28 -03: `433.982` registros
- Dias con datos distintos: `21`
- Rango de fechas: `2026-05-02` a `2026-05-25`
- Ultimos conteos por fecha vistos:
  - 2026-05-25: `33.525`
  - 2026-05-24: `33.780`
  - 2026-05-23: `33.897`
  - 2026-05-22: `33.810`
  - 2026-05-21: `34.237`
  - 2026-05-20: `34.134`
  - 2026-05-19: `34.144`
  - 2026-05-18: `34.132`

Operacion diaria:

- Timer systemd: `preciospy-scraper.timer`
- Servicio: `preciospy-scraper.service`
- Ultima corrida revisada: `2026-05-25 06:48:42 -03` a `07:25:24 -03`.
- Ultimo log revisado: `logs/scraper-2026-05-25_06-48-42.log`
- Estado systemd: servicio inactivo con salida `0/SUCCESS`.
- Proxima ejecucion vista: `2026-05-26 06:01:19 -03`.
- Casa Rica suele mostrar avisos temporales recuperados por desconexion remota.

Supermercados activos:

- Stock
- Superseis
- Los Jardines
- Casa Rica
- Biggie
- Areté

Supermercado removido:

- Megashop fue quitado porque el proyecto queda enfocado en Paraguay.
- El dashboard filtra Megashop si aparece en datos viejos.

Estado de Supabase:

- Se corrigio un bug importante: la lectura paginada de claves ahora usa `.order("id")` antes de `.range(...)`.
- Antes, Supabase podia parecer con faltantes falsos por paginacion sin orden estable.
- Verificacion real posterior al arreglo: `Registros faltantes detectados: 0`.
- Verificacion del 2026-05-25:
  - Registros validos en SQLite: `433.982`
  - Claves existentes en Supabase: `438.571`
  - Registros faltantes detectados: `0`

Rendimiento del dashboard:

- Ya se implemento carga por defecto de `Últimos 10 días`.
- Ya se permite ampliar a `Todo el histórico`.
- Ya existen indices SQLite para `fecha_registro`, `supermercado`, `nombre_producto` y `(supermercado, fecha_registro)`.
- Ya existe tabla materializada local `precios_ultimos` para ultimo precio por producto/supermercado.
- Ya hay exportacion bajo demanda para evitar preparar archivos pesados al cargar.
- Ya existe vista `Oportunidades` para mejores compras, resumen por categoria y ranking de supermercados.
- Matching ajustado con caso real `DESCARTABLE 2LTS` sin mezclar variantes `retornable`.

Verificacion tecnica:

- Suite completa ejecutada el 2026-05-25: `108 passed`.
- Dashboard levantado para prueba local en `http://127.0.0.1:8599`.
