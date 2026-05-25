# Proximos pasos recomendados

Prioridad alta ya resuelta: rendimiento del dashboard.

Trabajo ya implementado:

- Carga por defecto de `Últimos 10 días`.
- Opcion para ampliar a `Todo el histórico`.
- Indices SQLite:
  - `fecha_registro`
  - `supermercado`
  - `nombre_producto`
  - `(supermercado, fecha_registro)`
- Tabla materializada `precios_ultimos`.
- Exportaciones preparadas bajo demanda.
- Vista `Oportunidades` con mejores compras, resumen por categoria y ranking de supermercados.
- Matching ajustado para comparar productos `descartable` contra nombres genericos sin mezclar `retornable`.
- Tests completos pasando: `108 passed`.

Siguiente paso recomendado:

1. Verificacion visual del dashboard.
   - Levantar con `./scripts/run_dashboard.sh`.
   - Probar carga inicial con `Últimos 10 días`.
   - Probar cambio a `Todo el histórico`.
   - Revisar oportunidades, comparacion, alertas, tabla de datos, exportacion y monitoreo.
   - Confirmar que la experiencia real de carga sea aceptable con mas de 400k registros.

2. Seguir mejorando calidad del matching con casos reales.
   - Buscar productos que deberian coincidir y no coinciden.
   - Buscar productos que coinciden pero no deberian.
   - Agregar pruebas por cada caso real antes de ajustar reglas.
   - Revisar especialmente packs, unidades multiples y categorias ambiguas.

3. Reducir costo de verificacion diaria Supabase si hace falta.
   - El sync final actualmente lee cientos de paginas de claves para confirmar faltantes.
   - Funciona bien, pero podria optimizarse si el tiempo diario vuelve a crecer.

4. Mantener actualizado este contexto despues de cambios importantes.
   - Especialmente `estado-actual.md` y este archivo.
