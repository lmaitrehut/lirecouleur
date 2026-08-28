#!/usr/bin/env bash
# Script de demarrage : pointe vers le binaire Calibre portable (installe au build)
# puis lance gunicorn. Pas de sudo ici : le runtime free n'a pas les droits.
set -e

CALIBRE_DIR="$PWD/calibre-bin"

echo "=== Verification de Calibre ==="
if [ -x "$CALIBRE_DIR/ebook-convert" ]; then
    echo "ebook-convert present : $CALIBRE_DIR/ebook-convert"
    export PATH="$CALIBRE_DIR:$PATH"
    ebook-convert --version || echo "AVERTISSEMENT: le binaire ne tourne pas (probable probleme GLIBC)"
else
    echo "ERREUR: ebook-convert portable introuvable dans $CALIBRE_DIR"
    echo "Le build a peut-etre echoue a installer Calibre."
    exit 1
fi

echo "=== Lancement de gunicorn ==="
export PORT="${PORT:-5000}"
exec gunicorn --bind 0.0.0.0:"$PORT" --workers 1 --threads 1 --timeout 300 app:app
