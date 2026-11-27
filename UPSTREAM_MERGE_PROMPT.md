# 上游合并策略

> fork 定制已抽离为可重放的 `branding/` 层(2026-11 重构, 经树等价验证)。
> 本文档描述基于该层的合并流程; 层内细节见 `branding/README.md`。

## 仓库信息

- **本地分支**：`Mod`（默认分支）
- **Fork 来源**：`rustdesk/rustdesk`（remote: `upstream`），远程 fork：`agogo233/rustdesk`（remote: `origin`）
- **子模块**：`libs/hbb_common` → `https://github.com/agogo233/hbb_common.git`（Mod 分支），内部同步见 AGENTS.md
- **品牌**：MyDesk（上游 RustDesk）；`app_name() != "RustDesk"` 使 `is_custom_client()` 自动为 true
- **端口**：31115~31119（上游 21115~21119，仅语言文案迁移；src 测试代码保留上游端口）

## 定制层一览

| 层 | 位置 | 内容 |
|---|---|---|
| 品牌化变换 | `branding/apply.sh` + `rules/` | 标识符替换(text.tsv)、端口(ports.txt)、例外行(exceptions.txt)、rename/delete(files.tsv)、overlays 覆盖(二进制/SVG/新增文件/.gitmodules)、子模块 pin |
| 定制 patch | `branding/patches/NN-*.patch` | 10-security-core / 20-windows-msi / 30-macos / 40-android / 50-packaging / 60-ci / 70-flutter-ui / 80-lang-full / 90-docs / 95-misc |

## 合并流程

```bash
# 0. 前置(主仓库): 工作树干净才继续, 脏则 stash
cd /home/git/working/rustdesk
git diff --quiet && git diff --cached --quiet || git stash
git fetch upstream
git branch backup-$(date +%Y%m%d)   # 备份

# 1. 干净上游基线 worktree
git worktree add /tmp/opencode/upstream-rebuild --detach upstream/master
cd /tmp/opencode/upstream-rebuild

# 2. 品牌化层
/home/git/working/rustdesk/branding/apply.sh
git commit -qm "branding layer"

# 3. 定制 patch(顺序应用; 任一失败必须中止人工解决, 不得跳过继续)
for p in /home/git/working/rustdesk/branding/patches/*.patch; do
    git apply --check "$p" || { echo "需人工解决: $p"; exit 1; }
    git apply "$p"
done
# patch 冲突解决后回写对应 patch 文件(见 branding/README.md 的闭环)

# 4. 收尾: 暂存 + 带上 branding/ + pin 子模块 + 验证
git add -A -- . ':(exclude)libs/hbb_common'
git checkout /home/git/working/rustdesk/Mod -- branding/
git add branding
sha=$(awk -F'\t' '$1=="libs/hbb_common"{print $4}' /home/git/working/rustdesk/branding/rules/submodule.txt)
git update-index --cacheinfo "160000,$sha,libs/hbb_common"
git commit -qm "Merge upstream/master into Mod"
UP_HEAD=$(git rev-parse HEAD)
/home/git/working/rustdesk/branding/verify.sh
# 附加人工检查: git log <旧merge-base>..upstream/master --oneline 逐条确认上游提交的取舍

# 5. 落库(树取重放提交, commit-tree 双父保留历史) + 推送
cd /home/git/working/rustdesk
TREE=$(git -C /tmp/opencode/upstream-rebuild rev-parse HEAD^{tree})
NEW=$(git commit-tree "$TREE" -p HEAD -p "$UP_HEAD" -m "Merge upstream/master into Mod")
git update-ref refs/heads/Mod "$NEW" && git reset --hard Mod
git push origin Mod
git worktree remove --force /tmp/opencode/upstream-rebuild
```

## 决策原则(仍适用)

- `.github/workflows/` 只保留 `build-New.yml`，上游 workflow 一律不并入
- `libs/hbb_common` 指针只指向本 fork 的 Mod 分支
- RegisterPk 的 `pk: pk.into()` 必须保留(纯 TCP 服务端依赖它取公钥, 见 10-security-core.patch)
- 禁用自动更新三处空桩在 10-security-core.patch 内
- DRM 打包走本地 `--drm` + `mydesk-unattended-wayland` 独立变体, 不接上游 allow-drm-capture 运行时开关
- 语言表: 上游新 key 跟随, 译文含 RustDesk 处换 MyDesk(80-lang-full.patch 域)

## 常见陷阱

1. `git apply` 失败的 patch 解决后**必须回写**(见 branding/README.md 的闭环)
2. 上游新增含 RustDesk 的文件不会被自动品牌化(scope 外), 需人工替换并更新 scope
3. 树等价 gate(重构期验证)已通过; 未来合并的最终校验以 `verify.sh` + CI 为准
4. hbb_common 上游修复(websocket 等)需在 fork 源仓库单独合并, 再更新 submodule.txt 的 sha
