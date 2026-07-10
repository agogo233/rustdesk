# 上游合并策略提示词

> 此文件为 git 追踪版本，整合了本地全部独有变更的引用清单、合并策略决策指引和可执行的 AI prompt。

---

将此文档作为完整 prompt 提供给 AI 编码助手（如 Claude、Cursor 等），即可自动执行一次完整的上游合并。

hbb_common 子模块在同级文件夹 `hbb_common` 中，但本文档**不包含**其内部 merge 细节——请参考 `AGENTS.md` 中的 hbb_common 工作流处理。

---

## 角色设定

你是一个 Git 合并专家，专门负责将 `rustdesk/rustdesk`（upstream）的最新代码合并到 `agogo233/rustdesk` 的 `Mod` 分支。

## 仓库信息

- **本地分支**：`Mod`（默认分支）
- **Fork 来源**：`rustdesk/rustdesk`（remote name: `upstream`）
- **子模块**：`libs/hbb_common` 指向 `https://github.com/agogo233/hbb_common.git`（Mod 分支）
- **默认端口范围**：`31115~31119`（上游为 `21115~21119`）
- **品牌名**：`MyDesk`（上游为 `RustDesk`）
- **应用标识**：`com.mydesk.mydesk`（上游为 `com.carriez.rustdesk`）
- **自定义客户端标识**：`app_name() != "RustDesk"` → 自动视作 custom client（`is_custom_client()` 返回 `true`）

### 本地独有变更总览

| 类别 | 变更内容 | 影响范围 | 合并上游建议 |
|------|----------|----------|-------------|
| **Branding** | RustDesk → MyDesk 全量重命名（4 阶段） | 代码、FFI、Flutter、构建脚本、资源文件、翻译 | **上游可能拒绝**，需作为独立 patch 维护 |
| **端口迁移** | 2111x → 3111x | 网络通信、配置常量、i18n | 需确认上游是否接受端口变更 |
| **禁用自动更新** | 删除 `do_check_software_update` 调用 | `src/common.rs`, `src/rendezvous_mediator.rs`, `src/updater.rs` | **上游大概率拒绝**，需单独维护 |
| **Submodule** | hbb_common 指向自定义 Mod branch | `OPTION_START_ON_BOOT`、空字符串修复 | 合并上游后需确认 submodule 指向 |

---

## 合并前策略决策

**在开始合并前，逐项确认以下决策。每一项都可能影响半数以上 diff 的去留。**

### 1. 决策清单

- [ ] **Branding 策略**：**已定 — 保持 MyDesk**
  - `is_custom_client()` 依赖：MyDesk ≠ `"RustDesk"`，自动触发 custom client 路径
  - P0 冲突全取 `--ours`
- [ ] **端口策略**：保持 3111x。需要确认上游是否已使用 2111x，以及是否有新增端口
- [ ] **禁用更新检查**：fork 专属 patch，必须在 P1 重新应用
- [ ] **Submodule 策略**：保持指向 `agogo233/hbb_common` Mod 分支，按 `AGENTS.md` 流程同步

### 2. 变更分类与上游接受度参考

| 变更 | 上游接受度 | 维护策略 |
|------|-----------|---------|
| MyDesk Branding | ❌ 上游拒绝 | 独立 patch（P0） |
| 端口 3111x | ❓ 不确定 | 需确认后再决 |
| 禁用更新检查 | ❌ 上游拒绝 | 独立 fork patch（P1） |
| Windows 开机自启 | ✅ 可贡献 | 建议合并前提交 PR |
| MSI WiX v4 修复 | ✅ 可贡献 | 建议合并前提交 PR |
| CI 加密 + 自动清理 | ✅ 可贡献 | 建议合并前提交 PR |
| 空字符串覆盖修复 | ✅ bugfix | 建议合并前提交 PR |
| Android CI 修复 | ✅ 可贡献 | 建议合并前提交 PR |

### 3. 可先行向上游提交的 PR 清单

合并之前先向上游提 PR，可以减少冲突面：

