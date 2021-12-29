%global srcname copr-tito-quickdoc

Name: mibandpreview
Version: 0.9
Release: 1
License: Apache-2.0
Summary: Mi Band 4/5/6 watchface preview tool
Url: https://github.com/melianmiko/mibandpreview
Source0: %{name}-%{version}.tar.gz

BuildArch: noarch

BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: qt5-qtbase-devel
BuildRequires: qt5-linguist
BuildRequires: python3-qt5-base
Requires: python3-qt5-base
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
* Wed Dec 29 2021 MelianMiko <melianmiko@gmail.com> 0.9-1
- Refactor (melianmiko@gmail.com)
- Added rotate option (melianmiko@gmail.com)

* Fri Nov 26 2021 MelianMiko <melianmiko@gmail.com> 0.8.3-1
- Fixes 0.8.3 (melianmiko@gmail.com)

* Fri Nov 26 2021 MelianMiko <melianmiko@gmail.com> 0.8.2-2
- v0.8.2 (melianmiko@gmail.com)

* Fri Nov 26 2021 MelianMiko <melianmiko@gmail.com> 0.8.2-1
- Code deduplication (melianmiko@gmail.com)
- Added calories and heart LineScale support (melianmiko@gmail.com)
- Automatic commit of package [mibandpreview] release [0.8.1-1].
  (melianmiko@gmail.com)

* Fri Nov 05 2021 MelianMiko <melianmiko@gmail.com> 0.8.1-1
- new package built with tito


