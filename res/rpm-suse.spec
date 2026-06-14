Name:       mydesk
Version:    1.1.9
Release:    0
Summary:    RPM package
License:    GPL-3.0
Requires:   gtk3 libxcb1 libXfixes3 alsa-utils libXtst6 libva2 pam gstreamer-plugins-base gstreamer-plugin-pipewire
Recommends: libayatana-appindicator3-1 xdotool

# https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/

%description
The best open-source remote desktop client software, written in Rust.

%prep
# we have no source, so nothing here

%build
# we have no source, so nothing here

%global __python %{__python3}

%install
mkdir -p %{buildroot}/usr/bin/
mkdir -p %{buildroot}/usr/share/mydesk/
mkdir -p %{buildroot}/usr/share/mydesk/files/
mkdir -p %{buildroot}/usr/share/icons/hicolor/256x256/apps/
mkdir -p %{buildroot}/usr/share/icons/hicolor/scalable/apps/
install -m 755 $HBB/target/release/mydesk %{buildroot}/usr/bin/mydesk
install $HBB/libsciter-gtk.so %{buildroot}/usr/share/mydesk/libsciter-gtk.so
install $HBB/res/mydesk.service %{buildroot}/usr/share/mydesk/files/
install $HBB/res/128x128@2x.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/mydesk.png
install $HBB/res/scalable.svg %{buildroot}/usr/share/icons/hicolor/scalable/apps/mydesk.svg
install $HBB/res/mydesk.desktop %{buildroot}/usr/share/mydesk/files/
install $HBB/res/mydesk-link.desktop %{buildroot}/usr/share/mydesk/files/

%files
/usr/bin/mydesk
/usr/share/mydesk/libsciter-gtk.so
/usr/share/mydesk/files/mydesk.service
/usr/share/icons/hicolor/256x256/apps/mydesk.png
/usr/share/icons/hicolor/scalable/apps/mydesk.svg
/usr/share/mydesk/files/mydesk.desktop
/usr/share/mydesk/files/mydesk-link.desktop

%changelog
# let's skip this for now

%pre
# can do something for centos7
case "$1" in
  1)
    # for install
  ;;
  2)
    # for upgrade
    systemctl stop mydesk || true
  ;;
esac

%post
cp /usr/share/mydesk/files/mydesk.service /etc/systemd/system/mydesk.service
cp /usr/share/mydesk/files/mydesk.desktop /usr/share/applications/
cp /usr/share/mydesk/files/mydesk-link.desktop /usr/share/applications/
systemctl daemon-reload
systemctl enable mydesk
systemctl start mydesk
update-desktop-database

%preun
case "$1" in
  0)
    # for uninstall
    systemctl stop mydesk || true
    systemctl disable mydesk || true
    rm /etc/systemd/system/mydesk.service || true
  ;;
  1)
    # for upgrade
  ;;
esac

%postun
case "$1" in
  0)
    # for uninstall
    rm /usr/share/applications/mydesk.desktop || true
    rm /usr/share/applications/mydesk-link.desktop || true
    update-desktop-database
  ;;
  1)
    # for upgrade
  ;;
esac
