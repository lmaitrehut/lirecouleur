#!/usr/bin/env bash
# Script de demarrage : verifie que Calibre est present (installe au build)
# puis lance gunicorn. Pas de sudo ici : le runtime free n'a pas les droits.
set -e

echo "=== Verification de Calibre ==="
if command -v ebook-convert >/dev/null 2>&1; then
    echo "ebook-convert present : $(command -v ebook-convert)"
else
    echo "ERREUR: ebook-convert introuvable. Calibre n'a pas ete installe au build."
    exit 1
fi

echo "=== Lancement de gunicorn ==="
export PORT="${PORT:-5000}"
exec gunicorn --bind 0.0.0.0:"$PORT" --workers 1 --threads 1 --timeout 300 app:app
