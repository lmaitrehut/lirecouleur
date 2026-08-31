#!/usr/bin/env bash
# Render build command : installe Calibre portable (binaire autonome, sans root)
# dans le dossier du projet (zone writable pendant le build), puis les dependances Python.
set -e

CALIBRE_DIR="$PWD/calibre-bin"
mkdir -p "$CALIBRE_DIR"

if [ ! -x "$CALIBRE_DIR/ebook-convert" ]; then
    echo "=== Installation de Calibre portable ==="
    # On telecharge directement le tarball binaire (aucun check systeme,
    # pas de libOpenGL requise a l'installation). Le binaire embarque
    # toutes ses dependances. Version recente requise pour que les couleurs
    # DOCX -> EPUB soient preservees (bug Calibre corrige apres la v5.44).
    # Pour une version fixe, remplacer par exemple :
    #   CALIBRE_URL="https://download.calibre-ebook.com/7.5.1/calibre-7.5.1-x86_64.txz"
    CALIBRE_URL="https://calibre-ebook.com/dist/linux-x86_64"
    wget -nv -O "$CALIBRE_DIR/calibre.txz" "$CALIBRE_URL"
    tar -xJf "$CALIBRE_DIR/calibre.txz" -C "$CALIBRE_DIR"
    rm -f "$CALIBRE_DIR/calibre.txz"
    echo "Calibre installe dans $CALIBRE_DIR"
else
    echo "Calibre portable deja present dans $CALIBRE_DIR"
fi

ls -la "$CALIBRE_DIR" | head -20

echo "=== Installation des dependances Python ==="
pip install -r requirements.txt

echo "=== Build complete ==="
