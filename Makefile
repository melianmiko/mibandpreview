#!/usr/bin/make -f
DESTDIR=/
RELEASE_DIR=${HOME}/releases

all: qt

clean:
	rm -rf build dist mibandpreview.egg-info .files.txt debian/mibandpreview/

# Install commands
install: qt
	python3 setup.py install --record .files.txt --root $(DESTDIR) $(SETUP_PROPS)
	mkdir -p $(DESTDIR)/usr/share/icons/hicolor/96x96/apps
	mkdir -p $(DESTDIR)/usr/share/applications
	cp mibandpreview_qt/res/mibandpreview-qt.png $(DESTDIR)/usr/share/icons/hicolor/96x96/apps
	cp mibandpreview_qt/res/mibandpreview-qt.desktop $(DESTDIR)/usr/share/applications

uninstall:
	xargs rm -rfv < .files.txt
	rm -f /usr/share/applications/mibandpreview-qt.desktop
	rm -f /usr/share/icons/hicolor/96x96/apps/mibandpreview-qt.png

# Build commands
qt:
	cd mibandpreview_qt && pyuic5 qt/app.ui -o MainWindow.py
	cd mibandpreview_qt/qt && lupdate app.pro && lrelease app.pro

win32:
	rm -rf dist/mibandpreview
	mv mibandpreview.spec .mibandpreview.spec
	pyinstaller --name mibandpreview --icon mibandpreview_qt/res/icon.ico -w \
		--hidden-import=certifi \
		--add-data "mibandpreview/res;mibandpreview/res" \
		--add-data "mibandpreview_qt/res;mibandpreview_qt/res" \
		--add-data "mibandpreview_qt/qt;mibandpreview_qt/qt" \
		scripts/win32-entrypoint.py
	mv .mibandpreview.spec mibandpreview.spec

win32_nsis: win32
	cp tools/installer.nsi dist/installer.nsi
	cd dist && makensis installer.nsi

# Release commands
rpm: clean all
	mkdir -p ${RELEASE_DIR}/rpm
	tito build --rpm --test --output=${RELEASE_DIR}/rpm
	mv ${RELEASE_DIR}/rpm/noarch/mibandpreview-* ${RELEASE_DIR}/rpm

wheel: clean qt
	mkdir -p ${RELEASE_DIR}/wheel
	python3 setup.py bdist_wheel -d ${RELEASE_DIR}/wheel

deb: clean qt
	mkdir -p ${RELEASE_DIR}/deb
	dpkg-buildpackage -S
	dpkg-buildpackage -b
	mv ../mibandpreview_* ${RELEASES_DIR}/deb

exe: clean qt win32_nsis
	mkdir -p ${RELEASES_DIR}/windows
	mv dist/*.exe ${RELEASES_DIR}/windows