| 改动 | 说明 |
|------|------|
| Windows 开机自启（`HKCU Run`） | 纯功能增强，无冲突风险 |
| MSI 构建修复（WiX v4 兼容） | 修复 ICE60、移除 `Language` 属性 |
| CI 产物加密 + 自动清理 | 安全加固，通用价值 |
| 空字符串覆盖默认值修复 | bugfix，已在 hbb_common 修复 |
| Android CI 目录泄漏修复 | bugfix |
| 签名服务空值检查容错 | CI 健壮性改进 |
| APK 签名流程优化 | Android 构建改进 |
| Kotlin 版本管理改进 | Android 构建改进 |

---

## 合并前置检查

```bash
# 1. 确认工作区干净
git status --porcelain | grep -v '^\?' || true

# 2. 确认远端最新
git fetch upstream

# 3. 记录当前状态
BASE=$(git merge-base upstream/master HEAD)
echo "当前 merge-base: $BASE"
echo "上游 HEAD: $(git rev-parse upstream/master)"
echo "本地 HEAD: $(git rev-parse HEAD)"

# 4. 记录本地未合并提交数
echo "本地领先上游提交数: $(git log --oneline upstream/master..HEAD --no-merges | wc -l)"
```

---

## 步骤 1：执行合并

```bash
git merge upstream/master --no-ff -m "Merge upstream/master into Mod"
```

---

## 步骤 2：冲突分类处理

冲突文件按以下优先级依次解决。**每个类别解决完毕后立即 `git add` 并继续下一类。**

### P0 — 品牌重命名冲突（脚本批量处理）

**特征**：仅是 `RustDesk` ↔ `MyDesk` / `rustdesk` ↔ `mydesk` / `rust_desk` ↔ `my_desk` 等标识符替换，无逻辑变更。

> **⚠️ 关于 `is_custom_client()`**：品牌改为 MyDesk 后（`app_name() != "RustDesk"`），本 fork 自动满足 custom client 条件。合并时需确保 `is_custom_client` 的判断逻辑未被上游重构覆盖。

**处理方法**：对每个冲突文件，检查是否是 100% 的纯重命名冲突。如果是，执行：

```bash
git checkout --ours -- <冲突文件>
git add <冲突文件>
```

或者对批量文件自动处理：

```bash
# 方案 A：接受本地版本（保留品牌重命名）
git diff --name-only --diff-filter=U | while read f; do
  if git diff upstream/master -- "$f" | grep -qE '^[-+].*[Rr]ust[Dd]esk' && \
     ! git diff upstream/master -- "$f" | grep -qE '^[-+].*(feat|fix|refactor|new|add|remove|change)' 2>/dev/null; then
    git checkout --ours -- "$f"
    git add "$f"
    echo "P0 已解决: $f"
  fi
done
```

**涉及文件清单（高频冲突）**：

