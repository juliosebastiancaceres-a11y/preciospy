#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/juliosc/preciospy"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
HOST="${DASHBOARD_HOST:-127.0.0.1}"
PORT="${DASHBOARD_PORT:-8501}"

cd "$PROJECT_DIR"

if [ ! -x "$PYTHON_BIN" ]; then
    echo "No se encontro el entorno virtual en $PYTHON_BIN" >&2
    echo "Crea el entorno e instala dependencias antes de iniciar el dashboard." >&2
    exit 1
fi

exec "$PYTHON_BIN" -m streamlit run dashboard.py \
    --server.address "$HOST" \
    --server.port "$PORT"
