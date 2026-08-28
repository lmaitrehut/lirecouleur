#!/usr/bin/env bash
# Render build command: install system dependencies (Calibre) then Python deps.
set -e

echo "=== Installing Calibre via apt ==="
if command -v ebook-convert >/dev/null 2>&1; then
    echo "Calibre already installed."
else
    sudo apt-get update && \
    sudo apt-get install -y --no-install-recommends calibre && \
    sudo rm -rf /var/lib/apt/lists/*
fi

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Build complete ==="
