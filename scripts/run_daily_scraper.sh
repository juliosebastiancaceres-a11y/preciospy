#!/usr/bin/env bash
set -u

export PATH="/usr/local/bin:/usr/bin:/bin"

PROJECT_DIR="/home/juliosc/preciospy"
LOG_DIR="$PROJECT_DIR/logs"
TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
LOG_FILE="$LOG_DIR/scraper-$TIMESTAMP.log"

STOCK_LIMITE_CATEGORIAS="${STOCK_LIMITE_CATEGORIAS:-10}"
STOCK_LIMITE_PAGINAS="${STOCK_LIMITE_PAGINAS:-2}"
SUPERSEIS_LIMITE_CATEGORIAS="${SUPERSEIS_LIMITE_CATEGORIAS:-5}"
SUPERSEIS_LIMITE_PAGINAS="${SUPERSEIS_LIMITE_PAGINAS:-2}"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR" || exit 1

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

    run_scraper \
        "Stock" \
        python3 -u main.py \
            --supermercado stock \
            --limite-categorias "$STOCK_LIMITE_CATEGORIAS" \
            --limite-paginas "$STOCK_LIMITE_PAGINAS"

    run_scraper \
        "Superseis" \
        python3 -u main.py \
            --supermercado superseis \
            --limite-categorias "$SUPERSEIS_LIMITE_CATEGORIAS" \
            --limite-paginas "$SUPERSEIS_LIMITE_PAGINAS"

    echo
    echo "Estado final: $estado"
} >> "$LOG_FILE" 2>&1

exit "$estado"
