#!/bin/bash
cd src/l18n
intltool-extract --type=gettext/glade ../res/app.glade
xgettext --keyword=N_ --output=LC.pot ../res/app.glade.h

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
rm LC.pot ../res/app.glade.h
