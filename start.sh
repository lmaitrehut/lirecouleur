#!/usr/bin/env bash
# Script de demarrage : pointe vers le binaire Calibre portable (installe au build)
# puis lance gunicorn. Pas de sudo ici : le runtime free n'a pas les droits.
set -e

CALIBRE_DIR="$PWD/calibre-bin"

# L'installateur Calibre isole place le binaire dans <dir>/calibre/ebook-convert
for cand in \
    "$CALIBRE_DIR/ebook-convert" \
    "$CALIBRE_DIR/calibre/ebook-convert"; do
    if [ -x "$cand" ]; then
        EC="$cand"
        break
    fi
done

echo "=== Verification de Calibre ==="
if [ -n "$EC" ]; then
    echo "ebook-convert present : $EC"
    export PATH="$(dirname "$EC"):$PATH"
    ebook-convert --version || echo "AVERTISSEMENT: le binaire ne tourne pas (probable probleme de libs/GLIBC)"
else
    echo "ERREUR: ebook-convert introuvable dans $CALIBRE_DIR/calibre"
    echo "Contenu du dossier calibre :"
    ls -la "$CALIBRE_DIR" 2>/dev/null || echo "(calibre-bin absent)"
    exit 1
fi

echo "=== Lancement de gunicorn ==="
export PORT="${PORT:-5000}"
exec gunicorn --bind 0.0.0.0:"$PORT" --workers 1 --threads 1 --timeout 300 app:app
