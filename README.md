# PreciosPY

PreciosPY es un sistema simple de monitoreo de precios de supermercados en Paraguay.
El objetivo es scrapear precios de productos, guardarlos con fecha en una base de datos
SQLite local y, más adelante, visualizar la evolución de precios en el tiempo.

## Etapas planeadas

1. Crear la estructura inicial del proyecto y la base de datos local.
2. Implementar scrapers para supermercados paraguayos, empezando por Superseis.
3. Guardar precios históricos con fecha de registro.
4. Agregar consultas simples para revisar la evolución de precios.
5. Construir visualizaciones cuando el flujo de datos esté estable.

## Uso inicial

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Inicializar la base de datos:

```bash
python main.py
```

Ejecutar una prueba corta sin enviar datos a Supabase:

```bash
python main.py --supermercado stock --limite-categorias 1 --limite-paginas 1 --sin-supabase
```

Ejecutar solo un supermercado:

```bash
python main.py --supermercado superseis
python main.py --supermercado stock
```

El scraper de Stock lee sus categorías desde `stock_categorias_urls.txt`.
