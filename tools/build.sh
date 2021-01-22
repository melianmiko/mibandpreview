#!/bin/bash

mkmo() {
	mkdir -p $1/LC_MESSAGES
	msgfmt $1.po -o $1/LC_MESSAGES/app.mo
}

mkmo ru
mkmo en_US
