#!/usr/bin/make -f
DESTDIR=/

all: qt l18n clean
all_win32: l18n windows clean

qt:
	cd mibandpreview-qt && pyuic5 qt/app.ui -o MainWindow.py
	cd mibandpreview-qt/qt && lrelease app.pro

l18n:
	./tools/merge_l18ns.sh
	mkdir -p dist/locale/ru/LC_MESSAGES
	msgfmt mibandpreview-gtk/res/l18n/ru.po -o dist/locale/ru/LC_MESSAGES/mibandpreview.mo

clean:
	rm -rf src/__pycache__
	rm -rf build

install:
	mkdir -p $(DESTDIR)/opt/mibandpreview
	mkdir -p $(DESTDIR)/opt/mibandpreview-gtk
	mkdir -p $(DESTDIR)/usr/share/applications
	mkdir -p $(DESTDIR)/usr/share/locale
	cp tools/mi-band-preview.desktop $(DESTDIR)/usr/share/applications/mi-band-preview.desktop
	cp -r mibandpreview-gtk/* $(DESTDIR)/opt/mibandpreview-gtk
	cp -r mibandpreview/* $(DESTDIR)/opt/mibandpreview
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
	pyinstaller --name mibandpreview --icon mibandpreview-gtk/res/icon.ico -w \
		--add-data "mibandpreview/res;res" \
		--path "mibandpreview" --path "mibandpreview-gtk" \
		--add-data "tools/gtk-3.0;etc/gtk-3.0" \
		--add-data "dist/locale;share/locale" \
		mibandpreview-gtk/__init__.py
	cp -r mibandpreview-gtk/res/* dist/mibandpreview/res
	cp -r /usr/share/themes/Windows-10 dist/mibandpreview/share/themes
	rm -rf dist/mibandpreview/share/icons/Adwaita/48x48
	rm -rf dist/mibandpreview/share/icons/Adwaita/64x64
	rm -rf dist/mibandpreview/share/icons/Adwaita/96x96
	rm -rf dist/mibandpreview/share/icons/Adwaita/256x256
	rm -rf dist/mibandpreview/share/icons/Adwaita/512x512
	rm -rf dist/mibandpreview/share/icons/Adwaita/cursors
	rm -rf dist/mibandpreview/share/icons/Adwaita/scalable
	rm -rf dist/mibandpreview/share/icons/Adwaita/scalable-up-to-32
	cp tools/installer.nsi dist/installer.nsi
	cd dist && makensis installer.nsi
