Name "MiBandPreview"
OutFile "MiBandPreview-Install.exe"
InstallDir $PROGRAMFILES\MelianMiko\MiBandPreview
DirText "This will install Mi Band Preview tool on your computer. Choose a directory"

Section ""
	SetOutPath $INSTDIR
	File /r "mibandpreview\*"
	CreateShortCut "$SMPROGRAMS\Mi Band Preview.lnk" "$INSTDIR\mibandpreview.exe"
	CreateShortCut "$DESKTOP\Mi Band Preview.lnk" "$INSTDIR\mibandpreview.exe"
	WriteUninstaller $INSTDIR\Uninstall.exe
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MiBandPreview" \
                 "DisplayName" "Mi Band Preview -- by MelianMiko"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MiBandPreview" \
                 "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
SectionEnd

Section "Uninstall"
	Delete "$SMPROGRAMS\Mi Band Preview.lnk"
	Delete "$DESKTOP\Mi Band Preview.lnk"
	DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MiBandPreview"
	RMDir /r $INSTDIR
SectionEnd

