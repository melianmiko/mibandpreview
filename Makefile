#!/usr/bin/make -f
DESTDIR=/

all: qt clean

qt:
	cd mibandpreview_qt && pyuic5 qt/app.ui -o MainWindow.py
	cd mibandpreview_qt/qt && lupdate app.pro && lrelease app.pro

clean:
	rm -rf build dist mibandpreview.egg-info .files.txt debian/mibandpreview/

install:
	python3 setup.py install --record .files.txt --root $(DESTDIR) $(SETUP_PROPS)
	mkdir -p $(DESTDIR)/usr/share/icons/hicolor/96x96/apps
	mkdir -p $(DESTDIR)/usr/share/applications
	cp mibandpreview_qt/res/mibandpreview-qt.png $(DESTDIR)/usr/share/icons/hicolor/96x96/apps
	cp mibandpreview_qt/res/mibandpreview-qt.desktop $(DESTDIR)/usr/share/applications

uninstall:
	xargs rm -rfv < .files.txt
	rm -f /usr/share/applications/mibandpreview-qt.desktop
	rm -f /usr/share/icons/hicolor/96x96/apps/mibandpreview-qt.png

windows:
	rm -rf dist/mibandpreview
	pyinstaller --name mibandpreview --icon mibandpreview_qt/res/icon.ico -w \
		--specpath ~ \
		--hidden-import=certifi \
		--add-data "mibandpreview/res;mibandpreview/res" \
		--add-data "mibandpreview_qt/res;mibandpreview_qt/res" \
		--add-data "mibandpreview_qt/qt;mibandpreview_qt/qt" \
		scripts/win32-entrypoint.py
	cp tools/installer.nsi dist/installer.nsi
	cd dist && makensis installer.nsi

