# MiBandPreview4Linux
Mi Band 4/5 watchface preview tool for Linux (CLI + GTK).
This app created as an FOSS-alternative for WF_Preview app for Windows.

Features:
- Preview your Mi Band 4 watchfaces without building them (Mi Band 5 support is experimental)
- Set custom date/time/activity/status values for preview
- Preview updates automaticly when some file inside project dir is changed
- Opened path and current settings saves automaticly

## Installation (Ubuntu)
Download .deb package from [releases page](https://github.com/melianmiko/MiBandPreview4Linux/releases).

## Building
### Debian
ToDo!

### Windows
Install msys2 and update all packages (`pacman -Suy`). Then, install build and runtime dependsis:
```bash
pacman -S git mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-pip mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3-gobject mingw-w64-x86_64-python-pillow mingw-w64-x86_64-python3-watchdog
export PATH=$PATH:/mingw64/bin
pip install pyinstaller
```
Then run build
```
make windows
```
Build artifacts will be located in `dist` folder.

## Launch from source
First of all, install python3 and pip with your package manager. For ubuntu: `sudo
apt install python3 python3-pip`. Then, clone this repository to some directory
in your home, eg. `.local/app/mibandpreview`. Open a terminal in this directory and run:
```bash
# Do not use sudo!
pip3 install Pillow watchdog
```
Now, you can launch app with `./src/GtkUi.py` command.
Optionally, create a launcher icon:
```bash
./create-shortcut.sh
```

## License
Apache 2.0
