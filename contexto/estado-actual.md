# Estado actual

Fecha de este contexto: 2026-05-23, America/Asuncion.

Repo:

- Ruta local: `/home/juliosc/preciospy`
- Rama principal: `main`
- Remoto GitHub: `juliosebastiancaceres-a11y/preciospy`
- Ultimo commit subido conocido: `34c98d6 Mostrar verificacion final del sync`
- Cambios no trackeados recurrentes: `blockbench/`, `labs/`

Datos:

- SQLite local: `data/preciospy.db`
- Total aproximado al 2026-05-23 12:08: `355.190` registros
- Dias con datos distintos: `19`
- Ultimos conteos por fecha vistos:
  - 2026-05-23: `22.410` registros parciales mientras la corrida seguia activa
  - 2026-05-22: `33.810`
  - 2026-05-21: `34.237`
  - 2026-05-20: `34.134`
  - 2026-05-19: `34.144`
  - 2026-05-18: `34.132`

Operacion diaria:

- Timer systemd: `preciospy-scraper.timer`
- Servicio: `preciospy-scraper.service`
- El 2026-05-23 el servicio estaba activo/iniciando desde `09:37:46 -03`.
- Ultimo log en curso visto: `logs/scraper-2026-05-23_09-37-46.log`
- Al momento de documentar, la corrida iba por `Areté`; Stock, Superseis, Los Jardines, Casa Rica y Biggie ya habian terminado OK.
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
