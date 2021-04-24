[Homepage](https://melianmiko.ru/mibandpreview) | [Donate](https://melianmiko.ru/donate)

# MiBandPreview4Linux
Mi Band watchface preview tool (written with Python and GTK3).
This app created as an FOSS-alternative for WF_Preview app for Windows.

Features:
- Preview your Mi Band 4-6 watchfaces without building them (Mi Band 5 support is experimental)
- Set custom date/time/activity/status values for preview
- Preview updates automaticly when some file inside project dir is changed
- Opened path and current settings saves automaticly

## Instalation
You can download prebuild packages here: https://gitlab.com/melianmiko/mibandpreview/-/releases

### Ubuntu ppa
```bash
sudo add-apt-repository ppa:melianmiko/software
sudo apt update
sudo apt install mibandpreview
```

## Building for Linux
To build everything and install:
```bash
make
sudo make install
```

To make deb-package
```bash
dpkg-buildpackage -b
```

## Building for Windows
Install msys2 and update all packages (`pacman -Suy`). Then, install build and runtime dependsis:
```bash
pacman -S git mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-pip mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3-gobject mingw-w64-x86_64-python-pillow mingw-w64-x86_64-python3-watchdog mingw-w64-x86_64-nsis
export PATH=$PATH:/mingw64/bin
pip install pyinstaller
```

Then run build
```bash
make
make windows
```

Build artifacts will be located in `dist` folder.
To build an installer, use nsis with `dist/installer.nsi` script.

## License
Apache 2.0