| 文件 | 重命名模式 |
|------|-----------|
| `src/client/io_loop.rs` | `RustDeskInterval`→`MyDeskInterval`, `rustdesk_interval`→`mydesk_interval`, `rustdesk_idd`→`mydesk_idd` |
| `src/server/connection.rs` | 同上 |
| `src/rendezvous_mediator.rs` | 同上 + 注释中的 `rustdesk --deploy`→`mydesk --deploy` |
| `src/client.rs` | `RustDeskInterval`, URL `rustdesk.com`→`mydesk.com` |
| `src/server.rs` | `try_kill_rustdesk_main_window_process`→`try_kill_mydesk_main_window_process` |
| `src/clipboard.rs` | `RUSTDESK_CLIPBOARD_OWNER_FORMAT`→`MYDESK_CLIPBOARD_OWNER_FORMAT`, `is_file_url_set_by_rustdesk`→`is_file_url_set_by_mydesk`, 路径 `/tmp/.rustdesk_`→`/tmp/.mydesk_` |
| `src/ipc.rs` | 注释中的 `rustdesk`→`mydesk` |
| `src/ipc/fs.rs` | 注释/测试中的 `rustdesk-ipc`→`mydesk-ipc` |
| `src/flutter.rs` | `rustdesk_core_main`→`mydesk_core_main`, `get_rustdesk_app_name`→`get_mydesk_app_name` |
| `src/flutter_ffi.rs` | 下载文件名 `rustdesk-`→`mydesk-` |
| `src/core_main.rs` | 模块路径 `rustdesk_idd`→`mydesk_idd`, 注释 |
| `src/updater.rs` | 下载 URL 路径 `rustdesk-`→`mydesk-` |
| `src/server/input_service.rs` | 注释中的 `RustDesk`→`MyDesk` 和路径 |
| `src/virtual_display_manager.rs` | `IDD_IMPL_RUSTDESK`→`IDD_IMPL_MYDESK`, `rustdesk_idd::`→`mydesk_idd::`, 字段名 |
| `src/plugin/*.rs` | `RustDesk`→`MyDesk` |
| `src/privacy_mode/*.rs` | `RustDesk`→`MyDesk` |
| `src/platform/*.rs` | `RustDesk`→`MyDesk`（windows.rs: 路径、进程名；macos/linux: 注释） |
| `src/lang/*.rs` | 翻译条目中的 `"RustDesk"`→`"MyDesk"` |
| `flutter/lib/*.dart` | `rustDeskWinManager`→`myDeskWinManager`, `RustDeskImpl`→`MyDeskImpl`, `RUSTDESK_APPNAME`→`MYDESK_APPNAME`, 注释 |
| `flutter/lib/common.dart` | `DISABLE_RUSTDESK_RESTORE_WINDOW_POSITION`→`DISABLE_MYDESK_RESTORE_WINDOW_POSITION` |
| `flutter/android/**/*.kt` | 包路径 `com.carriez.flutter_hbb`→`mydesk.mydesk` |
| `flutter/ios/**/*.swift/.plist` | 应用名和 bundle ID |
| `flutter/linux/**` | 应用名 |
| `flutter/macos/**` | 应用名和 bundle ID |
| `flutter/windows/**` | 应用名和资源 |
| `res/msi/**/*.wxs/.cpp` | `RustDesk`→`MyDesk`, 组件 GUID |
| `res/*.{desktop,service,spec}` | 服务名、包名 |
| `build.py` | `rustdesk`→`mydesk`（包名、路径、桌面文件、控制文件） |
| `Cargo.toml` | `name`, `authors`, `description`, `default-run`, lib/Windows 元数据/macOS bundle ID |

**红色警告 — 几乎必然冲突**（以下文件冲突程度最高）：

| 文件 | 原因 |
|------|------|
| `.github/workflows/build.yml` | 完全重写（简化 + 中文 + 加密 + 新 steps） |
| `.github/workflows/flutter-build.yml` | 重命名 + 加密 + 分支构建限制 |
| `Cargo.toml` | lib 名 `librustdesk` → `libmydesk`, 依赖版本, 更新检测 |
| `src/platform/windows.rs` | IDD 命名 + MSI 启动项 + 审计修复 + 配置 |
| `src/server/connection.rs` | 审计特性修改（controller audit） |
| `src/rendezvous_mediator.rs` | 审计特性修改（controller audit） |
| `res/msi/**` | 中文默认语言 + 启动快捷方式 + WiX v4 兼容 |
| `build.py` | 打包脚本全面重命名 |

**黄色预警 — 视上游改动范围可能冲突**：

| 文件 | 原因 |
|------|------|
| `flutter/lib/**` | 平台通道名 + 类名 + URI scheme 重命名 |
| `flutter/android/**` | package path + Kotlin source 路径 |
| `flutter/macos/**` / `flutter/ios/**` | `pbxproj` lib 引用重命名 |
| `libs/clipboard/**` | 运行时字符串 `rustdesk` → `mydesk` |
| `res/*.desktop` / `res/*.service` | 文件名变更 |
| `src/virtual_display_manager.rs` | `RUSTDESK_IDD_DEVICE_STRING` 重命名 |
| `libs/hbb_common` | 子模块指针变更（必须指向 `origin/Mod`） |

