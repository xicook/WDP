#!/bin/bash

echo "Configurando ambiente de build (Debian/Ubuntu safe)..."

# Create a temporary virtual environment
python3 -m venv venv_build
source venv_build/bin/activate

# Install dependencies inside the venv
pip install --upgrade pip
pip install pyinstaller Pillow requests

# Build the app
# --onefile: single executable
# --noconsole: don't show terminal (GUI only)
# --add-data: include the registry file
pyinstaller --onefile --noconsole --add-data "wdp_registry.json:." wdp_browser.py

# Cleanup
deactivate
rm -rf venv_build

echo "----------------------------------------------------"
echo "Build concluído! Executável localizado em: dist/wdp_browser"
echo "----------------------------------------------------"
