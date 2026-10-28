#!/usr/bin/env python3
"""Lint as-implemented RTL specs, citations, waveform syntax and RTL snapshot integrity."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

MODULE_HEADINGS = ('Function', 'Parameters', 'Interface', 'Clock and Reset',
                   'State and Algorithm', 'Cycle Timing', 'Waveform Scenarios',
                   'Source Evidence', 'Unknowns and Verification')
IP_HEADINGS = ('Overview', 'Hierarchy and Architecture', 'Interfaces',
               'Clock and Reset Domains', 'Behavior and Timing', 'Waveform Scenarios',
               'Verification', 'Assumptions and Open Questions', 'Source Evidence')
EVIDENCE = re.compile(r'(?<![\w/])([\w./-]+\.(?:svh|sv|vh|v)):(\d+)(?:-\d+)?')
IMG_LINKS = re.compile(r'!\[[^]]*\]\(([^)]+\.svg)\)')


def validate(root: Path, docs: Path, inventory_path: Path, strict: bool):
    errors, warnings, checks = [], [], []
    inv = json.loads(inventory_path.read_text(encoding='utf-8'))
    sources = {item['path']: item for item in inv['files']}
    for source, item in sources.items():
        actual = root / source
        if not actual.is_file():
            errors.append('RTL source missing since inventory: ' + source)
        elif hashlib.sha256(actual.read_bytes()).hexdigest() != item['sha256']:
            errors.append('RTL changed since inventory snapshot: ' + source)
        else:
            checks.append('source snapshot match: ' + source)

    targets = [(docs / 'ip_spec.md', IP_HEADINGS)]
    for mod in inv['modules']:
        targets.append((docs / 'modules' / (mod['name'] + '.md'), MODULE_HEADINGS))
    cited = set()
    for doc, required in targets:
        if not doc.is_file():
            errors.append('missing document: ' + str(doc))
            continue
        txt = doc.read_text(encoding='utf-8')
        if strict and re.search(r'\bTODO\b|\[TODO|DRAFT —', txt, flags=re.I):
            errors.append('uncompleted template placeholders: ' + str(doc))
        for heading in required:
            if not re.search(r'^##\s+' + re.escape(heading) + r'\s*$', txt, flags=re.M):
                errors.append(f'{doc.name}: missing heading ## {heading}')
        valid_refs = 0
        for m in EVIDENCE.finditer(txt):
            path, line = m.group(1), int(m.group(2))
            # Common forms `./rtl/foo.v` and `rtl/foo.v`
            path = path.removeprefix('./')
            if path not in sources:
                errors.append(f'{doc.name}: cited RTL not in inventory: {path}:{line}')
            elif not (1 <= line <= sources[path]['lines']):
                errors.append(f'{doc.name}: cited line out of range: {path}:{line}')
            else:
                valid_refs += 1
                cited.add(path)
        if strict and valid_refs == 0:
            errors.append(f'{doc.name}: no verifiable RTL path:line citations')
        for rel in IMG_LINKS.findall(txt):
            if not (doc.parent / rel).is_file():
                errors.append(f'{doc.name}: missing linked SVG: {rel}')
        checks.append(f'{doc.name}: required section and citation lint completed')
    wave_dir = docs / 'waveforms'
    wave_files = sorted(wave_dir.glob('*.json5')) + sorted(wave_dir.glob('*.json')) if wave_dir.exists() else []
    wave_files = [w for w in wave_files if not w.name.endswith('.meta.json')]
    if strict and not wave_files:
        errors.append('no WaveDrom scenarios found under waveforms/')
    for wave in wave_files:
        try:
            data = json.loads(wave.read_text(encoding='utf-8'))
            rows = data['signal']
            n = len(rows[0]['wave'])
            if not 1 <= n <= 256:
                raise ValueError('cycle count must be 1..256')
            for row in rows:
                s = row['wave']
                if len(s) != n or any(ch not in '01xz=.p' for ch in s):
                    raise ValueError('inconsistent/unsupported symbols for ' + row.get('name', '?'))
                if s[0] == '.':
                    raise ValueError('first symbol cannot be .')
                if s.count('=') != len(row.get('data', [])):
                    raise ValueError('each = segment requires one data label')
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as ex:
            errors.append(f'invalid WaveDrom data {wave.name}: {ex}')
            continue
        if not wave.with_suffix('.svg').is_file():
            errors.append(f'waveform SVG missing: {wave.with_suffix(".svg").name}')
        meta = wave.with_suffix('.meta.json')
        heading = data.get('head', {}).get('text', '').upper()
        if meta.is_file():
            m = json.loads(meta.read_text())
            if m.get('provenance', '').startswith('VCD-OBSERVED') and 'VCD OBSERVED' not in heading:
                errors.append('VCD metadata present but wave label not VCD OBSERVED: ' + wave.name)
        elif not ('ILLUSTRATIVE' in heading or 'VCD OBSERVED' in heading):
            errors.append('waveform missing explicit origin/provenance label: ' + wave.name)
        checks.append(f'waveform parsed: {wave.name}')
    if strict and (docs / 'ip_spec.md').is_file():
        iptxt = (docs / 'ip_spec.md').read_text()
        if not IMG_LINKS.search(iptxt):
            errors.append('ip_spec.md has no embedded timing SVG reference')
    if strict:
        for m in inv['modules']:
            if m['file'] not in cited:
                warnings.append('RTL file with no cited module doc evidence: ' + m['file'])
    if len(inv['top_candidates']) != 1:
        warnings.append('ambiguous lexical top candidates: ' + repr(inv['top_candidates']))
    report = {'status': 'FAIL' if errors else 'PASS', 'mode': 'strict' if strict else 'draft',
              'docs': str(docs.resolve()), 'errors': errors, 'warnings': warnings,
              'checks': checks,
              'disclaimer': 'Lint checks structure and file-line existence; not functional correctness.'}
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--docs', type=Path, required=True)
    p.add_argument('--inventory', type=Path, required=True)
    p.add_argument('--strict', action='store_true', help='Fail on drafts, missing waves or citations')
    args = p.parse_args()
    try:
        report = validate(args.root.resolve(), args.docs, args.inventory, args.strict)
    except (ValueError, OSError, json.JSONDecodeError) as ex:
        p.error(str(ex))
    args.docs.mkdir(parents=True, exist_ok=True)
    path = args.docs / 'validation_report.json'
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(f'{report["status"]}: {len(report["errors"])} errors, {len(report["warnings"])} warnings; report {path}')
    for error in report['errors'][:30]:
        print('  ERROR:', error)
    for warning in report['warnings'][:10]:
        print('  WARN:', warning)
    sys.exit(1 if report['errors'] else 0)

if __name__ == '__main__':
    main()