**自动化替换脚本（对已解决冲突的文件执行二次检查）**：

```bash
# 对 Rust 源文件应用品牌重命名
find src/ -name '*.rs' -exec sed -i \
  -e 's/RustDeskInterval/MyDeskInterval/g' \
  -e 's/rustdesk_interval/mydesk_interval/g' \
  -e 's/RustDeskIddDriver/MyDeskIddDriver/g' \
  -e 's/IDD_IMPL_RUSTDESK/IDD_IMPL_MYDESK/g' \
  -e 's/rustdesk_idd/mydesk_idd/g' \
  -e 's/get_rustdesk_app_name/get_mydesk_app_name/g' \
  -e 's/rustdesk_core_main/mydesk_core_main/g' \
  -e 's/rustdesk_com/mydesk_com/g' \
  -e 's/RUSTDESK_APPNAME/MYDESK_APPNAME/g' \
  -e 's/RUSTDESK_CLIPBOARD_OWNER_FORMAT/MYDESK_CLIPBOARD_OWNER_FORMAT/g' \
  -e 's/is_file_url_set_by_rustdesk/is_file_url_set_by_mydesk/g' \
  -e 's|/tmp/\.rustdesk_|/tmp/.mydesk_|g' \
  -e 's|rustdesk-ipc|mydesk-ipc|g' \
  -e 's|rustdesk\.com|mydesk.com|g' \
  {} +

# 对 Flutter/Dart 源文件
find flutter/lib/ -name '*.dart' -exec sed -i \
  -e 's/rustDeskWinManager/myDeskWinManager/g' \
  -e 's/RustDeskImpl/MyDeskImpl/g' \
  -e 's/RUSTDESK_APPNAME/MYDESK_APPNAME/g' \
  -e 's/DISABLE_RUSTDESK_RESTORE_WINDOW_POSITION/DISABLE_MYDESK_RESTORE_WINDOW_POSITION/g' \
  -e 's/RustDeskRemoteWindow/MyDeskRemoteWindow/g' \
  {} +

# 对 Flutter Android Kotlin
find flutter/android/ -name '*.kt' -exec sed -i \
  -e 's/com\.carriez\.flutter_hbb/mydesk.mydesk/g' \
  {} +

# 对 MSI 文件
find res/msi/ -name '*.wxs' -o -name '*.cpp' -o -name '*.wxl' | xargs sed -i \
  -e 's/RustDesk/MyDesk/g' \
  -e 's/rustdesk/mydesk/g' 2>/dev/null

# 对 build.py
sed -i \
  -e 's/rustdesk/mydesk/g' \
  -e 's/RustDesk/MyDesk/g' \
  build.py

# 对 Cargo.toml
sed -i \
  -e 's/rustdesk/mydesk/g' \
  -e 's/RustDesk/MyDesk/g' \
  -e 's/com\.carriez/com.mydesk/g' \
  Cargo.toml
```

> **注意**：`sed` 批量替换是「安全检查后」的加速手段。推荐流程：先 `git checkout --ours` 接受本地版本 → `git add` → 运行 sed 确保一致。不要对上游新增的、包含复杂逻辑的文件直接运行 sed。

---

### P1 — 安全策略变更（手动确认）

**本地已做的安全策略修改，合并后需要重新应用**：

| 修改点 | 文件 | 需要做的操作 |
|--------|------|-------------|
| 禁用自动更新检查 | `src/common.rs` → `check_software_update()` | 确认函数体为空桩（只保留 `Ok(())`） |
| 禁用启动时自动更新 | `src/rendezvous_mediator.rs` | 确认 `start_auto_update()` 调用被注释或移除 |
| 禁用更新线程 | `src/updater.rs` → `update_controlling_session_count()` | 确认函数体为空 |
| 端口范围 2111x→3111x | `libs/hbb_common` 子模块（由 fork 维护） | 确认子模块指针正确 |
| 空配置覆盖防护 | `src/common.rs` 配置读取逻辑 | 确认空字符串不会覆盖有默认值的配置项 |

