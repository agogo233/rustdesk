# MyDesk 品牌化层

把 fork 相对上游的全部定制拆成可重放的确定性变换, 让上游合并从"逐文件解决 106 个冲突"
变成"从干净上游基线重建"。经树等价验证: BASE(7949eca16) + 本层重放 = 原 Mod 树(8db873aff)。

## 结构

| 路径 | 作用 |
|---|---|
| `engine.py` | 变换引擎(rename/delete/文本替换/overlays/gitlink pin), bytes 级保 CRLF 与文件模式 |
| `apply.sh` | 引擎入口, 在干净的上游基线 worktree 根执行(单次执行语义, 带脏树守卫) |
| `verify.sh` | 静态验证(逻辑禁区/品牌残留基线/子模块指针/CI 清单) |
| `rules/scope.txt` | 替换作用域: 仅这些文件应用文本替换(上游未动的文件不碰) |
| `rules/text.tsv` | 标识符替换对(长串优先, 从 BASE..Mod 实际 diff 挖掘) |
| `rules/ports.txt` | 端口迁移对(仅 src/lang/*.rs 的 value) |
| `rules/exceptions.txt` | 例外行: 未被品牌化的 BASE 行(逻辑禁区/协议字段/URL) |
| `rules/files.tsv` | rename(R) / delete(D) 清单 |
| `rules/submodule.txt` | hbb_common 指针(fork URL/branch/gitlink) |
| `overlays/` | 整文件覆盖: 48 个二进制修改 + 6 个 SVG 重绘 + 新增文件 + .gitmodules |
| `patches/` | 非品牌化定制(按功能域编号), `git apply` 顺序应用 |

## 上游合并流程

```bash
# 0. 前置(主仓库): 干净才继续, 脏则 stash
git -C /home/git/working/rustdesk diff --quiet && git -C /home/git/working/rustdesk diff --cached --quiet || git -C /home/git/working/rustdesk stash
git fetch upstream

# 1. 干净上游基线(临时 worktree)
git worktree add /tmp/opencode/upstream-rebuild --detach upstream/master
cd /tmp/opencode/upstream-rebuild

# 2. 应用品牌化层
/home/git/working/rustdesk/branding/apply.sh
git commit -qm "branding layer"

# 3. 顺序应用定制 patch — 任一失败必须中止人工解决, 不得跳过继续
for p in /home/git/working/rustdesk/branding/patches/*.patch; do
    git apply --check "$p" || { echo "需人工解决: $p"; exit 1; }
    git apply "$p"
done

# 4. 收尾: 暂存 + 带上 branding/ 自身 + pin 子模块 + 验证
git add -A -- . ':(exclude)libs/hbb_common'
git checkout /home/git/working/rustdesk/Mod -- branding/
git add branding
sha=$(awk -F'\t' '$1=="libs/hbb_common"{print $4}' /home/git/working/rustdesk/branding/rules/submodule.txt)
git update-index --cacheinfo "160000,$sha,libs/hbb_common"
git commit -qm "Merge upstream/master into Mod"
UP_HEAD=$(git rev-parse HEAD)
/home/git/working/rustdesk/branding/verify.sh

# 5. 落库: 树取重放提交, commit-tree 双父保留历史(Mod HEAD + 重放 HEAD)
cd /home/git/working/rustdesk
TREE=$(git -C /tmp/opencode/upstream-rebuild rev-parse HEAD^{tree})
NEW=$(git commit-tree "$TREE" -p HEAD -p "$UP_HEAD" -m "Merge upstream/master into Mod")
git update-ref refs/heads/Mod "$NEW" && git reset --hard Mod
git push origin Mod
git worktree remove --force /tmp/opencode/upstream-rebuild
```

## patch 冲突闭环(重要)

`git apply` 失败的 patch: 手工解决该 patch 涉及文件的冲突后, **必须回写对应 patch 文件**
(在解决完成的树上重新 `git diff <branding基线>..HEAD -- <该域文件> > patches/NN-xxx.patch`),
否则下次重放仍用旧版。语言 patch(80) 在上游中部修改/删除 key 时会局部冲突, 属预期。

## 已知限制

- overlays 中被修改的二进制会覆盖上游对同名文件的更新(品牌图标, 预期行为)
- 上游新增含 `RustDesk` 的文件不会被自动品牌化(不在 scope), verify.sh 不检查 scope 外文件;
  如需品牌化, 人工替换并把文件加入 `rules/scope.txt`
- 引擎的替换规则源自 BASE..Mod 的一次性挖掘, 上游新形态的品牌词可能需要新增 text.tsv 条目
- `branding/rules/submodule.txt` 的 gitlink 是快照值, fork 更新后需同步修改
- lang 文件的结构感知替换假定每行恰一个 `("key", "value")` 条目且以 `"),` 收尾; 上游若引入
  同行多 entry 或行尾注释, 该行走整行替换兜底(端口迁移会跳过), 需人工复核
- text.tsv 的替换对与 patches 内容耦合: 单独增删替换对而不重新生成全部 patches, 会导致
  `git apply` 大面积 context 失配。调整 text.tsv 后必须全链路重放并重新生成 patches
- hbb_common 子模块内部同步见仓库根 AGENTS.md 的工作流章节
