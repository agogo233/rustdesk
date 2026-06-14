# MyDesk 品牌变更修复方案

> 目的：将 RustDesk 项目更名为 MyDesk，以避免特征识别拦截。
> 核心原则：**只改客户端品牌表现，不改网络基础设施连接**。

---

## 一、已确认不做改动的项

| 模块 | 理由 |
|------|------|
| `RENDEZVOUS_SERVERS` (`rs-ny.rustdesk.com`) | 仍连接 RustDesk 公网基础设施 |
| `RS_PUB_KEY` | 公钥不变 |
| `api.rustdesk.com` (版本检查) | 仍用 RustDesk API |
| `is_public()` 函数 | 仍识别 rustdesk.com 为官方服务器（期望行为） |
| `is_custom_client()` 返回 true | 这正是改名想要的效果——看起来不像官方客户端 |
| Firebase / GoogleService-Info.plist | 不迁移，保持原样 |
| 代码签名证书 (macOS/Windows) | 改后不签名 |
| RustDeskIddDriver 虚拟显示器驱动 | 设备字符串、驱动名保持原样 |
| GitHub `rustdesk-org/*` 依赖源 | 无法修改，必须引用上游 |
| 注释中的 GitHub 问题链接 | 只影响日志/错误消息，不影响运行 |

---

## 二、P0 — 构建/打包阻断（不改则编译/打包失败）

### 2.1 `build.py` 所有 `rustdesk` → `mydesk`

| 行号 | 当前内容 | 改为 |
|------|---------|------|
| 17 | `hbb_name = 'rustdesk'` | `hbb_name = 'mydesk'` |
| 296-302 | `Package: rustdesk` / `rustdesk <info@rustdesk.com>` / `https://rustdesk.com` | `Package: mydesk` / `mydesk <info@mydesk.com>` / `https://mydesk.com` |
| 326-329 | `usr/share/rustdesk` / `etc/rustdesk/` | `usr/share/mydesk` / `etc/mydesk/` |
| 334-364 | `rustdesk.service`, `rustdesk.desktop`, `rustdesk-link.desktop`, `rustdesk.deb` | `mydesk.service`, `mydesk.desktop`, `mydesk-link.desktop`, `mydesk.deb` |
| 371-401 | server-only deb：同上 | 同上 |
| 412 | `librustdesk.dylib` | `libmydesk.dylib` |
| 420-424 | `RustDesk.app`, `rustdesk.dmg`, `"RustDesk Installer"` | `MyDesk.app`, `mydesk.dmg`, `"MyDesk Installer"` |
| 435 | `librustdesk.so` | `libmydesk.so` |
| 456-466 | `rustdesk.exe`, `rustdesk_portable.exe`, `rustdesk-{version}-install.exe` | `mydesk.exe`, `mydesk_portable.exe`, `mydesk-{version}-install.exe` |
| 506 | `mv .../rustdesk.exe .../RustDesk.exe` | `mv .../mydesk.exe .../MyDesk.exe` |
| 517 | `target/release/RustDesk.exe` | `target/release/MyDesk.exe` |
| 521 | `rustdesk-{version}-win7-install.exe` | `mydesk-{version}-win7-install.exe` |
| 531 | `target/release/rustdesk` | `target/release/mydesk` |
| 534-535 | `rustdesk-%s-0-x86_64.pkg.tar.zst` / `rustdesk-%s-manjaro-arch.pkg.tar.zst` | `mydesk-%s-*` |
| 539 | `target/release/rustdesk` | `target/release/mydesk` |
| 541-556 | rpm 包名/产物名中的 `rustdesk` | `mydesk` |
| 590-603 | `rustdesk-{version}.dmg` / `RustDesk.app` | `mydesk-{version}.dmg` / `MyDesk.app` |
| 608-638 | deb repack 中所有 `rustdesk` | `mydesk` |

### 2.2 Flutter Android 包名

