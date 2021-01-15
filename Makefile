#!/usr/bin/make -f
DESTDIR=/

all: clean

clean:
	rm -rf src/__pycache__
	rm -rf build dist

install:
	mkdir -p $(DESTDIR)/opt/mibandpreview
	mkdir -p $(DESTDIR)/usr/share/applications
	cp -r src/* $(DESTDIR)/opt/mibandpreview
	ln -sf $(DESTDIR)/opt/mibandpreview/res/mi-band-preview.desktop $(DESTDIR)/usr/share/applications/mi-band-preview.desktop

uninstall:
	rm $(DESTDIR)/usr/share/applications/mi-band-preview.desktop
	rm -rf $(DESTDIR)/opt/mibandpreview

debian:
	dpkg-buildpackage

windows:
	export PATH=$PATH:/mingw64/bin
	rm -rf build dist
	pyinstaller --name mibandpreview --icon src/res/icon.ico -w \
		--add-data "src/res;res" --add-data "src/locale;locale" \
		src/GtkUi.py
	mkdir dist/mibandpreview/etc
	mv dist/mibandpreview/res/gtk-3.0 dist/mibandpreview/etc/gtk-3.0
	rm -rf dist/mibandpreview/share/locale
	rm -rf dist/mibandpreview/share/icons/Adwaita/48x48
	rm -rf dist/mibandpreview/share/icons/Adwaita/64x64
	rm -rf dist/mibandpreview/share/icons/Adwaita/96x96
	rm -rf dist/mibandpreview/share/icons/Adwaita/256x256
	rm -rf dist/mibandpreview/share/icons/Adwaita/512x512
	rm -rf dist/mibandpreview/share/icons/Adwaita/cursors
	rm -rf dist/mibandpreview/share/icons/Adwaita/scalable
	rm -rf dist/mibandpreview/share/icons/Adwaita/scalable-up-to-32
	pwd
