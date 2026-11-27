#!/usr/bin/env bash
# MyDesk 品牌化层重放: 在干净的上游基线 worktree 根目录执行。
# 用法: cd <upstream-baseline-worktree> && /path/to/branding/apply.sh
set -euo pipefail
BRANDING_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$BRANDING_DIR/engine.py" "$BRANDING_DIR"
echo "branding apply 完成"
