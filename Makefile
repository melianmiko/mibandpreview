#!/usr/bin/make -f
DESTDIR=/

all: qt clean

qt:
	cd mibandpreview-qt && pyuic5 qt/app.ui -o MainWindow.py
	cd mibandpreview-qt/qt && lrelease app.pro

clean:
	rm -rf build

install:
	mkdir -p $(DESTDIR)/opt/mibandpreview
	mkdir -p $(DESTDIR)/opt/mibandpreview-qt
	mkdir -p $(DESTDIR)/usr/share/applications
	cp tools/mibandpreview-qt.desktop $(DESTDIR)/usr/share/applications/mibandpreview-qt.desktop
	cp -r mibandpreview-qt/* $(DESTDIR)/opt/mibandpreview-qt
	cp -r mibandpreview/* $(DESTDIR)/opt/mibandpreview

uninstall:
	rm $(DESTDIR)/usr/share/applications/mibandpreview-qt.desktop
	rm -rf $(DESTDIR)/opt/mibandpreview

deb:
	dpkg-buildpackage -sa

windows: qt
	rm -rf dist/mibandpreview
	pyinstaller --name mibandpreview --icon mibandpreview-qt/res/icon.ico -w \
		--add-data "mibandpreview/res;res" \
		--add-data "mibandpreview-qt/res;res" \
		--add-data "mibandpreview-qt/qt;qt" \
		--path "mibandpreview" --path "mibandpreview-qt" \
		mibandpreview-qt/mibandpreview-qt
	cp tools/installer.nsi dist/installer.nsi
	cd dist && makensis installer.nsi
