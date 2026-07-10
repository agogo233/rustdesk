# UPSTREAM MERGE PROMPT — Mod 分支独有变更总览

> 生成时间: 2026-07-09
> 分叉起点: `upstream/master` — `4a54029c` fix(update): msi, norestart (#15440)
> 本地 HEAD: `origin/Mod` — `c48561754` Merge upstream/master into Mod (2026-07-09)
> 上游 HEAD: `upstream/master` — `29e1852a6` fix: ci: macos: allow signed but not notarized dmg (#15530)
> 已合入上游提交: `493b14ba7` ~ `29e1852a6`（8 commits: 1.4.9 bump + non-E2EE dialog + remove cli feature + harden wf_cliprdr + Korean + Italian + force TLS + macOS CI）
> 待合入上游提交: —（无）

---

## 一、品牌重命名 RustDesk → MyDesk（核心改动，~20 提交）

### Phase 1 — 运行时字符串重命名
**提交**: `ec5f73d3c`

- clipboard: owner format、临时文件前缀
- dbus: service name → `org.mydesk.mydesk`
- terminal: pipe names
- env vars: `RUSTDESK_APPNAME` → `MYDESK_APPNAME` 等
- portable: binary identifier、进程名 `RuntimeBroker`
- plugin: `MSG_TO_RUSTDESK_TARGET`
- virtual display: `idd_impl` string、module name
- UI: install paths、error messages、FUSE name、printer temp
- download URL patterns
- `Cargo.toml`: lib 名 `librustdesk` → `libmydesk`
- bin imports: `use libmydesk` 替代 `use librustdesk`

### Phase 2 — FFI 符号 + 平台通道重命名
**提交**: `516ca70e9`

- Rust FFI: `rustdesk_core_main` → `mydesk_core_main`
- Rust FFI: `get_rustdesk_app_name` → `get_mydesk_app_name`
- Linux: `librustdesk.so` → `libmydesk.so`, `BINARY_NAME` rustdesk → mydesk
- Linux: platform channel `org.rustdesk.rustdesk` → `org.mydesk.mydesk`
- Linux: window title, icon name, side button channel
- Windows: `librustdesk.dll` → `libmydesk.dll`, typedef + `GetProcAddress`
- Windows: platform channel `org.rustdesk.rustdesk` → `org.mydesk.mydesk`
- macOS: `mydesk_core_main()`, `MyDeskPlugin`, channel name
- macOS/iOS: `pbxproj` `liblibrustdesk` → `liblibmydesk`
- Android: `loadLibrary rustdesk` → `mydesk`, notify title, wakelock tag
- Dart: platform channels, class names, UI strings, URI scheme
- Dart: `native_model.dart` lib paths, virtual display constants

### Phase 3 — 打包脚本重命名
**提交**: `3f92859d8`

- Desktop files: `rustdesk.desktop` → `mydesk.desktop`
- Service file: `rustdesk.service` → `mydesk.service`
- RPM spec 文件: 全部路径/名称 → mydesk
- PKGBUILD: `pkgname`, paths → mydesk
- `build.py`: 全部 install paths, deb/dmg/rpm 文件名, app 引用 → mydesk
- DEBIAN scripts: `preinst/postinst/prerm/postrm` 路径 → mydesk
- flatpak: `com.rustdesk.RustDesk` → `com.mydesk.MyDesk`
- `osx-dist.sh`: `RustDesk.app`, dmg names → MyDesk/mydesk
- `job.py`: `RustDeskPrinterDriver` → `MyDeskPrinterDriver`
- MSI `preprocess.py`: default app MyDesk, component wxs rename
- pam.d: `rustdesk.debian/suse` → `mydesk.debian/suse`

### Phase 4 — 剩余符号修正 + 修复
- `f2c788c0f`: `RUSTDESK_IDD_DEVICE_STRING` → `MYDESK_IDD_DEVICE_STRING`
- `8038d2bd9`: 修复 `settings_page.dart` rebrand 语法错误
- `0d420e156`: 同步 `build.yml` artifact names 和 lib 路径
- `353fd3ec3`: 修正 Android `.so` 路径 `libmydesk` → `liblibmydesk`
- `5ce390256`: CI 构建后检测 `libmydesk.dll` 代替 `librustdesk.dll`
- `1c5ab5d88`: 补全剩余 REBRAND_PLAN — Runner.xcscheme, License.rtf, config.rs
- `2719fb4bf`: `RUSTDESK_IDD_DEVICE_STRING` → `MYDESK_IDD_DEVICE_STRING`（二次修复）

### 全库字符串替换
- `74225f895`: `chore: rebrand RustDesk to MyDesk across codebase`
- `343fcf891`: `chore: rebrand RustDesk to MyDesk across translations and build scripts`
- `de7e1e661`: `fix: rename Dart class RustdeskImpl->MydeskImpl for crate rename`
- `dc27c61a6`: `fix: update binary/exe names in build scripts for mydesk rename`
- `4bede06b1`: `fix(ci): 更新 MSI 构建脚本适配 mydesk 重命名`

### 回退 / 兼容
- `40f7c3147`: IDD 驱动名回退到 `RustDeskIddDriver`（`.inf` 兼容性）
- `6a65e097f`: `is_custom_client` 检查回退到 `!= "RustDesk"`（MyDesk 被视作 custom client）

### 依赖库重命名（hbb_common）
- `af38389a5`: 同步子模块指针到含运行时字符串重命名的 hbb_common
- `a203de4`（hbb_common）: rename runtime strings rustdesk→mydesk in hbb_common
- `4d9c818`（hbb_common）: rebrand HELPER_URL hashmap keys from rustdesk to mydesk

---

## 二、CI/CD 工作流定制（~13 提交）

### Workflow 精简与重写
- `fd6c5eb84`: 精简 workflow，仅保留 Win x86_64 和 Android arm64 构建
- `477e460c6`: Win 构建增加 ZIP 绿色包输出
- `11f35bfaf`: 上传 Windows release artifacts (exe/msi/zip)
- `35e01e478`: 移除独立的 `librustdesk.so` 上传
- `bab6c848d`: 拆分 Windows artifacts 到独立上传步骤
- `da5695b17`: 移除未签名 artifact 上传
- `dcce6a777`: 移除 Windows 构建的 GitHub Release 发布（无权限）
- `ec7919461`: 移除发布到 GitHub Release 的步骤（无权限）

### Android 构建修复
- `53270ef74`: 移除多余 `popd` 导致 Android CI 目录栈空
- `0f2fd76f2`: conditional signing config + kotlin version
- `4dd0a7859`: 移除 kotlin-stdlib 版本锁定，由插件自动管理
- `f3ec47917`: APK 在 flutter build 阶段直接使用 release 签名

### 缓存与 Action 升级
- `67123d12e`: `actions/cache@v4` 替代 `lukka/run-vcpkg` 内置缓存，修复 Cache API 400
- `8ba816277`: `actions/github-script` v7 → v8 (Node.js 20 deprecation)
- `e1ae81776`: 回退 `install-llvm-action` v3 → v2（v3 tag 不存在）
- `0b55709f7`: 更新 deprecated Node.js 20 actions
- `c7528159f`: 修正 node24 comments → node20

### 加密与清理
- `5fee5f68a`: AES-256 构建产物加密 + 自动清理
- `741cc9e3e`: `Mattraks/delete-workflow-runs` 替代手动清理脚本

### VCPKG 缓存修复
- `15ead505e`: P0-P3 修复云编译 WiX ICE60/ICE84 警告和 CI 兼容性

### Secrets 注入
- `2fb440a50`: CI 注入 GitHub Secrets 到 `DEFAULT_SETTINGS`（`option_env!` 方式）

### Dependabot
- `7df56298e`: 禁用 dependabot 子模块更新

---

## 三、MSI 安装器改进（~8 提交）

### 中文语言默认
- `00c022aec`: MSI 文件默认语言设为 zh-CN (2052)
- `7d714b2ce`: MSI 安装界面默认中文，回退 Language 属性修复
- 新增 `Package.zh-cn.wxl` 和 `WixExt_zh-cn.wxl` 翻译文件

### 启动快捷方式
- `4e0ad1f1b`: MSI 启动快捷方式选项（含 `CustomActions.cpp` 运行时管理）
- `c4848af66`: 补回 `STARTUPSHORTCUTS` 的 `ComponentRef`（持久化修复）

### WiX 兼容性
- `c08d47ab9`: ICE60 `Language` 属性、`reinterpret_cast` address-of 警告、signed/unsigned 不匹配
- `a911cd50b`: 移除 WiX `File` 元素的 `Language` 属性（WiX v4 兼容）
- `15ead505e`: 自动生成 `File` 元素加 `Language="0"` 修复 ICE60；移除多余 `InstallExecuteSequence` 修复 ICE84

### 审计问题
- `df3d70e2f`: MSI KeyPath/desync、CI SIGN_BASE_URL、Sciter port、log 反转、死代码、APPDATA 安全

---

## 四、端口号迁移 2111x → 3111x（2 仓库协同）

- `2272f2421`: rustdesk 端同步所有端口引用 `2111x` → `3111x`
- `02dc51a`（hbb_common）: `feat: port 31115~31119`
- `e4d9715`（hbb_common）: `OPTION_ALLOW_HTTPS_21114` → `OPTION_ALLOW_HTTPS_31114`

---

## 五、Windows 开机自启（2 提交）

- `b50c0370b`: HKCU Run 注册表键实现
- `f589536`（hbb_common）: 新增 `OPTION_START_ON_BOOT` 配置项

*子模块指针同步（多次）*: `8139f2989`, `fa2cd575a`, `cc039bb01`, `d8accb942` 等

---

## 六、Logo 重新设计（2 提交）

- `b30fc6e34`: 替换 `flutter/assets/logo.png` / `logo_dark.png` / `logo_light.png`
- `1b0f7487b`: 补充 mipmap round/foreground 图标

---

## 七、安全与配置策略（4 提交）

- `b246719ac`: 禁用版本更新检测
- `e54612756`: 禁用向 `api.rustdesk.com` 的自动更新检查
- `f45cd38cd`: 防止空字符串覆盖有默认值的配置项
- `560a22b33`: 移除 `load_custom_client` 中冗余的 `inject_env_vars()` 双重调用

### hbb_common 配置修复
- `94b8db4`（hbb_common）: `get_or` 过滤空字符串，允许回退到 `DEFAULT_SETTINGS`

---

## 八、代码重构（3 提交）

- `03b89a9fb`: 环境变量注入提取为独立函数 `inject_env_vars()`
- `560a22b33`: 移除 `inject_env_vars()` 双重调用
- `40a11bff9`: `check_id` 改 ID 时补发 `pk` 字段

---

## 九、Gitignore（3 提交）

- `2e22c425b`: 取消忽略 `CHANGELOG.md`；新增忽略 `UPSTREAM_MERGE_PROMPT.md`
- `3a4d23c62`: 修复 `.gitignore` mydesk 规则不排除 Android Kotlin 源码
- `bbed7b2e3`: 锚定 `.gitignore` mydesk 规则到根目录，防止子目录误排除

---

## 十、hbb_common 子模块独有提交总览（8 个）

| 提交 | 描述 | 类别 |
|---|---|---|
| `d4d8f5d` | 端口 31115~31119, rename RustDesk → MyDesk | 重命名 + 端口 |
| `02dc51a` | 端口 31115~31119, rename RustDesk → MyDesk（同内容修正） | 重命名 + 端口 |
| `a203de4` | rename runtime strings rustdesk→mydesk (VER_TYPE, fs path, env var) | 重命名 |
| `94b8db4` | `get_or` 过滤空字符串 | 配置修复 |
| `e4d9715` | `OPTION_ALLOW_HTTPS_21114` → `OPTION_ALLOW_HTTPS_31114` | 端口 |
| `d950212` | Add controlled context for controller audit attribution | 审计特性 |
| `4d9c818` | rebrand HELPER_URL hashmap keys from rustdesk to mydesk | 重命名 |
| `f589536` | `OPTION_START_ON_BOOT` for Windows start-on-boot | 功能 |

---

## 冲突高发区（合并时重点检查）

### 红色警告 — 几乎必然冲突

| 文件 | 原因 |
|---|---|
| `.github/workflows/build.yml` | 完全重写（简化 + 中文 + 加密 + 新 steps） |
| `.github/workflows/flutter-build.yml` | 重命名 + 加密 + 分支构建限制 |
| `Cargo.toml` | lib 名 `librustdesk` → `libmydesk`, 依赖版本, 更新检测 |
| `src/platform/windows.rs` | IDD 命名 + MSI 启动项 + 审计修复 + 配置 |
| `src/server/connection.rs` | 审计特性修改（controller audit） |
| `src/rendezvous_mediator.rs` | 审计特性修改（controller audit） |
| `res/msi/**` | 中文默认语言 + 启动快捷方式 + WiX v4 兼容 |
| `build.py` | 打包脚本全面重命名 |

### 黄色预警 — 视上游改动范围可能冲突

| 文件 | 原因 |
|---|---|
| `flutter/lib/**` | 平台通道名 + 类名 + URI scheme 重命名 |
| `flutter/android/**` | package path + Kotlin source 路径 |
| `flutter/macos/**` / `flutter/ios/**` | `pbxproj` lib 引用重命名 |
| `libs/clipboard/**` | 运行时字符串 `rustdesk` → `mydesk` |
| `res/*.desktop` / `res/*.service` | 文件名变更 |
| `src/virtual_display_manager.rs` | `RUSTDESK_IDD_DEVICE_STRING` 重命名 |
| `gitignore` | 新增 mydesk 规则 + 锚定 |
| `libs/hbb_common` | 子模块指针变更（必须指向 `origin/Mod`） |

---

## 合并步骤建议

### 第一步：合并 rustdesk 主仓库

```bash
# 确保工作目录干净
git checkout Mod
git fetch upstream master

# 创建备份分支
git branch backup-merge-$(date +%Y%m%d)

# 合并上游
git merge upstream/master
```

### 第二步：处理冲突

按顺序解决：
1. `.github/workflows/*` — CI 配置重复程度最高
2. `res/msi/**` — MSI 文件结构变化大
3. `Cargo.toml` — 注意保持 lib 名、版本、feature flags
4. `build.py` — 自行比对 `rustdesk` vs `mydesk` 路径
5. Rust 源码 (`src/`) — 注意 IDD 命名 + 审计 + config
6. Flutter/Dart (`flutter/`) — 平台通道 + 类名
7. 翻译文件 (`src/lang/`) — 通常自动合并成功

### 第三步：同步 hbb_common 子模块

```bash
git -C /home/git/working/hbb_common fetch upstream main
git submodule update --remote libs/hbb_common
```

合并 hbb_common 子模块的冲突（如果有）。

### 第四步：最终验证

```bash
# 检查是否有残留的 "rustdesk" 引用（忽略大小写不敏感路径）
rg -n "rustdesk" --type rust --type dart --type-add 'py:*.py' --type-add 'xml:*.xml' -g '!.git/' -g '!target/' -g '!flutter/build/'

# 检查构建
cargo check 2>&1 | head -30
```

---

## 该文档本身

此文件在 `.gitignore` 中被排除，不会提交到版本控制。如需更新内容，直接编辑本文件即可。
