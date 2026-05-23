# Proximos pasos recomendados

Prioridad alta: rendimiento del dashboard.

Problema observado:

- El dashboard tarda en cargar porque ya hay mas de 300k registros historicos.
- Varias secciones calculan sobre todo el historico.

Mejoras recomendadas, en orden:

1. Cargar por defecto solo los ultimos 10 dias en el dashboard.
   - Permitir opcion para ampliar a todo el historico.
   - Esto deberia mejorar mucho la primera carga.

2. Agregar indices SQLite.
   - `fecha_registro`
   - `supermercado`
   - `nombre_producto`
   - `(supermercado, fecha_registro)`

3. Calcular secciones pesadas bajo demanda.
   - Comparacion entre supermercados.
   - Alertas.
   - Exportaciones.

4. Cachear resultados pesados.
   - Comparacion.
   - Alertas.
   - Historico filtrado.

5. Mas adelante: tabla auxiliar de ultimo precio por producto/supermercado.

Pendiente operativo inmediato:

- Revisar que la corrida del 2026-05-23 termine OK, porque al crear este contexto seguia en curso por Areté.
- Confirmar que el timer vuelva a mostrar proxima ejecucion despues de terminar la corrida actual.
