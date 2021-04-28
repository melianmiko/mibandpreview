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

windows: qt
	rm -rf dist/mibandpreview
	pyinstaller --name mibandpreview --icon mibandpreview-qt/res/icon.ico -w \
		--add-data "mibandpreview/res;res" \
		--add-data "mibandpreview-qt/res;res" \
		--add-data "mibandpreview-qt/qt;qt" \
		--path "mibandpreview" --path "mibandpreview-qt" \
		--add-data "tools/gtk-3.0;etc/gtk-3.0" \
		--add-data "dist/locale;share/locale" \
		mibandpreview-qt/mibandpreview-qt
	cp tools/installer.nsi dist/installer.nsi
	cd dist && makensis installer.nsi
