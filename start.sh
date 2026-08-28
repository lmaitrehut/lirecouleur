#!/usr/bin/env bash
# Script de demarrage : installe Calibre au runtime, puis lance gunicorn.
set -e

echo "=== Installation de Calibre (runtime) ==="
if command -v ebook-convert >/dev/null 2>&1; then
    echo "Calibre deja installe."
else
    apt-get update && \
    apt-get install -y --no-install-recommends calibre && \
    rm -rf /var/lib/apt/lists/*
    echo "Calibre installe."
fi

# Verification
command -v ebook-convert

echo "=== Lancement de gunicorn ==="
exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 1 --timeout 300 app:app
