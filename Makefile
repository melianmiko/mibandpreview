#!/usr/bin/make -f
DESTDIR=/

all: clean

clean:
	rm -rf src/__pycache__

install:
	mkdir -p $(DESTDIR)/opt/mibandpreview
	mkdir -p $(DESTDIR)/usr/share/applications
	cp -r src/* $(DESTDIR)/opt/mibandpreview
	ln -sf $(DESTDIR)/opt/mibandpreview/mi-band-preview.desktop $(DESTDIR)/usr/share/applications/mi-band-preview.desktop

uninstall:
	rm $(DESTDIR)/usr/share/applications/mi-band-preview.desktop
	rm -rf $(DESTDIR)/opt/mibandpreview

debian:
	dpkg-buildpackage

windows:
	export PATH=$PATH:/mingw64/bin
	pyinstaller --name mibandpreview --icon src/res/icon.ico \
		--add-data "src/res;res" --add-data "src/app.glade;app.glade" \
		--add-data "src/locale;locale" \
		src/GtkUi.py
