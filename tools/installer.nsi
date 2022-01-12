!include "MUI2.nsh"
Name "Mi Band Preview"
OutFile "mibandpreview-win64-install.exe"
Unicode True

;Default installation folder
InstallDir "$PROGRAMFILES\MelianMiko\Mi Band Preview"

;Get installation folder from registry if available
InstallDirRegKey HKCU "Software\MelianMiko Mi Band Preview" ""

;Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Dummy Section" SecDummy

  SetOutPath "$INSTDIR"
  File /r "mibandpreview\"
  
  ;Shortcuts
  CreateShortCut "$DESKTOP\Mi Band Preview.lnk" "$INSTDIR\mibandpreview.exe"
  CreateShortCut "$SMPROGRAMS\Mi Band Preview.lnk" "$INSTDIR\mibandpreview.exe"

  ;Store installation folder
  WriteRegStr HKCU "Software\MelianMiko Mi Band Preview" "" $INSTDIR
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MelianMiko_MBP" \
			"DisplayName" "Mi Band Preview"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MelianMiko_MBP" \
			"UninstallString" "$\"$INSTDIR\uninstall.exe$\""
				 
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  Delete "$INSTDIR\Uninstall.exe"
  Delete "$DESKTOP\Mi Band Preview.lnk"
  Delete "$SMPROGRAMS\Mi Band Preview.lnk"
  RMDir /r "$INSTDIR"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MelianMiko_MBP"
  DeleteRegKey /ifempty HKCU "Software\MelianMiko Mi Band Preview"

SectionEnd
