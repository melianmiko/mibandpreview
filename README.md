# ![App icon](mibandpreview_qt/res/icon48.png) Mi Band Preview

![Last release](https://img.shields.io/github/v/release/melianmiko/mibandpreview)
![Release date](https://img.shields.io/github/release-date/melianmiko/mibandpreview)
![Downloads](https://img.shields.io/github/downloads/melianmiko/mibandpreview/total)
[![AUR last update](https://img.shields.io/aur/last-modified/mibandpreview-git?label=AUR%20Updated)](https://aur.archlinux.org/packages/mibandpreview-git/)

Mi Band watchface preview generator library and Qt5 GUI written in Python3

-   [Homepage](https://melianmiko.ru/mibandpreview)
-   [Make a small donation](https://melianmiko.ru/donate)

Features:
-   Preview your Mi Band 4-6 watch faces without building them (Mi Band 5 support is experimental)
-   Set custom date/time/activity/status values for preview
-   Preview updates automatically when some files inside project dir would being changed
-   Opened path and current settings saves automatically

## Installation
### Ubuntu ppa
Just add my Ubuntu package archive and install application from them:
```bash
sudo add-apt-repository ppa:melianmiko/software
sudo apt update
sudo apt install mibandpreview
```

### Arch Linux
Install from [AUR](https://aur.archlinux.org/packages/mibandpreview-git/): 
```bash
# You need Yay tool
yay -S mibandpreview-git
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
Requirements:
- [MSYS2](https://www.msys2.org/)
- [Visual C++ Redist 2013](https://www.microsoft.com/ru-RU/download/details.aspx?id=40784)

MSYS2 configuration
```bash
# Update everything
pacman -Suy

# Install dependencies
pacman -S git mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-pip mingw-w64-x86_64-python-pillow mingw-w64-x86_64-nsis make mingw-w64-x86_64-python-certifi mingw-w64-x86_64-python-pyqt5 mingw-w64-x86_64-qt5-tools
pip install pyinstaller

# Add MinGW64 tools to path
echo "export PATH=$PATH:/mingw64/bin" > ~/.bashrc
```

Then run build
```bash
make
make windows
```

Build artifacts will be located in `dist` folder.
To build an installer, use nsis with `dist/installer.nsi` script.

### Python3 package
⚠ **Python3 package doesn't provide desktop icons.** This installation method should be used only if you want to use
this package as part of your own python application. If you need this package as desktop application, use Linux installation 
method.

Just install package from `pip` repository:
```bash
pip3 install mibandpreview
```

## License
Apache 2.0
