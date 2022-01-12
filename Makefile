#!/usr/bin/make -f
DESTDIR=/

clean:
	rm -rf build dist mibandpreview.egg-info .files.txt debian/mibandpreview/
	rm -f ../mibandpreview_*

# Install commands
install:
	python3 setup.py install --record .files.txt --root $(DESTDIR) $(SETUP_PROPS)

uninstall:
	xargs rm -rfv < .files.txt

