#!/usr/bin/env bash
# Render build command : installe Calibre (droits root disponibles au build)
# puis les dependances Python. L'image construite est deployee au runtime.
set -e

echo "=== Installation de Calibre ==="
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends calibre
rm -rf /var/lib/apt/lists/*
echo "Calibre installe : $(command -v ebook-convert)"

echo "=== Installation des dependances Python ==="
pip install -r requirements.txt

echo "=== Build complete ==="
