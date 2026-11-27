#!/usr/bin/env bash
# MyDesk 品牌化层静态验证: 在重放完成的树上运行(仓库根目录)。
# 检查: 逻辑禁区 / scope 内品牌残留基线 / 子模块指针 / CI 清单
set -uo pipefail
BRANDING_DIR="$(cd "$(dirname "$0")" && pwd)"
FAIL=0

note() { echo "[verify] $*"; }
fail() { echo "[verify][FAIL] $*"; FAIL=1; }

# ---------- 1. 逻辑禁区(必须原样保留 RustDesk) ----------
note "1. 逻辑禁区检查"
grep -q 'get_app_name() != "RustDesk"' src/common.rs || fail "src/common.rs custom client 判定丢失"
grep -q 's.replace("RustDesk", &crate::get_app_name())' src/platform/macos.rs || fail "macos.rs 动态替换丢失"
grep -q '"RustDesk"' src/platform/mod.rs || fail "platform/mod.rs 判定丢失"
grep -q 'mainGetAppNameSync(hint: hint) != "RustDesk"' flutter/lib/web/bridge.dart || fail "bridge.dart web custom client 判定丢失"
[ "$(grep -c 'RustDesk' src/lang.rs)" = "9" ] || fail "src/lang.rs RustDesk 实例数 != 9"
grep -q 'pk: pk.into()' src/ui_interface.rs || fail "RegisterPk pk 保留丢失(P1.5)"

# ---------- 2. scope 内品牌行必须都在基线集合内 ----------
note "2. 品牌残留基线检查(scope 内, 集合外=疑似漏网)"
python3 - "$BRANDING_DIR" <<'PYEOF' || FAIL=1
import re, sys
branding = sys.argv[1]
base = {}
for line in open(f'{branding}/rules/rustdesk-baseline.txt'):
    if line.startswith('#'):
        continue
    p, c = line.rstrip('\n').split('\t', 1)
    base.setdefault(p, set()).add(c)
re_brand = re.compile(r'(?i)rust_?desk')
fail = 0
for raw in open(f'{branding}/rules/scope.txt'):
    f = raw.strip()
    if not f or f.startswith('#'):
        continue
    try:
        content = open(f, encoding='utf-8', errors='replace').read()
    except OSError:
        continue
    if not re_brand.search(content):
        continue
    for l in content.split('\n'):
        if re_brand.search(l) and l not in base.get(f, ()):
            print(f'[verify][FAIL] {f} 基线外品牌行: {l[:120]}')
            fail = 1
sys.exit(fail)
PYEOF

# ---------- 3. 子模块指针 ----------
note "3. 子模块指针检查"
want_sha=$(awk -F'\t' '$1=="libs/hbb_common"{print $4}' "$BRANDING_DIR/rules/submodule.txt")
got_sha=$(git ls-tree HEAD libs/hbb_common | awk '{print $3}')
[ "$want_sha" = "$got_sha" ] || fail "gitlink $got_sha != 规则 $want_sha"
grep -q 'agogo233/hbb_common' .gitmodules || fail ".gitmodules URL 非本 fork"

# ---------- 4. CI 清单 ----------
note "4. CI 清单检查"
[ -f .github/workflows/build-New.yml ] || fail "build-New.yml 缺失"
for f in bridge ci clear-cache fdroid flutter-build flutter-ci flutter-nightly flutter-tag playground third-party-RustDeskTempTopMostWindow update-webpki-roots; do
    [ -f ".github/workflows/$f.yml" ] && fail "上游 workflow 未删除: $f.yml"
done

if [ "$FAIL" = "0" ]; then note "全部通过"; else note "存在失败项"; exit 1; fi
