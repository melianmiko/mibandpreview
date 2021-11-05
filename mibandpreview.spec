%global srcname copr-tito-quickdoc

Name: mibandpreview
Version: 0.8.1
Release: 0%{?dist}
License: Apache-2.0
Summary: Mi Band 4/5/6 watchface preview tool
Url: https://github.com/melianmiko/mibandpreview
Source0: %{name}-%{version}.tar.gz

BuildArch: noarch

BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: qt5-qtbase-devel
BuildRequires: qt5-linguist
Requires: python3-pyqt5-sip
Requires: python3-pillow
Requires: python3-certifi
Requires: python3

%description
Watchface preview tool, written in Python3 + PyQt5. You can use this tool to preview your
Mi Band custom watchface without compiling.

#-- PREP, BUILD & INSTALL -----------------------------------------------------#
%prep
%autosetup

%build
PATH=$PATH:/usr/lib64/qt5/bin make

%install
make install DESTDIR=%{buildroot}

#-- FILES ---------------------------------------------------------------------#
%files
/usr/share/icons/hicolor/96x96/apps/mibandpreview-qt.png
/usr/share/applications/mibandpreview-qt.desktop
%{python3_sitelib}/%{name}-*.egg-info/
%{python3_sitelib}/%{name}_qt/
%{python3_sitelib}/%{name}/

#-- CHANGELOG -----------------------------------------------------------------#
%changelog

