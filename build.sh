#!/usr/bin/env bash
# Render build command : installe Calibre portable (binaire autonome, sans root)
# dans le dossier du projet (zone writable pendant le build), puis les dependances Python.
set -e

CALIBRE_DIR="$PWD/calibre-bin"
mkdir -p "$CALIBRE_DIR"

if [ ! -x "$CALIBRE_DIR/ebook-convert" ]; then
    echo "=== Installation de Calibre portable ==="
    # Mode "isolated" : n'ecrit que dans install_dir, sans droits root.
    # Le binaire Calibre embarque toutes ses dependances.
    # NB: les versions recentes (>=6) exigent libOpenGL/system libs indisponibles
    # sur Render free (systeme de fichiers en lecture seule). On force une version
    # 5.x qui evite ces checks et ne requiert que GLIBC >= 2.27.
    wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh \
        | sh /dev/stdin install_dir="$CALIBRE_DIR" isolated=y version=5.44.0
    echo "Calibre installe dans $CALIBRE_DIR"
else
    echo "Calibre portable deja present dans $CALIBRE_DIR"
fi

ls -la "$CALIBRE_DIR" | head -20

echo "=== Installation des dependances Python ==="
pip install -r requirements.txt

echo "=== Build complete ==="
