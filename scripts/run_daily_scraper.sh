#!/usr/bin/env bash
set -u

export PATH="/usr/local/bin:/usr/bin:/bin"
export PRECIOSPY_PAUSA_ENTRE_PAGINAS="${PRECIOSPY_PAUSA_ENTRE_PAGINAS:-0.2}"
export PRECIOSPY_PAUSA_REINTENTO="${PRECIOSPY_PAUSA_REINTENTO:-2}"
export PRECIOSPY_REQUEST_TIMEOUT="${PRECIOSPY_REQUEST_TIMEOUT:-20}"
export PRECIOSPY_REQUEST_REINTENTOS="${PRECIOSPY_REQUEST_REINTENTOS:-3}"
export PRECIOSPY_INTERVALO_PROGRESO_PAGINAS="${PRECIOSPY_INTERVALO_PROGRESO_PAGINAS:-25}"

PROJECT_DIR="/home/juliosc/preciospy"
LOG_DIR="$PROJECT_DIR/logs"
TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
LOG_FILE="$LOG_DIR/scraper-$TIMESTAMP.log"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"

STOCK_LIMITE_CATEGORIAS="${STOCK_LIMITE_CATEGORIAS:-10}"
STOCK_LIMITE_PAGINAS="${STOCK_LIMITE_PAGINAS:-2}"
SUPERSEIS_LIMITE_CATEGORIAS="${SUPERSEIS_LIMITE_CATEGORIAS:-5}"
SUPERSEIS_LIMITE_PAGINAS="${SUPERSEIS_LIMITE_PAGINAS:-2}"
LOS_JARDINES_LIMITE_CATEGORIAS="${LOS_JARDINES_LIMITE_CATEGORIAS:-18}"
LOS_JARDINES_LIMITE_PAGINAS="${LOS_JARDINES_LIMITE_PAGINAS:-250}"
CASA_RICA_LIMITE_CATEGORIAS="${CASA_RICA_LIMITE_CATEGORIAS:-24}"
CASA_RICA_LIMITE_PAGINAS="${CASA_RICA_LIMITE_PAGINAS:-250}"
BIGGIE_LIMITE_CATEGORIAS="${BIGGIE_LIMITE_CATEGORIAS:-21}"
BIGGIE_LIMITE_PAGINAS="${BIGGIE_LIMITE_PAGINAS:-250}"
ARETE_LIMITE_CATEGORIAS="${ARETE_LIMITE_CATEGORIAS:-26}"
ARETE_LIMITE_PAGINAS="${ARETE_LIMITE_PAGINAS:-250}"
MEGASHOP_LIMITE_CATEGORIAS="${MEGASHOP_LIMITE_CATEGORIAS:-16}"
MEGASHOP_LIMITE_PAGINAS="${MEGASHOP_LIMITE_PAGINAS:-250}"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR" || exit 1

if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="$(command -v python3)"
fi

estado=0

run_scraper() {
    nombre="$1"
    shift

    echo
    echo "== $nombre =="
    echo "Inicio: $(date '+%Y-%m-%d %H:%M:%S %Z')"

    "$@"
    codigo=$?

    echo "Fin: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "Codigo de salida: $codigo"

    if [ "$codigo" -ne 0 ]; then
        estado="$codigo"
    fi
}

{
    echo "PreciosPY scraper diario"
    echo "Log: $LOG_FILE"
    echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "Python: $PYTHON_BIN"
    echo "Pausa entre paginas: $PRECIOSPY_PAUSA_ENTRE_PAGINAS s"
    echo "Pausa reintento: $PRECIOSPY_PAUSA_REINTENTO s"
    echo "Timeout request: $PRECIOSPY_REQUEST_TIMEOUT s"
    echo "Reintentos request: $PRECIOSPY_REQUEST_REINTENTOS"

    run_scraper \
        "Stock" \
        "$PYTHON_BIN" -u main.py \
            --supermercado stock \
            --limite-categorias "$STOCK_LIMITE_CATEGORIAS" \
            --limite-paginas "$STOCK_LIMITE_PAGINAS"

    run_scraper \
        "Superseis" \
        "$PYTHON_BIN" -u main.py \
            --supermercado superseis \
            --limite-categorias "$SUPERSEIS_LIMITE_CATEGORIAS" \
            --limite-paginas "$SUPERSEIS_LIMITE_PAGINAS"

    run_scraper \
        "Los Jardines" \
        "$PYTHON_BIN" -u main.py \
            --supermercado losjardines \
            --limite-categorias "$LOS_JARDINES_LIMITE_CATEGORIAS" \
            --limite-paginas "$LOS_JARDINES_LIMITE_PAGINAS"

    run_scraper \
        "Casa Rica" \
        "$PYTHON_BIN" -u main.py \
            --supermercado casarica \
            --limite-categorias "$CASA_RICA_LIMITE_CATEGORIAS" \
            --limite-paginas "$CASA_RICA_LIMITE_PAGINAS"

    run_scraper \
        "Biggie" \
        "$PYTHON_BIN" -u main.py \
            --supermercado biggie \
            --limite-categorias "$BIGGIE_LIMITE_CATEGORIAS" \
            --limite-paginas "$BIGGIE_LIMITE_PAGINAS"

    run_scraper \
        "Areté" \
        "$PYTHON_BIN" -u main.py \
            --supermercado arete \
            --limite-categorias "$ARETE_LIMITE_CATEGORIAS" \
            --limite-paginas "$ARETE_LIMITE_PAGINAS"

    run_scraper \
        "Megashop" \
        "$PYTHON_BIN" -u main.py \
            --supermercado megashop \
            --limite-categorias "$MEGASHOP_LIMITE_CATEGORIAS" \
            --limite-paginas "$MEGASHOP_LIMITE_PAGINAS"

    run_scraper \
        "Sincronizar faltantes SQLite -> Supabase" \
        "$PYTHON_BIN" -u scripts/sync_sqlite_to_supabase.py --apply

    echo
    echo "Estado final: $estado"
} >> "$LOG_FILE" 2>&1

exit "$estado"
