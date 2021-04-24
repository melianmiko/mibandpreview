#!/bin/bash
cd mibandpreview-gtk/res/l18n
intltool-extract --type=gettext/glade ../app.glade
xgettext --keyword=N_ --output=LC.pot ../app.glade.h

merge() {
	if [[ ! -f $1.po ]]
	then
		msginit --locale $1 --input LC.pot
	fi
	msgmerge -U $1.po LC.pot
}

# Lost locales
merge ru

# Cleanup
rm LC.pot ../app.glade.h
