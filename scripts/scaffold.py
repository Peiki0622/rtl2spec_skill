#!/usr/bin/env python3
"""Create non-destructive specification drafts from lexical inventory."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def make_draft(root: Path, inventory_path: Path, out: Path, top: str | None,
               overwrite: bool = False) -> tuple[list[Path], list[Path]]:
    inv = json.loads(inventory_path.read_text())
    names = {m['name'] for m in inv['modules']}
    if len(names) != len(inv['modules']):
        raise ValueError('duplicate module names in inventory; resolve active compiled configuration first')
    if top is None:
        candidates = inv['top_candidates']
        if len(candidates) != 1:
            raise ValueError(f'--top required: candidates={candidates}')
        top = candidates[0]
    if top not in names:
        raise ValueError(f'--top {top!r} not found in inventory')
    skill_dir = Path(__file__).resolve().parent.parent
    templates = skill_dir / 'assets' / 'templates'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'modules').mkdir(exist_ok=True)
    (out / 'waveforms').mkdir(exist_ok=True)
    written, skipped = [], []
    for mod in inv['modules']:
        dest = out / 'modules' / (mod['name'] + '.md')
        if dest.exists() and not overwrite:
            skipped.append(dest); continue
        template = (templates / 'module_spec.md').read_text()
        dest.write_text(template.format(module=mod['name'], source=mod['file'], line=mod['line']))
        written.append(dest)
    dest = out / 'ip_spec.md'
    if not dest.exists() or overwrite:
        index = '\n'.join(f"- [{m['name']}](modules/{m['name']}.md) — `{m['file']}:{m['line']}`"
                          for m in inv['modules'])
        dest.write_text((templates / 'ip_spec.md').read_text().format(top=top, module_index=index))
        written.append(dest)
    else:
        skipped.append(dest)
    return written, skipped


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--inventory', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--top', help='Explicit top module; required if ambiguous')
    p.add_argument('--overwrite', action='store_true', help='EXPLICIT destructive replacement')
    args = p.parse_args()
    try:
        written, skipped = make_draft(args.root, args.inventory, args.out, args.top, args.overwrite)
    except ValueError as ex:
        p.error(str(ex))
    print(f'Drafts written: {len(written)}; existing preserved: {len(skipped)}')
    for f in written:
        print(f'  + {f}')
    for f in skipped:
        print(f'  = {f}')
    print('DRAFT ONLY: replace TODOs with source-grounded analysis; no behavior inferred by script.')

if __name__ == '__main__':
    main()
