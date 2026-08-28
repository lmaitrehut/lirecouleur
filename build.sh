#!/usr/bin/env bash
# Render build command : installe les dependances Python.
# Calibre est installe au RUNTIME (start.sh) car le build et le runtime
# sont des environnements separes sur Render free.
set -e

echo "=== Installation des dependances Python ==="
pip install -r requirements.txt

echo "=== Build complete ==="
