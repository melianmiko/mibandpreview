#!/usr/bin/make -f
DESTDIR=/

all: l18n clean
all_win32: l18n windows clean

l18n:
	./tools/merge_l18ns.sh
	mkdir -p dist/locale/ru/LC_MESSAGES
	msgfmt src/l18n/ru.po -o dist/locale/ru/LC_MESSAGES/mibandpreview.mo

clean:
	rm -rf src/__pycache__
	rm -rf build

install:
	mkdir -p $(DESTDIR)/opt/mibandpreview
	mkdir -p $(DESTDIR)/usr/share/applications
	mkdir -p $(DESTDIR)/usr/share/locale
	cp tools/mi-band-preview.desktop $(DESTDIR)/usr/share/applications/mi-band-preview.desktop
	cp -r src/* $(DESTDIR)/opt/mibandpreview
	cp -r dist/locale/* $(DESTDIR)/usr/share/locale/

uninstall:
	rm $(DESTDIR)/usr/share/applications/mi-band-preview.desktop
	rm -rf $(DESTDIR)/opt/mibandpreview
	find $(DESTDIR)/usr/share/locale -name "mibandpreview.mo" -delete

deb:
	dpkg-buildpackage -sa

windows:
	export PATH=$(PATH):/mingw64/bin
	rm -rf dist/mibandpreview
	pyinstaller --name mibandpreview --icon src/res/icon.ico -w \
		--add-data "src/res;res" src/__main__.py
	mkdir dist/mibandpreview/etc
	cp -r tools/gtk-3.0 dist/mibandpreview/etc/gtk-3.0
	cp -r dist/locale/* dist/mibandpreview/share/locale
	rm -rf dist/mibandpreview/share/icons/Adwaita/48x48
	rm -rf dist/mibandpreview/share/icons/Adwaita/64x64
	rm -rf dist/mibandpreview/share/icons/Adwaita/96x96
	rm -rf dist/mibandpreview/share/icons/Adwaita/256x256
	rm -rf dist/mibandpreview/share/icons/Adwaita/512x512
	rm -rf dist/mibandpreview/share/icons/Adwaita/cursors
	rm -rf dist/mibandpreview/share/icons/Adwaita/scalable
	rm -rf dist/mibandpreview/share/icons/Adwaita/scalable-up-to-32