| 文件 | 当前值 | 改为 |
|------|--------|------|
| `flutter/android/app/build.gradle:100` | `applicationId "com.carriez.flutter_hbb"` | `applicationId "com.mydesk.mydesk"` |
| `src/main/AndroidManifest.xml:3` | `package="com.carriez.flutter_hbb"` | `package="com.mydesk.mydesk"` |
| `src/debug/AndroidManifest.xml:2` | 同上 | 同上 |
| `src/profile/AndroidManifest.xml:2` | 同上 | 同上 |
| `src/main/AndroidManifest.xml:41` | `com.carriez.flutter_hbb.DEBUG_BOOT_COMPLETED` | `com.mydesk.mydesk.DEBUG_BOOT_COMPLETED` |
| `BootReceiver.kt:14` | `DEBUG_BOOT_COMPLETED = "com.carriez.flutter_hbb..."` | `"com.mydesk.mydesk..."` |
| 12 个 `.kt` 文件 | `package com.carriez.flutter_hbb` | `package com.mydesk.mydesk` |

> **注意**：Android keystore 通过 `flutter/android/key.properties` 由 CI/开发者本地提供（不在仓库中）。改包名后需用新 keystore。

### 2.3 Flutter macOS 配置

| 文件 | 当前值 | 改为 |
|------|--------|------|
| `AppInfo.xcconfig:8` | `PRODUCT_NAME = RustDesk` | `PRODUCT_NAME = MyDesk` |
| `project.pbxproj:448,593,630` | `PRODUCT_BUNDLE_IDENTIFIER = com.carriez.rustdesk` | `com.mydesk.mydesk` |
| `Info.plist:29` | `CFBundleURLName = com.carriez.rustdesk` | `com.mydesk.mydesk` |
| `MainMenu.xib:16,333` | `customModule="RustDesk"` | `customModule="MyDesk"` |

### 2.4 Flutter iOS 配置

| 文件 | 当前值 | 改为 |
|------|--------|------|
| `project.pbxproj:437,633,721` | `PRODUCT_BUNDLE_IDENTIFIER = com.carriez.flutterHbb` | `com.mydesk.mydesk` |
| `exportOptions.plist:11` | `com.carriez.flutterHbb` | `com.mydesk.mydesk` |
| `GoogleService-Info.plist:16` | `com.carriez.flutterHbb` | `com.mydesk.mydesk` |

### 2.5 Flutter Linux 配置

| 文件 | 当前值 | 改为 |
|------|--------|------|
| `flutter/linux/CMakeLists.txt:10` | `APPLICATION_ID "com.carriez.flutter_hbb"` | `APPLICATION_ID "com.mydesk.mydesk"` |

---

## 三、P1 — 运行时可恢复（不影响编译，但用户可见）

### 3.1 安装/打包脚本

| 文件 | 内容 | 操作 |
|------|------|------|
| `res/pacman_install` | 全部 8 个 `rustdesk.service/desktop` 引用 | 改为 `mydesk.*` |
| `res/rpm.spec:6-7` | `URL: https://rustdesk.com`, `Vendor: rustdesk` | 改为 mydesk.com / mydesk |
| `res/rpm-flutter.spec:6-7` | 同上 | 同上 |
| `res/rpm-flutter-suse.spec:6-7` | 同上 | 同上 |
| `res/rpm-suse.spec:6-7` | 同上 | 同上 |

### 3.2 MSI Windows 安装程序

| 文件 | 内容 | 操作 |
|------|------|------|
| `res/msi/preprocess.py:30,34,38` | `github.com/rustdesk/rustdesk` | 改为新仓库 URL |
| `res/msi/preprocess.py:498-499` | 许可证替换逻辑中的 rustdesk.com | 改为 mydesk.com |
| `AddRemoveProperties.wxs:19-23` | ARPCONTACT/ARPHELPLINK 等全部 rustdesk | 改为 mydesk |
| `Package.en-us.wxl:54` | `"Start RustDesk on system startup"` | `"Start MyDesk on system startup"` |
| `WixExt_en-us.wxl:13` | `"Adapted by RustDesk for..."` | `"Adapted by MyDesk for..."` |
| `License.rtf` | 全文中的 "rustdesk.com" / "RustDesk" | 替换为 "mydesk.com" / "MyDesk" |

---

## 四、P2 — 外观/品牌一致性（用户体验相关）

### 4.1 macOS 权限脚本

