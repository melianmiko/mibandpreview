# MiBandPreview4Linux
Mi Band 4/5 watchface preview tool for Linux (CLI + GTK).
This app created as an FOSS-alternative for WF_Preview app for Windows.

Features:
- Preview your Mi Band 4 watchfaces without building them (Mi Band 5 support is experimental)
- Set custom date/time/activity/status values for preview
- Preview updates automaticly when some file inside project dir is changed
- Opened path and current settings saves automaticly

## Instalation (Ubuntu)
Download .deb package from [releases page](https://github.com/melianmiko/MiBandPreview4Linux/releases).

## Requirements
- Linux (windows is not supported, hah!)
- Python3, pip3
- GTK+ 3
- Pillow, watchdog

## Instalation
First of all, install python3 and pip with your package manager. For ubuntu: `sudo
apt install python3 python3-pip`. Then, clone this repository to some directory
in your home, eg. `.local/app/mibandpreview`. Open a terminal in this directory and run:
```bash
# Do not use sudo!
pip3 install Pillow watchdog
./create-shortcut.sh
```
Now, application shortcut will appear in your applications menu.

## Usage (GTK)
Run `./GtkUI.py` to start, or use application launcher icon (see Instalation).

## Usage (Cli)
Run `./cli.py` inside a directory with your watchface files.
Preview will appear in parent directory.

## API
You can use our preview generator as part of your python3 project.
Simply import `Loader_MiBand4` (or 5) and do what you want.
See `cli.py` as example.

## License
Apache 2.0
