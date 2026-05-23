# Decisiones tomadas

Supermercados:

- Mantener foco en supermercados paraguayos.
- Megashop fue removido por no ser paraguayo.
- Activos: Stock, Superseis, Los Jardines, Casa Rica, Biggie, Areté.

Sync Supabase:

- Bug corregido: paginacion de Supabase sin orden fijo producia faltantes falsos.
- Solucion: `cargar_claves_supabase()` usa `.order("id")` antes de `.range(...)`.
- El sync ahora muestra progreso y valida al final si corre con `--apply`.
- Si quedan pendientes finales reales, el script retorna codigo `2`.

Dashboard:

- Se agregaron filtros propios para comparacion entre supermercados.
- Esos filtros no afectan el grafico de evolucion historica.
- La barra lateral fue forzada visualmente para evitar que quede escondida sin forma clara de volver.
- El monitoreo distingue:
  - `OK`,
  - `OK con avisos`,
  - `OK con reparacion`,
  - `En curso`,
  - `Error`.

Datos y seguridad:

- No incluir credenciales en archivos de contexto.
- No tocar `.env` salvo pedido explicito del usuario.
- `blockbench/` y `labs/` no se suben salvo indicacion clara.