| 文件 | 当前值 | 改为 |
|------|--------|------|
| `install.scpt:3,5,7,9,11` | `com.carriez.RustDesk_*` | `com.mydesk.MyDesk_*` |
| `install.scpt:15` | `"RustDesk wants to install..."` | `"MyDesk wants to install..."` |
| `uninstall.scpt:1-3` | `com.carriez.RustDesk_*` | `com.mydesk.MyDesk_*` |
| `update.scpt:3-4` | `com.carriez.RustDesk_*` | `com.mydesk.MyDesk_*` |
| `daemon.plist:6,9,19,24,26,28` | `com.carriez.RustDesk_service`, `/Applications/RustDesk.app`, `/tmp/rustdesk_service.*`, `com.carriez.rustdesk` | `com.mydesk.MyDesk_service`, `/Applications/MyDesk.app`, `/tmp/mydesk_service.*`, `com.mydesk.mydesk` |
| `agent.plist:6,9,29,33` | `com.carriez.RustDesk_server`, `com.carriez.rustdesk`, `/Applications/RustDesk.app` | `com.mydesk.MyDesk_server`, `com.mydesk.mydesk`, `/Applications/MyDesk.app` |

### 4.2 Flutter Dart 代码中的外部 URL

| 文件 | 当前内容 | 改为 |
|------|---------|------|
| `flutter/lib/desktop/pages/desktop_home_page.dart:440` | `rustdesk.com/download` | `mydesk.com/download` |
| `flutter/lib/desktop/pages/desktop_home_page.dart:456` | `github.com/rustdesk/rustdesk/releases` | 新仓库 releases |
| `flutter/lib/desktop/pages/desktop_home_page.dart:533,544,550` | `rustdesk.com/docs/en/...` | `mydesk.com/docs/en/...` |
| `flutter/lib/desktop/pages/desktop_setting_page.dart:2458` | `rustdesk.com/privacy.html` | `mydesk.com/privacy.html` |
| `flutter/lib/desktop/pages/desktop_setting_page.dart:2466` | `rustdesk.com` | `mydesk.com` |
| `flutter/lib/desktop/pages/connection_page.dart:44` | `rustdesk.com/pricing` | `mydesk.com/pricing` |
| `flutter/lib/desktop/pages/install_page.dart:190,192` | `rustdesk.com/privacy.html` | `mydesk.com/privacy.html` |
| `flutter/lib/mobile/pages/settings_page.dart:39,988,1101` | `rustdesk.com` / `rustdesk.com/privacy.html` | `mydesk.com` / `mydesk.com/privacy.html` |
| `flutter/lib/mobile/pages/connection_page.dart:127` | `rustdesk.com/download` | `mydesk.com/download` |
| `flutter/lib/common.dart:3700` | `launchUrl(Uri.parse('https://rustdesk.com'))` | `launchUrl(Uri.parse('https://mydesk.com'))` |
| `flutter/lib/common.dart:2430-2432` | `// rustdesk://<connect-id>` (注释) | `// mydesk://<connect-id>` |
| `flutter/lib/desktop/pages/desktop_setting_page.dart:2666` | `// "RustDesk" -> "Permissions"` (注释) | `// "MyDesk" -> ...` |

### 4.3 Rust 代码中的文档/帮助 URL

| 文件 | 当前内容 | 改为 |
|------|---------|------|
| `libs/hbb_common/src/config.rs:100-110` | `LINK_DOCS_HOME 等 → rustdesk.com` | `mydesk.com` |
| `src/client.rs:132` | `SCRAP_X11_REF_URL → rustdesk.com` | `mydesk.com` |
| `src/client.rs:3332` | `link: "rustdesk.com/docs/..."` | `mydesk.com` |
| `src/lang/en.rs:92` | `"doc_mac_permission" URL` | `mydesk.com` |
| `src/lang/en.rs:199` | `"doc_fix_wayland" URL` | `mydesk.com` |
| `src/common.rs:1034` | `"https://admin.rustdesk.com"` | `"https://admin.mydesk.com"` |

### 4.4 Sciter UI（`src/ui/`，已废弃但仍有引用）

| 文件 | 行号 | 当前内容 | 改为 |
|------|------|---------|------|
| `src/ui/index.tis` | 96 | `rustdesk.com/blog/id-relay-set/` | `mydesk.com/blog/id-relay-set/` |
| `src/ui/index.tis` | 604-605 | `rustdesk.com/privacy.html` | `mydesk.com/privacy.html` |
| `src/ui/index.tis` | 837,840 | `rustdesk.com` / `rustdesk.com/download` | `mydesk.com` / `mydesk.com/download` |
| `src/ui/index.tis` | 1346 | `rustdesk.com` | `mydesk.com` |
| `src/ui/index.tis` | 1562,1615 | `url.indexOf('rustdesk')` URL 校验 | `mydesk` |
| `src/ui/install.tis` | 53 | `rustdesk.com/privacy` | `mydesk.com/privacy` |

