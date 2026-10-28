#!/usr/bin/env python3
"""Conservative lexical RTL inventory. Not a SystemVerilog parser or elaborator.

Only used to discover files/module candidates and source-line anchors; Codex must
inspect original RTL and confirm compiled hierarchy/parameters with a real tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
from pathlib import Path

RTL_EXTS = {'.v', '.sv'}
HEADER_EXTS = {'.vh', '.svh'}
EXCLUDED_DIRS = {'.git', '.agents', '.venv', 'venv', '__pycache__', 'node_modules',
                 'build', 'obj_dir', 'dist', 'out', '.cache'}
ID = r'[A-Za-z_$][A-Za-z0-9_$]*'
MOD_DECL = re.compile(r'\bmodule\s+(?:(?:automatic|static)\s+)?(' + ID + r')\b')
END_DECL = re.compile(r'\bendmodule\b')
DIRECTIONS = {'input', 'output', 'inout', 'ref'}


def strip_comments_and_strings(src: str) -> str:
    """Maintain offsets/newlines when hiding comments and strings."""
    out = list(src)
    i = 0
    while i < len(src):
        if src.startswith('//', i):
            j = src.find('\n', i)
            if j == -1:
                j = len(src)
            for k in range(i, j):
                out[k] = ' '
            i = j
        elif src.startswith('/*', i):
            j = src.find('*/', i + 2)
            j = len(src) if j == -1 else j + 2
            for k in range(i, j):
                if src[k] != '\n':
                    out[k] = ' '
            i = j
        elif src[i] == '"':
            j = i + 1
            while j < len(src):
                if src[j] == '\\':
                    j += 2
                elif src[j] == '"':
                    j += 1
                    break
                else:
                    j += 1
            for k in range(i, min(j, len(src))):
                if src[k] != '\n':
                    out[k] = ' '
            i = j
        else:
            i += 1
    return ''.join(out)


def line_at(src: str, offset: int) -> int:
    return src.count('\n', 0, offset) + 1


def matching_paren(src: str, open_idx: int) -> int | None:
    if src[open_idx:open_idx + 1] != '(':
        return None
    depth = 0
    for i in range(open_idx, len(src)):
        if src[i] == '(':
            depth += 1
        elif src[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return None


def split_top_commas(src: str) -> list[str]:
    splits = []
    depth_p = depth_b = depth_c = 0
    start = 0
    for i, c in enumerate(src):
        if c == '(':
            depth_p += 1
        elif c == ')':
            depth_p -= 1
        elif c == '[':
            depth_b += 1
        elif c == ']':
            depth_b -= 1
        elif c == '{':
            depth_c += 1
        elif c == '}':
            depth_c -= 1
        elif c == ',' and depth_p == depth_b == depth_c == 0:
            splits.append(src[start:i].strip())
            start = i + 1
    splits.append(src[start:].strip())
    return [s for s in splits if s]


def parse_header(mod_body: str, modname: str, source: str, base_line: int):
    """Return candidate parameter and ANSI/non-ANSI port information."""
    after = MOD_DECL.search(mod_body)
    if not after:
        return [], [], ['module header could not be located']
    idx = after.end()
    while idx < len(mod_body) and mod_body[idx].isspace():
        idx += 1
    parameters = []
    warnings = []
    if idx < len(mod_body) and mod_body[idx] == '#':
        idx += 1
        while idx < len(mod_body) and mod_body[idx].isspace():
            idx += 1
        if idx < len(mod_body) and mod_body[idx] == '(':
            end = matching_paren(mod_body, idx)
            if end is not None:
                for item in split_top_commas(mod_body[idx + 1:end]):
                    # Parameter names are heuristic: no constant evaluation here.
                    item = re.sub(r'^\s*(?:parameter|localparam)\b', '', item).strip()
                    left, _, val = item.partition('=')
                    tokens = re.findall(ID, left)
                    if tokens:
                        parameters.append({'name': tokens[-1], 'default_expr': val.strip() or None})
                idx = end + 1
            else:
                warnings.append('unbalanced module parameter list')
    while idx < len(mod_body) and mod_body[idx].isspace():
        idx += 1
    if idx >= len(mod_body) or mod_body[idx] != '(':
        warnings.append('non-standard or missing module port list')
        return parameters, [], warnings
    end = matching_paren(mod_body, idx)
    if end is None:
        warnings.append('unbalanced module port list')
        return parameters, [], warnings
    entries = split_top_commas(mod_body[idx + 1:end])
    port_candidates = []
    current_dir = current_width = None
    for entry in entries:
        entry = re.sub(r'\(\*.*?\*\)', ' ', entry, flags=re.S).strip()
        dmatch = re.match(r'^(input|output|inout|ref)\b', entry)
        if dmatch:
            current_dir = dmatch.group(1)
            entry = entry[dmatch.end():].strip()
            match_width = re.search(r'\[[^\[\]]+\]', entry)
            current_width = match_width.group(0) if match_width else '1'
        no_default = entry.split('=', 1)[0].strip()
        # Remove unpacked dimensions after a port name; can be ambiguous for exotic syntax.
        no_default = re.sub(r'(?:\s*\[[^\[\]]+\])+$', '', no_default).strip()
        token = re.search(r'(' + ID + r')\s*$', no_default)
        if not token:
            warnings.append('could not identify port from ' + entry[:48])
            continue
        port_candidates.append({'name': token.group(1), 'direction': current_dir,
                                'width_expr': current_width if current_dir else None})
    # Classic Verilog non-ANSI directions appear in the module body instead.
    for direction in DIRECTIONS:
        for m in re.finditer(r'\b' + direction + r'\b([^;]*);', mod_body[end + 1:]):
            declaration = m.group(1)
            width = re.search(r'\[[^\[\]]+\]', declaration)
            names_part = declaration
            for dtype in ('wire', 'reg', 'logic', 'signed', 'unsigned', 'integer', 'tri'):
                names_part = re.sub(r'\b' + dtype + r'\b', ' ', names_part)
            if width:
                names_part = names_part.replace(width.group(0), ' ')
            for s in split_top_commas(names_part):
                v = re.search(r'(' + ID + r')\s*$', s.strip())
                if v:
                    for port in port_candidates:
                        if port['name'] == v.group(1):
                            port.update(direction=direction, width_expr=width.group(0) if width else '1')
    if any(p['direction'] is None for p in port_candidates):
        warnings.append('one or more port directions unresolved (non-ANSI/interface ports?)')
    return parameters, port_candidates, warnings


def instance_candidates(body: str, module_names: set[str]) -> list[dict]:
    """Find candidate instantiations, *never* treat as proven elaborated hierarchy."""
    found = []
    for name in sorted(module_names, key=len, reverse=True):
        for m in re.finditer(r'\b' + re.escape(name) + r'\b', body):
            i = m.end()
            while i < len(body) and body[i].isspace():
                i += 1
            if body[i:i + 1] == '#':
                i += 1
                while i < len(body) and body[i].isspace():
                    i += 1
                if body[i:i + 1] != '(':
                    continue
                end = matching_paren(body, i)
                if end is None:
                    continue
                i = end + 1
            match = re.match(r'\s*(' + ID + r')\s*\(', body[i:])
            if match:
                found.append({'module': name, 'instance': match.group(1),
                              'confidence': 'candidate-not-elaborated'})
    return sorted({(v['module'], v['instance']): v for v in found}.values(),
                  key=lambda v: (v['module'], v['instance']))


def parse_filelist(root: Path, fl: Path):
    sources: set[Path] = set()
    include_dirs: set[str] = set()
    defines: set[str] = set()
    warnings: list[str] = []
    seen = set()

    def parse_one(path: Path):
        path = path.resolve()
        if path in seen:
            return
        seen.add(path)
        if not path.is_file():
            warnings.append(f'missing filelist: {path}')
            return
        tokens = shlex.split(path.read_text(errors='replace'), comments=True)
        idx = 0
        while idx < len(tokens):
            item = tokens[idx]
            idx += 1
            if item in ('-f', '-F'):
                if idx < len(tokens):
                    parse_one(path.parent / tokens[idx]); idx += 1
                continue
            if item.startswith('-f') and item not in ('-f', '-F'):
                parse_one(path.parent / item[2:]); continue
            if item.startswith('+incdir+'):
                include_dirs.update(item[len('+incdir+'):].split('+'))
                continue
            if item.startswith('+define+'):
                defines.update(item[len('+define+'):].split('+'))
                continue
            if item in ('-I', '-D', '-y', '-v'):
                if idx < len(tokens):
                    v = tokens[idx]; idx += 1
                    if item == '-I': include_dirs.add(v)
                    elif item == '-D': defines.add(v)
                    elif item == '-v': sources.add((path.parent / v).resolve())
                    else: warnings.append(f'library directory needs elaborator handling: {v}')
                continue
            if item.startswith('-I') and len(item) > 2:
                include_dirs.add(item[2:]); continue
            if item.startswith('-D') and len(item) > 2:
                defines.add(item[2:]); continue
            if item.startswith('-') or item.startswith('+'):
                warnings.append('unparsed filelist option: ' + item)
                continue
            f = (path.parent / item).resolve()
            if f.suffix in RTL_EXTS | HEADER_EXTS:
                sources.add(f)
            else:
                warnings.append('unrecognized filelist token: ' + item)

    parse_one(fl)
    return sources, sorted(include_dirs), sorted(defines), warnings


def get_inventory(root: Path, filelist: Path | None = None) -> dict:
    root = root.resolve()
    warnings = ['Lexical/heuristic inventory only: not SystemVerilog elaboration, width resolution, or functional proof.']
    if filelist:
        paths, include_dirs, defines, msgs = parse_filelist(root, filelist)
        warnings.extend(msgs)
    else:
        include_dirs, defines = [], []
        paths = {p.resolve() for p in root.rglob('*') if p.is_file()
                 and p.suffix in RTL_EXTS | HEADER_EXTS
                 and not any(part in EXCLUDED_DIRS or part.startswith('.') for part in p.relative_to(root).parts[:-1])}
    sources = []
    modules = []
    for path in sorted(paths):
        if not path.is_file():
            warnings.append(f'input RTL not found: {path}')
            continue
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            warnings.append(f'file outside root omitted: {path}')
            continue
        raw = path.read_bytes()
        text = raw.decode('utf-8', errors='replace')
        entry = {'path': rel, 'sha256': hashlib.sha256(raw).hexdigest(),
                 'lines': len(text.splitlines()), 'modules': [], 'kind': path.suffix}
        sources.append(entry)
        if path.suffix not in RTL_EXTS:
            continue
        clean = strip_comments_and_strings(text)
        pos = 0
        while True:
            m = MOD_DECL.search(clean, pos)
            if not m:
                break
            # Ignore `module` in `endmodule` (regex word boundary already handles it).
            mend = END_DECL.search(clean, m.end())
            if mend is None:
                warnings.append(f'no endmodule: {rel}:{line_at(clean, m.start())}')
                break
            snippet = clean[m.start():mend.start()]
            params, ports, issues = parse_header(snippet, m.group(1), rel, line_at(clean, m.start()))
            for issue in issues:
                warnings.append(f'{rel}:{line_at(clean, m.start())}: {issue}')
            mod = {'name': m.group(1), 'file': rel,
                   'line': line_at(clean, m.start()), 'end_line': line_at(clean, mend.end()),
                   'parameters': params, 'ports': ports, 'instantiations': [],
                   'analysis_level': 'lexical-candidate'}
            modules.append(mod)
            entry['modules'].append(m.group(1))
            pos = mend.end()
    names = {m['name'] for m in modules}
    for name in sorted(names):
        declarations = [m['file'] + ':' + str(m['line']) for m in modules if m['name'] == name]
        if len(declarations) > 1:
            warnings.append('duplicate module declaration: ' + name + ' -> ' + ', '.join(declarations))
    by_file_clean = {f['path']: strip_comments_and_strings((root / f['path']).read_text(errors='replace'))
                     for f in sources if f['kind'] in RTL_EXTS}
    for mod in modules:
        text = by_file_clean[mod['file']]
        start = sum(len(line) + 1 for line in text.split('\n')[:mod['line'] - 1])
        stop = sum(len(line) + 1 for line in text.split('\n')[:mod['end_line']])
        mod['instantiations'] = instance_candidates(text[start:stop], names - {mod['name']})
    instantiated = {inst['module'] for mod in modules for inst in mod['instantiations']}
    tops = [m['name'] for m in modules if m['name'] not in instantiated]
    if len(tops) != 1:
        warnings.append('Top module ambiguous; choose --top using build/elaboration evidence.')
    return {'format_version': 1, 'root': str(root),
            'filelist': str(filelist.resolve()) if filelist else None,
            'include_dirs': include_dirs, 'defines': defines,
            'files': sources, 'modules': modules, 'top_candidates': sorted(set(tops)),
            'warnings': warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--filelist', type=Path, help='Optional .f; simple flags only, no full preprocessor')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error('--root is not a directory')
    inventory = get_inventory(args.root, args.filelist)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + '\n')
    print(f"Inventory: {len(inventory['files'])} files, {len(inventory['modules'])} modules; "
          f"top candidates {inventory['top_candidates']}; warnings {len(inventory['warnings'])}")
    print(f"Written: {args.out}")


if __name__ == '__main__':
    main()
