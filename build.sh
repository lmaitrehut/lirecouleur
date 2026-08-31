#!/usr/bin/env bash
# Render build command : installe uniquement les dependances Python.
# Plus de Calibre : la coloration est faite en pur Python sur l'epub directement.
set -e

echo "=== Installation des dependances Python ==="
pip install -r requirements.txt

echo "=== Build complete ==="