**处理方法**：

```bash
# 对 src/common.rs：找到合并后的 check_software_update，确保它是空桩
# 对 src/rendezvous_mediator.rs：找到并注释 start_auto_update() 调用
# 对 src/updater.rs：找到并清空 update_controlling_session_count 函数体
```

---

### P2 — 功能新增冲突（逐个审查）

本地新增的功能需要与上游新代码融合：

| 功能 | 文件 | 冲突说明 |
|------|------|---------|
| Windows 开机自启 | `src/platform/windows.rs`, `src/flutter_ffi.rs`, `src/lang/*.rs` | 检查上游是否已有类似功能，若已实现则适配；若无则重新应用本地代码 |
| MSI 启动快捷方式 | `res/msi/Package/Fragments/ShortcutProperties.wxs` 等 | 检查上游 MSI 结构是否变化，按需移植 |
| 品牌 Logo 资源 | `res/*.png`, `flutter/assets/*`, `flutter/android/app/src/main/res/mipmap-*` 等 | 全量替换即可，上游不会触及这些文件 |
| env var 注入 | `src/common.rs` 中的 `inject_env_vars()` | 确认该函数仍然独立存在，未被上游重构覆盖 |

---

### P3 — CI/CD 工作流冲突

**本地有自己完整的一套 workflow**（`.github/workflows/build.yml`），与上游完全不同。

```bash
# 直接保留本地版本
git checkout --ours -- .github/workflows/
git add .github/workflows/
```

如果上游新增了 workflow 文件且本地需要，则手动挑选合并。

**具体 workflow 差异**：
- 本地移除了 9 个上游 workflow，重建了 1 个精简版 `build.yml`
- 本地构建缩减为仅 Windows x86_64 + Android arm64
- 本地没有 GitHub Release 发布权限（上传步骤已删除）
- 本地增加了 AES-256 加密和自动清理

---

### P4 — 子模块指针冲突

**注意**：本文档仅处理 rustdesk 主仓库侧的操作。hbb_common 的源码修改和内部 merge 请参考 `AGENTS.md` 中的 hbb_common 工作流。

```bash
# 子模块保持指向 agogo233/hbb_common 的 Mod 分支
git checkout --ours -- libs/hbb_common
git add libs/hbb_common

# 更新子模块到包含上游最新代码的版本
git submodule update --remote libs/hbb_common
```

**确认 `.gitmodules` 保持**：
```
url = https://github.com/agogo233/hbb_common.git
```

---

### P5 — 杂项修复

| 修复项 | 说明 |
|--------|------|
| MSI WiX v4 兼容 | `Language` 属性移除、ICE60 修复 |
| MSI 默认语言 zh-CN | `res/msi/Package/Language/Package.en-us.wxl` 中的语言代码 |
| Android .so 路径 | 确认 `flutter/android/app/build.gradle` 中 jniLibs 路径 |
| Android 条件签名 | `flutter/android/app/build.gradle` 中的 signingConfigs |
| CI Node.js 版本 | 确认 workflow 使用 node20（非已弃用的 node16/node12） |
| dependabot 禁用 | 确认 `.github/dependabot.yml` 不存在或配置正确 |

---

## 步骤 3：验证清单

```bash
# 1. 基础编译
cargo check 2>&1 | head -50

# 2. 检查关键品牌标识一致性
grep -rn 'RustDesk' src/Cargo.toml src/main.rs src/flutter.rs 2>/dev/null || echo "无残留 RustDesk（正确）"
grep -rn 'com\.carriez' Cargo.toml 2>/dev/null || echo "无残留 com.carriez（正确）"

# 3. 检查 is_custom_client 逻辑未被上游覆盖
grep -n 'is_custom_client' src/ 2>/dev/null
# 预期输出类似：app_name() != "RustDesk" 的判断，MyDesk 应返回 true

# 4. 检查端口一致性
grep -rn '2111[5-9]' src/ 2>/dev/null || echo "无残留 2111x 端口（正确）"
grep -rn '3111[5-9]' src/ 2>/dev/null | head -5

# 5. 检查安全策略
grep -n 'do_check_software_update' src/common.rs  # 应为空桩
grep -rn 'start_auto_update' src/ 2>/dev/null      # 应无调用（注释除外）

# 6. 子模块指针确认
git submodule status

# 7. 完整编译（耗时较长，但推荐）
# cargo build
```

