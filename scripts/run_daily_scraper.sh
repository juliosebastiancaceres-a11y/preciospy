#!/usr/bin/env bash
set -u

export PATH="/usr/local/bin:/usr/bin:/bin"

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
        "Sincronizar faltantes SQLite -> Supabase" \
        "$PYTHON_BIN" -u scripts/sync_sqlite_to_supabase.py --apply

    echo
    echo "Estado final: $estado"
} >> "$LOG_FILE" 2>&1

exit "$estado"
