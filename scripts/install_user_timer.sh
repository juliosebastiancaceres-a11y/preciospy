#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/juliosc/preciospy"
UNIT_DIR="$HOME/.config/systemd/user"

mkdir -p "$UNIT_DIR"
cp "$PROJECT_DIR/scripts/systemd/preciospy-scraper.service" "$UNIT_DIR/"
cp "$PROJECT_DIR/scripts/systemd/preciospy-scraper.timer" "$UNIT_DIR/"

systemctl --user daemon-reload
systemctl --user enable --now preciospy-scraper.timer
systemctl --user list-timers --all preciospy-scraper.timer
