Name:       mydesk
Version:    1.4.7
Release:    0
Summary:    RPM package
License:    GPL-3.0
URL:        https://mydesk.com
Vendor:     mydesk <info@mydesk.com>
Requires:   gtk3 libxcb1 libXfixes3 alsa-utils libXtst6 libva2 pam gstreamer-plugins-base gstreamer-plugin-pipewire
Recommends: libayatana-appindicator3-1 xdotool
Provides:   libdesktop_drop_plugin.so()(64bit), libdesktop_multi_window_plugin.so()(64bit), libfile_selector_linux_plugin.so()(64bit), libflutter_custom_cursor_plugin.so()(64bit), libflutter_linux_gtk.so()(64bit), libscreen_retriever_plugin.so()(64bit), libtray_manager_plugin.so()(64bit), liburl_launcher_linux_plugin.so()(64bit), libwindow_manager_plugin.so()(64bit), libwindow_size_plugin.so()(64bit), libtexture_rgba_renderer_plugin.so()(64bit)

# https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/

%description
The best open-source remote desktop client software, written in Rust.

%prep
# we have no source, so nothing here

%build
# we have no source, so nothing here

# %global __python %{__python3}

%install

mkdir -p "%{buildroot}/usr/share/mydesk" && cp -r ${HBB}/flutter/build/linux/x64/release/bundle/* -t "%{buildroot}/usr/share/mydesk"
mkdir -p "%{buildroot}/usr/bin"
install -Dm 644 $HBB/res/mydesk.service -t "%{buildroot}/usr/share/mydesk/files"
install -Dm 644 $HBB/res/mydesk.desktop -t "%{buildroot}/usr/share/mydesk/files"
install -Dm 644 $HBB/res/mydesk-link.desktop -t "%{buildroot}/usr/share/mydesk/files"
install -Dm 644 $HBB/res/128x128@2x.png "%{buildroot}/usr/share/icons/hicolor/256x256/apps/mydesk.png"
install -Dm 644 $HBB/res/scalable.svg "%{buildroot}/usr/share/icons/hicolor/scalable/apps/mydesk.svg"

%files
/usr/share/mydesk/*
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
ln -sf /usr/share/mydesk/mydesk /usr/bin/mydesk
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
    rm /usr/bin/mydesk || true
    rmdir /usr/lib/mydesk || true
    rmdir /usr/local/mydesk || true
    rmdir /usr/share/mydesk || true
    rm /usr/share/applications/mydesk.desktop || true
    rm /usr/share/applications/mydesk-link.desktop || true
    update-desktop-database
  ;;
  1)
    # for upgrade
    rmdir /usr/lib/mydesk || true
    rmdir /usr/local/mydesk || true
  ;;
esac
