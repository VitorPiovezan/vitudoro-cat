#!/bin/bash
set -e

echo "Instalando vitudoro-cat..."

pip3 install --user .

DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"
cp vitudoro-cat.desktop "$DESKTOP_DIR/"

echo "Instalacao concluida!"
echo "Execute com: vitudoro-cat"
echo "Ou encontre 'Vitudoro Cat' no menu de aplicativos."
