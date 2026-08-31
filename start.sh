#!/usr/bin/env bash
# Script de demarrage : lance gunicorn.
# Plus de Calibre : le traitement est 100% Python (epub_processor.py).
set -e

echo "=== Lancement de gunicorn ==="
export PORT="${PORT:-5000}"
exec gunicorn --bind 0.0.0.0:"$PORT" --workers 1 --threads 1 --timeout 300 app:app
