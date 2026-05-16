# PreciosPY

PreciosPY es un sistema simple para monitorear precios de supermercados en Paraguay.
Scrapea productos, guarda registros historicos en SQLite y permite revisar precios,
productos baratos y evolucion temporal desde un dashboard en Streamlit.

## Tecnologias

- Python
- Streamlit
- SQLite
- Requests + BeautifulSoup
- Pandas
- Supabase opcional

## Estructura

```text
.
├── dashboard.py              # Dashboard Streamlit
├── main.py                   # Entrada CLI para ejecutar scrapers
├── scraper/                  # Scrapers y limpieza de datos
├── database/                 # Persistencia SQLite y Supabase
├── data/                     # Base SQLite local, ignorada por Git
├── tests/                    # Pruebas basicas
├── stock_categorias_urls.txt # Categorias usadas por el scraper de Stock
├── .env.example              # Variables de entorno de ejemplo
└── requirements.txt
```

## Instalacion

```bash
pip install -r requirements.txt
```

Si tu sistema bloquea instalaciones globales de Python, crea primero un entorno
virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuracion

Copiar el archivo de ejemplo y completar credenciales propias si se va a usar
Supabase:

```bash
cp .env.example .env
```

Variables disponibles:

```env
SUPABASE_URL=
SUPABASE_KEY=
```

Supabase es opcional. Si esas variables no existen, el scraper guarda solo en
SQLite local y omite la sincronizacion remota con un mensaje claro.

No subir al repositorio `.env`, bases locales `*.db`, `data/*.db`,
`.streamlit/secrets.toml` ni archivos de cache.

## Supabase

Para usar Supabase:

1. Crear un proyecto en Supabase.
2. Abrir el SQL Editor.
3. Ejecutar el contenido de `database/supabase_schema.sql`.
4. Copiar `SUPABASE_URL` y `SUPABASE_KEY` en `.env`.
5. Ejecutar una prueba corta:

```bash
python main.py --supermercado stock --limite-categorias 1 --limite-paginas 1
```

La tabla remota debe tener la restriccion unica:

```sql
unique (supermercado, nombre_producto, fecha_registro)
```

Esa restriccion es necesaria para que el `upsert` evite duplicados.

Si la tabla `precios` ya existia antes, el mismo SQL agrega las columnas nuevas
con `alter table ... add column if not exists` y crea la restriccion unica. Si
Supabase rechaza la restriccion, primero revisar duplicados con:

```sql
select supermercado, nombre_producto, fecha_registro, count(*)
from public.precios
group by supermercado, nombre_producto, fecha_registro
having count(*) > 1;
```

No borres datos sin revisar esos resultados.

## Ejecutar el scraper

Inicializar base y scrapear todos los supermercados configurados:

```bash
python main.py
```

Ejecutar solo un supermercado:

```bash
python main.py --supermercado superseis
python main.py --supermercado stock
python main.py --supermercado losjardines
python main.py --supermercado casarica
python main.py --supermercado biggie
python main.py --supermercado arete
```

Prueba corta sin enviar datos a Supabase:

```bash
python main.py --supermercado stock --limite-categorias 1 --limite-paginas 1 --sin-supabase
```

El scraper de Stock lee sus categorias desde `stock_categorias_urls.txt`.
El scraper de Los Jardines recorre las paginas del catalogo con el formato
`categoria.2`, `categoria.3`, etc., hasta que no encuentra mas productos o llega
al limite configurado.
El scraper de Casa Rica usa el mismo formato de paginacion del catalogo y recorre
las categorias principales configuradas.
El scraper de Biggie usa su API publica de categorias y articulos, paginando con
`take` y `skip` hasta cubrir el total reportado por cada categoria.
El scraper de Areté usa la paginacion del catalogo con el formato `categoria.2`,
`categoria.3`, etc., igual que Los Jardines y Casa Rica.

## Sincronizar historicos SQLite a Supabase

Revisar registros locales que todavia no estan en Supabase:

```bash
python scripts/sync_sqlite_to_supabase.py
```

Subir los historicos faltantes usando `upsert` sin duplicar:

```bash
python scripts/sync_sqlite_to_supabase.py --apply
```

## Ejecutar el dashboard

```bash
./scripts/run_dashboard.sh
```

El script usa siempre `.venv/bin/python -m streamlit` para cargar las
dependencias instaladas en el entorno virtual del proyecto. Por defecto abre en
`http://127.0.0.1:8501`; se puede cambiar con `DASHBOARD_PORT`.

El dashboard lee `data/preciospy.db`. Si la base no existe o no tiene datos,
muestra un mensaje informativo en lugar de fallar.

## Desplegar en Streamlit Community Cloud

1. Entrar a <https://share.streamlit.io>.
2. Iniciar sesion con GitHub.
3. Crear una app nueva desde este repositorio:
   - Repository: `juliosebastiancaceres-a11y/preciospy`
   - Branch: `main`
   - Main file path: `dashboard.py`
4. En `Advanced settings`, pegar los secrets:

```toml
SUPABASE_URL="https://tu-proyecto.supabase.co"
SUPABASE_KEY="tu_clave_de_supabase"
```

5. Elegir el subdominio, por ejemplo `preciospy`, si esta disponible.
6. Hacer deploy.

No pegar secrets en archivos del repositorio. Streamlit Cloud los guarda fuera
del codigo y el dashboard los lee desde `st.secrets`.

## Funcionalidades actuales

- Filtros por supermercado, nombre y rango de precios.
- Busqueda literal segura, sin interpretar el texto como expresion regular.
- Metricas separadas para productos unicos, registros historicos, supermercados,
  dias registrados y ultima actualizacion.
- Seccion de productos mas baratos usando el registro mas reciente por producto
  y supermercado.
- Grafico de evolucion de precios por producto y supermercado.
- Evolucion historica por producto equivalente usando matching.
- Comparacion de productos equivalentes entre supermercados.
- Alertas de cambios de precio y minimos historicos.
- Exportacion CSV/Excel de productos, comparaciones, alertas e historico.
- Vista de salud y logs recientes del scraper.
- Tabla de productos filtrados con precio formateado en guaranies.
- SQLite con proteccion contra duplicados por supermercado, producto y fecha.
- Supabase opcional con `upsert` por clave natural.

## Base de datos

La tabla principal es `precios`. Para instalaciones nuevas se crea con una clave
unica:

```sql
UNIQUE(supermercado, nombre_producto, fecha_registro)
```

En bases antiguas con duplicados existentes, el proyecto no borra datos
automaticamente. En ese caso instala un trigger para evitar nuevos duplicados y
avisa por consola.

## Tests

```bash
pytest
```

Las pruebas cubren limpieza de precios, normalizacion de nombres, matching,
exportaciones, alertas, logs y descarte de precios invalidos.

## Mejoras futuras

- Migracion asistida para deduplicar bases SQLite antiguas.
- Mejoras adicionales de matching para packs, marcas y variantes complejas.
- Alertas configurables por producto o supermercado.
- Alternativa cloud mas confiable que GitHub Actions para scraping.
