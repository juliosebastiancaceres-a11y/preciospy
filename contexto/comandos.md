# Comandos frecuentes

Dashboard:

```bash
python3 -m streamlit run dashboard.py --server.address 127.0.0.1 --server.port 8501
```

URL local:

```text
http://127.0.0.1:8501
```

Tests:

```bash
.venv/bin/python -m pytest
```

Tests por area:

```bash
.venv/bin/python -m pytest tests/test_sync_sqlite_to_supabase.py
.venv/bin/python -m pytest tests/test_dashboard_logs.py
.venv/bin/python -m pytest tests/test_dashboard_matching.py
```

Scraper corto sin Supabase:

```bash
.venv/bin/python main.py --supermercado stock --limite-categorias 1 --limite-paginas 1 --sin-supabase
.venv/bin/python main.py --supermercado superseis --limite-categorias 1 --limite-paginas 1 --sin-supabase
```

Verificar Supabase sin aplicar cambios:

```bash
.venv/bin/python scripts/sync_sqlite_to_supabase.py --limite 5
```

Aplicar reparacion de faltantes:

```bash
.venv/bin/python scripts/sync_sqlite_to_supabase.py --apply
```

Systemd usuario:

```bash
systemctl --user list-timers --all
systemctl --user status preciospy-scraper.timer preciospy-scraper.service
journalctl --user -u preciospy-scraper.service -n 100 --no-pager
```

Git basico:

```bash
git status --short
git add <archivos>
git commit -m "Mensaje"
git push
```