---

## 五、P3 — 辅助项（不影响功能但建议改）

### 5.1 运行时标识符

| 文件 | 当前 | 改为 |
|------|------|------|
| `libs/hbb_common/src/config.rs:57` | `ORG = "com.carriez"` (macOS 配置目录用) | `"com.mydesk"` |
| `Cargo.toml:236` | `identifier = "com.carriez.mydesk"` | `"com.mydesk.mydesk"` |
| `libs/clipboard/src/platform/unix/serv_files.rs:327` | `"rustdesk_sig_test_"` 临时文件 | `"mydesk_sig_test_"` |

### 5.2 Flatpak 元数据

`flatpak/com.mydesk.MyDesk.metainfo.xml` 中所有 8 个 `<url>` 标签（homepage, bugtracker, faq, help, donation, vcs-browser 等）改为 mydesk.com。

### 5.3 CI/GitHub 基础设施

| 文件 | 内容 | 操作 |
|------|------|------|
| `.github/ISSUE_TEMPLATE/bug_report.yaml:38-39` | `"RustDesk Version(s)"` | `"MyDesk Version(s)"` |
| `.github/ISSUE_TEMPLATE/config.yml:4,7` | `github.com/rustdesk/rustdesk/discussions` | 新仓库 discussions |
| `.github/FUNDING.yml:1-2` | `github: [rustdesk]`, `ko_fi: rustdesk` | 改为新赞助链接 |
| `.github/workflows/build.yml:174` | SHA256 校验 `rustdesk_printer_driver_v4` | 改文件名后同步改校验模式 |

### 5.4 README 文件

所有 `README.md` 和 `docs/README-*.md` (约 17 个文件) 中的 F-Droid 下载徽章链接中包含 `com.carriez.flutter_hbb`，需改为 `com.mydesk.mydesk`。

---

## 六、执行顺序

```
Phase 1: 构建修复（阻断）
  ├── build.py (33 处替换)
  ├── 安卓包名 + Kotlin package (15 个文件)
  ├── macOS Xcode 配置 (4 个文件)
  ├── iOS Xcode 配置 (3 个文件)
  └── Linux CMakeLists.txt
  └── 验证：cargo build + flutter build

Phase 2: 安装/打包
  ├── pacman_install
  ├── rpm .spec 文件 (×4)
  └── MSI Windows 安装程序 (6 个文件)
  └── 验证：build.py 执行

Phase 3: macOS 服务脚本
  ├── daemon.plist + agent.plist
  ├── install.scpt + uninstall.scpt + update.scpt
  └── 验证：osascript 语法检查

Phase 4: 品牌一致性
  ├── Flutter Dart URL (14 处)
  ├── Rust 文档 URL (6 处)
  ├── Sciter UI URL (7 处)
  └── ORG + Cargo.toml identifier + 临时文件名
  └── 验证：cargo build + flutter build

Phase 5: 辅助清理
  ├── Flatpak 元数据
  ├── CI/ISSUE_TEMPLATE
  ├── README 文件
  └── .github/workflows
  └── 验证：人工审查
```

## 七、验证清单

| 检查项 | 命令/方式  | 预期结果 |
|--------|-----------|----------|
| Rust 编译 | `cargo build --release` | 输出 `target/release/mydesk` |
| Flutter Linux | `flutter build linux --release` | bundle 中无 rustdesk 引用 |
| Flutter Windows | `flutter build windows --release` | .exe 名为 mydesk.exe |
| Flutter macOS | `flutter build macos --release` | app 名为 MyDesk.app |
| deb 包 | `build.py` deb 构建 | 包名 mydesk，路径 usr/share/mydesk |
| Android APK | `flutter build apk` | applicationId 为 com.mydesk.mydesk |
| macOS plist | 检查 `install.scpt` 输出的文件 | Label 为 com.mydesk.MyDesk_service |
| macOS 权限提示 | `install.scpt:15` | 提示 "MyDesk wants to install..." |