---

## 步骤 4：回滚方案

如果在合并过程中发现问题：

```bash
# 终止合并并回退到合并前状态
git merge --abort

# 如果 merge --abort 不可用（部分已提交），硬重置到合并前
git log --oneline --all --graph | grep -v 'Merge'
git reset --hard <合并前最后一个提交的 hash>

# 恢复子模块指针
git submodule update --init --recursive
```

---

## 常见陷阱

1. **不要把 `RustDesk` 字符串全部替换**：上游的一些 RustDesk-specific 标识符不应替换（如 `rustdesk-server` 的协议字段），只替换应用自身的品牌名。
2. **`.github/workflows/` 整目录冲突**：直接取本地版本，因为本地 workflow 是完全独立的一套。
3. **`src/lang/*.rs` 冲突**：这些文件的冲突通常是上游添加了新翻译键与本地重命名冲突。接受本地版本，然后更新新键的 "MyDesk" 条目。
4. **`build.py` 冲突**：上游此文件改动频繁。接受本地版本，然后手动挑选上游有价值的构建修复。
5. **`Cargo.toml` 冲突**：品牌重命名 + 依赖版本。先接受本地版本，然后手动将上游新增的依赖合并进来。
6. **`is_custom_client` 依赖关系**：品牌改为 MyDesk 后自动触发 custom client 路径。如果上游重构了 `app_name()` 或 `is_custom_client()` 的实现，需手动确认 MyDesk 仍被视作 custom client。常见陷阱：上游可能将 `is_custom_client` 改为基于白名单判断，此时 MyDesk 不再自动满足条件。

---

## 合并后提交模板

```bash
git commit -m "Merge upstream/master into Mod

# 合并摘要：
# - P0: 品牌重命名冲突已批量解决（保持 MyDesk）
# - P0 is_custom_client: 已确认 MyDesk 被视作 custom client
# - P1: 安全策略已重新应用（禁用更新检查、空配置防护）
# - P2: 功能新增已融合（开机自启、MSI 快捷方式等）
# - P3: CI/CD 工作流已保留本地版本
# - P4: 子模块已同步（hbb_common 指向 origin/Mod）
# - P5: 杂项修复已应用
"
```

---

## 完整自动化脚本（单文件版本）

以下是一个可直接执行的 bash 脚本，封装了上述所有步骤：

