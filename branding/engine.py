#!/usr/bin/env python3
"""MyDesk 品牌化变换引擎: 在干净的上游基线 worktree 上执行确定性变换。

步骤: rename -> delete -> 文本替换(例外行保护+lang value 结构感知) -> overlays -> gitlink pin
特性: bytes 级替换保 CRLF, 保留文件模式, 幂等(重复执行结果一致)。
"""
import os
import re
import sys
import shutil
import subprocess

BRANDING = os.path.abspath(sys.argv[1])
WT = os.getcwd()
GIT = ['git']


def load_rules():
    tokens = []
    with open(f'{BRANDING}/rules/text.tsv') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            a, b = line.rstrip('\n').split('\t')
            tokens.append((a, b))
    tokens.sort(key=lambda x: -len(x[0]))
    ports = []
    with open(f'{BRANDING}/rules/ports.txt') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            a, b = line.rstrip('\n').split('\t')
            ports.append((a, b))
    exc = {}
    with open(f'{BRANDING}/rules/exceptions.txt') as f:
        for line in f:
            if line.startswith('#'):
                continue
            path, content = line.rstrip('\n').split('\t', 1)
            exc.setdefault(path, set()).add(content)
    return tokens, ports, exc


TOKENS, PORTS, EXCEPTIONS = load_rules()
TOKENS_B = [(a.encode(), b.encode()) for a, b in TOKENS]
LANG_RE = re.compile(r'^(\s*\(".*?",\s*")(.*)("\),?)$')


def apply_tokens_b(data):
    for a, b in TOKENS_B:
        data = data.replace(a, b)
    return data


def apply_tokens_s(s):
    for a, b in TOKENS:
        s = s.replace(a, b)
    return s


def apply_ports_s(s):
    for a, b in PORTS:
        s = s.replace(a, b)
    return s


def process_lines(data, path):
    is_lang = path.startswith('src/lang/') and path.endswith('.rs')
    exc = EXCEPTIONS.get(path)
    lines = data.split(b'\n')
    out = []
    for line in lines:
        cr = b'\r' if line.endswith(b'\r') else b''
        core = line[:-1] if cr else line
        try:
            s = core.decode('utf-8')
        except UnicodeDecodeError:
            out.append(line)
            continue
        if exc is not None and s in exc:
            out.append(line)
            continue
        if is_lang:
            m = LANG_RE.match(s)
            if m:
                value = apply_ports_s(m.group(2))
                value = apply_tokens_s(value)
                rebuilt = m.group(1) + value + m.group(3)
                out.append(rebuilt.encode('utf-8') + cr)
                continue
        out.append(apply_tokens_b(core) + cr)
    return b'\n'.join(out)


def scope_files():
    paths = []
    with open(f'{BRANDING}/rules/scope.txt') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            paths.append(line.strip())
    return paths


def is_binary_head(path):
    full = os.path.join(WT, path)
    try:
        with open(full, 'rb') as f:
            return b'\0' in f.read(4096)
    except OSError:
        return True


def main():
    # 基线守卫: 只在未品牌化的上游基线上运行, 防止误在已品牌化树上执行造成 token 误替换
    with open(os.path.join(WT, 'Cargo.toml'), encoding='utf-8') as f:
        cargo = f.read()
    m = re.search(r'^name\s*=\s*"([^"]+)"', cargo, re.M)
    if not m or 'mydesk' in m.group(1).lower():
        sys.exit(f'拒绝执行: Cargo.toml name={m.group(1) if m else "?"}, 目标必须是未品牌化的上游基线')
    # 干净守卫: 脏树上运行会把无关改动卷入 branding 提交
    for flag in (['diff', '--quiet'], ['diff', '--cached', '--quiet']):
        if subprocess.run(GIT + flag, cwd=WT).returncode != 0:
            sys.exit('worktree 不干净, 拒绝执行 (先 commit 或 stash)')
    # 1. rename + delete
    with open(f'{BRANDING}/rules/files.tsv') as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.rstrip('\n').split('\t')
            if parts[0] == 'R':
                src_full = os.path.join(WT, parts[1])
                dst_full = os.path.join(WT, parts[2])
                if not os.path.lexists(src_full):
                    if os.path.lexists(dst_full):
                        continue
                    raise FileNotFoundError(f'rename 源不存在: {parts[1]}')
                os.makedirs(os.path.dirname(dst_full), exist_ok=True)
                subprocess.run(GIT + ['mv', '-f', parts[1], parts[2]], cwd=WT, check=True)
            elif parts[0] == 'D':
                full = os.path.join(WT, parts[1])
                if os.path.lexists(full):
                    os.remove(full)
                subprocess.run(GIT + ['rm', '-q', '--cached', '--ignore-unmatch', parts[1]], cwd=WT, check=True)

    # 2. 文本替换
    overlays = set()
    ov_root = os.path.join(BRANDING, 'overlays')
    for root, _dirs, files in os.walk(ov_root):
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), ov_root)
            overlays.add(rel)
    for path in scope_files():
        if path in overlays or path == '.gitmodules':
            continue
        if path.startswith('libs/hbb_common'):
            continue
        full = os.path.join(WT, path)
        if not os.path.isfile(full) or is_binary_head(full):
            continue
        with open(full, 'rb') as f:
            data = f.read()
        new = process_lines(data, path)
        if new != data:
            with open(full, 'wb') as f:
                f.write(new)

    # 3. overlays 覆盖(含 .gitmodules)
    for rel in sorted(overlays):
        src = os.path.join(ov_root, rel)
        dst = os.path.join(WT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    # 4. 暂存(排除子模块路径) + overlays 强制加入(可能被上游 .gitignore 规则忽略) + gitlink pin
    subprocess.run(GIT + ['add', '-A', '--', '.', ':(exclude)libs/hbb_common'], cwd=WT, check=True)
    for rel in sorted(overlays):
        subprocess.run(GIT + ['add', '-f', '--', rel], cwd=WT, check=True)
    with open(f'{BRANDING}/rules/submodule.txt') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            sub_path, _url, _branch, sha = line.rstrip('\n').split('\t')
            subprocess.run(GIT + ['update-index', '--cacheinfo', f'160000,{sha},{sub_path}'], cwd=WT, check=True)


if __name__ == '__main__':
    main()
