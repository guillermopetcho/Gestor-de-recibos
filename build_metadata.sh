#!/bin/bash
set -e

export WINEPREFIX="$PWD/.wine_env_full"
export WINEDEBUG=-all

PYTHON_DIR="$PWD/python_nuget_env/tools"

echo "Preparando compilacion..."
rm -rf build GestorRecibos.spec executable dist

echo "Compilando ejecutable para Windows..."
WIN_PWD="Z:${PWD//\//\\}"
wine "$PYTHON_DIR/python.exe" -m PyInstaller --noconsole --onefile --hidden-import pkgutil --version-file="version_info.txt" --add-data "$WIN_PWD\\python_nuget_env\\tools\\Lib\\site-packages\\PyQt6\\Qt6\\plugins;PyQt6/Qt6/plugins" --name "GestorRecibos" run.py

echo "Renombrando dist a executable..."
mv dist executable

echo "=== ¡Proceso completado! ==="