```bash
#!/usr/bin/env bash
set -euo pipefail

# === 配置 ===
UPSTREAM_REMOTE="upstream"
UPSTREAM_BRANCH="master"
LOCAL_BRANCH="Mod"

echo "=== 步骤 1: 前置检查 ==="
git fetch "$UPSTREAM_REMOTE"
if [ -d .git/MERGE_MSG ]; then
    echo "警告: 存在未完成的合并，尝试 git merge --abort"
    git merge --abort 2>/dev/null || true
fi
if ! git diff --stat --cached | grep -q . && ! git diff --stat | grep -q .; then
    echo "工作区干净 ✓"
else
    echo "工作区不干净，请先 stash 或提交"
    exit 1
fi

BASE=$(git merge-base "$UPSTREAM_REMOTE/$UPSTREAM_BRANCH" HEAD)
echo "merge-base: $BASE"
echo "上游 HEAD: $(git rev-parse "$UPSTREAM_REMOTE/$UPSTREAM_BRANCH")"

echo "=== 步骤 2: 执行合并 ==="
git merge "$UPSTREAM_REMOTE/$UPSTREAM_BRANCH" --no-ff -m "Merge $UPSTREAM_REMOTE/$UPSTREAM_BRANCH into $LOCAL_BRANCH" || true

echo "=== 步骤 3: 解决冲突 ==="

# P0: 品牌重命名 — 纯重命名文件取本地版本
echo "--- P0: 品牌重命名 ---"
git diff --name-only --diff-filter=U | while read f; do
    case "$f" in
        src/lang/*.rs|src/client/io_loop.rs|src/server/connection.rs|src/clipboard.rs|src/ipc.rs|src/ipc/fs.rs|src/flutter.rs|src/core_main.rs|src/server/input_service.rs|src/virtual_display_manager.rs)
            git checkout --ours -- "$f"
            git add "$f"
            echo "  P0 已解决: $f"
            ;;
        flutter/lib/*.dart)
            git checkout --ours -- "$f"
            git add "$f"
            echo "  P0 已解决: $f"
            ;;
        Cargo.toml|build.py)
            git checkout --ours -- "$f"
            git add "$f"
            echo "  P0 已解决: $f"
            ;;
    esac
done

# P3: CI/CD 工作流
echo "--- P3: CI/CD ---"
git diff --name-only --diff-filter=U | grep '^\.github/' | while read f; do
    git checkout --ours -- "$f"
    git add "$f"
    echo "  P3 已解决: $f"
done

# P4: 子模块
echo "--- P4: 子模块 ---"
if git diff --name-only --diff-filter=U | grep -q 'libs/hbb_common'; then
    git checkout --ours -- libs/hbb_common
    git add libs/hbb_common
    echo "  子模块冲突已解决（使用本地指针）"
    echo "  注意: 请参考 AGENTS.md 处理 hbb_common 内部 merge"
fi

# 输出未解决的冲突
REMAINING=$(git diff --name-only --diff-filter=U)
if [ -n "$REMAINING" ]; then
    echo "=== 需要手动解决的冲突 ==="
    echo "$REMAINING"
    echo "请手动解决后执行: git add <文件> && git commit"
    exit 1
fi

echo "=== 步骤 4: 无残留冲突，提交合并 ==="
# 安全策略检查确认
echo "  请确认安全策略变更已重新应用（见文档 P1 部分）"

git commit
echo "=== 合并完成 ==="
```

---

## 快速参考表

| 优先级 | 类别 | 处理方式 | 涉及文件数 |
|--------|------|---------|-----------|
| P0 | 品牌重命名 | `git checkout --ours` + 批量 sed | ~269 个 |
| P1 | 安全策略 | 手动确认 3 个关键函数 | 3 个 |
| P2 | 功能新增 | 逐个审查融合 | ~8 个 |
| P3 | CI/CD | 直接取本地版本 | ~10 个 |
| P4 | 子模块 | 取本地指针（hbb_common 内部见 AGENTS.md） | 1 个 |
| P5 | 杂项 | 按清单检查 | 若干 |

---

## 附录 A：历史合并记录

### 2025-06-25 — 合并上游 2 个提交（FUSE 路径修复 + ptbr 翻译）

| 提交 | 内容 | 合并方式 |
|------|------|----------|
| `b8117c5c` | fix(fuse): fuse path broken, since ipc path changed | 自动合并，保留 `mydesk-cliprdr-fs` 品牌 |
| `a69614d4` | Update translation for 'Control Actions' in ptbr.rs | 自动合并，保留 MyDesk 品牌 |

**验证结果：** 零冲突、品牌保留、功能修复采纳、端口/更新/`is_mydesk()` 均正常。

### 2025-06-25 — 合并上游 2 个提交（clipboard 指纹去重 + tray 图标修复）

| 提交 | 内容 | 合并方式 |
|------|------|----------|
| `ff226f6d8` | fix(clipboard): unix, refresh cached file size/mtime on re-copy | 自动合并，品牌无影响 |
| `0cbdb6ffb` | Fix tray icon click (regression due to breaking change in tray-icon) | 自动合并，保留 `mydesk_interval` 品牌 |

**验证结果：** 零冲突、`FileSig`/`fingerprint()` 已采纳、tray 图标修复已采纳、品牌/端口/更新均正常。