#!/usr/bin/env bash

APPROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "[Desktop Entry]" > ~/.local/share/applications/mi-band-preview.desktop
echo "Version=1.1" >> ~/.local/share/applications/mi-band-preview.desktop
echo "Type=Application" >> ~/.local/share/applications/mi-band-preview.desktop
echo "Name=Mi Band Preview" >> ~/.local/share/applications/mi-band-preview.desktop
echo "Comment=Tool to preview Mi Band watchfaces" >> ~/.local/share/applications/mi-band-preview.desktop
echo "Icon=$APPROOT/docs/icon.png" >> ~/.local/share/applications/mi-band-preview.desktop
echo "Exec=$APPROOT/GtkUI.py" >> ~/.local/share/applications/mi-band-preview.desktop
echo "Path=$APPROOT" >> ~/.local/share/applications/mi-band-preview.desktop
echo "Actions=" >> ~/.local/share/applications/mi-band-preview.desktop
echo "Categories=Development;" >> ~/.local/share/applications/mi-band-preview.desktop
