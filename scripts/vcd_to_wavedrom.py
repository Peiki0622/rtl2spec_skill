#!/usr/bin/env python3
"""Extract clock-edge samples from VCD and produce strict-JSON WaveDrom + provenance.

Limited, independently authored parser. Does not prove waveform origin or design correctness.
Only value-change formats `0id`, `1id`, `xid`, `zid`, and `bBINARY id` are supported.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path


def parse_header(fh):
    scopes = []
    names = {}
    widths = {}
    timescale = 'not-declared'
    multiline_time = False
    time_buffer = ''
    for raw in fh:
        line = raw.strip()
        if multiline_time:
            time_buffer += ' ' + line
            if '$end' in line:
                timescale = ' '.join(time_buffer.replace('$end', '').split())
                multiline_time = False
            continue
        if line.startswith('$timescale'):
            part = line.replace('$timescale', '', 1)
            if '$end' in part:
                timescale = ' '.join(part.replace('$end', '').split())
            else:
                time_buffer = part
                multiline_time = True
        elif line.startswith('$scope '):
            toks = line.split()
            if len(toks) > 2:
                scopes.append(toks[2])
        elif line.startswith('$upscope'):
            if scopes:
                scopes.pop()
        elif line.startswith('$var '):
            toks = line.split()
            if len(toks) >= 6:
                width = int(toks[2]); ident = toks[3]; local = toks[4]
                # The same ID may be aliased under more than one name.
                full = '.'.join([*scopes, local])
                names[full] = ident
                widths[ident] = max(width, widths.get(ident, 0))
        elif line.startswith('$enddefinitions'):
            break
    if not names:
        raise ValueError('No $var declarations found (not a VCD header?)')
    return names, widths, timescale


def resolve(selectors: list[str], available: dict[str, str]):
    result = []
    for selector in selectors:
        if selector in available:
            full = selector
        else:
            match = [n for n in available if n.endswith('.' + selector)]
            if len(match) == 1:
                full = match[0]
            elif not match:
                raise ValueError(f'Signal {selector!r} missing from VCD. Examples: {list(available)[:12]}')
            else:
                raise ValueError(f'Ambiguous signal {selector!r}: {match}; use full hierarchical path')
        if full not in result:
            result.append(full)
    return result


def normalize(raw: str, width: int) -> str:
    raw = raw.lower()
    if raw not in ('x', 'z', '0', '1') and re.search(r'[^01xz]', raw):
        return 'x' * width
    if len(raw) >= width:
        return raw[-width:]
    pad = raw[0] if raw[0] in ('x', 'z') else '0'
    return pad * (width - len(raw)) + raw


def vcd_samples(vcd: Path, clock: str, selectors: list[str],
                cycles: int = 16, start: int = 0, end: int | None = None):
    if cycles < 1 or cycles > 256:
        raise ValueError('cycles must be 1..256 (document-focused window)')
    if start < 0 or (end is not None and end < start):
        raise ValueError('invalid time interval')
    snapshots = []
    with vcd.open(encoding='utf-8', errors='replace') as fh:
        names, widths, timescale = parse_header(fh)
        resolved = resolve([clock, *selectors], names)
        clk = resolved[0]
        clk_id = names[clk]
        values = {ident: 'x' * width for ident, width in widths.items()}
        old_clock = values[clk_id]
        now = 0
        seen_timestamp = False

        def commit():
            nonlocal old_clock
            current = values[clk_id]
            if (old_clock == '0' and current == '1' and now >= start
                    and (end is None or now <= end)):
                snapshots.append({'time': now,
                                  'values': {n: values[names[n]] for n in resolved}})
            old_clock = current

        for raw in fh:
            line = raw.strip()
            if not line or line.startswith('$'):
                continue
            if line.startswith('#'):
                if seen_timestamp:
                    commit()
                    if len(snapshots) >= cycles:
                        break
                try:
                    now = int(line[1:])
                except ValueError:
                    raise ValueError('Malformed VCD timestamp: ' + line)
                seen_timestamp = True
                continue
            if line[0] in '01xXzZ' and len(line) >= 2:
                val, ident = line[0], line[1:]
            elif line[0] in 'bB':
                toks = line.split(None, 1)
                if len(toks) != 2:
                    continue
                val, ident = toks[0][1:], toks[1].strip()
            else:
                # Real/string/unknown change records: not interpreted.
                continue
            if ident in values:
                values[ident] = normalize(val, widths[ident])
        else:
            if seen_timestamp:
                commit()
    if not snapshots:
        raise ValueError('No 0->1 clock edges detected in requested VCD window; check clock/time')
    return resolved, names, widths, timescale, snapshots[:cycles]


def logic_symbol(value: str, width: int):
    if width > 1:
        return '=', ('X' if set(value) == {'x'} else 'Z' if set(value) == {'z'}
                     else f'0x{int(value, 2):x}' if set(value) <= {'0', '1'}
                     else value.upper())
    return (value[0] if value[0] in '01xz' else 'x'), None


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def convert(vcd: Path, clock: str, signals: list[str], cycles: int = 16,
            start: int = 0, end: int | None = None):
    resolved, names, widths, timescale, samples = vcd_samples(vcd, clock, signals, cycles, start, end)
    # Clock row is a *cycle marker*, not full event-level clock history.
    rows = [{'name': resolved[0] + ' (posedge)', 'wave': 'p' * len(samples)}]
    for full in resolved[1:]:
        w = widths[names[full]]
        symbols, data = [], []
        previous = None
        for sample in samples:
            value = sample['values'][full]
            kind, label = logic_symbol(value, w)
            if value == previous:
                symbols.append('.')
            else:
                symbols.append(kind)
                if label is not None:
                    data.append(label)
            previous = value
        row = {'name': full, 'wave': ''.join(symbols)}
        if data:
            row['data'] = data
        rows.append(row)
    diagram = {'signal': rows, 'head': {'text': 'VCD 观测 · 来源待核对'},
               'config': {'hscale': 1}}
    metadata = {
        'provenance': 'VCD-OBSERVED (file source and testbench pass status not authenticated)',
        'vcd_path': str(vcd.resolve()),
        'vcd_sha256': hash_file(vcd),
        'vcd_timescale': timescale,
        'sampling': '0->1 clock edge; last value change at each VCD timestamp; post-timestamp snapshot',
        'warning': 'A pre-edge valid && ready transfer cannot be inferred from post-edge values alone.',
        'clock': resolved[0], 'signals': resolved,
        'number_of_edges': len(samples), 'edge_timestamps': [s['time'] for s in samples],
        'time_window_ticks': {'start': start, 'end': end},
        'functional_correctness': 'UNVERIFIED', 'simulator_command': None,
        'testbench_assertions': 'NOT PROVIDED',
    }
    return diagram, metadata


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vcd', type=Path, required=True)
    p.add_argument('--clock', required=True, help='Full VCD hierarchical path; suffix if unambiguous')
    p.add_argument('--signals', nargs='+', required=True, help='Selected signal names (full/suffix)')
    p.add_argument('--cycles', type=int, default=16)
    p.add_argument('--start', type=int, default=0, help='Starting VCD timestamp in VCD ticks')
    p.add_argument('--end', type=int, help='Ending VCD timestamp in VCD ticks')
    p.add_argument('--out', type=Path, required=True, help='WaveDrom .json5 file (strict JSON syntax)')
    p.add_argument('--svg', type=Path, help='Optional SVG rendered with bundled WaveDrom-subset renderer')
    p.add_argument('--verdi-manifest', type=Path, help='Successful fsdb2vcd manifest from vcs_verdi.py')
    p.add_argument('--vcs-run-manifest', type=Path, help='Successful VCS run manifest, required with --verdi-manifest')
    args = p.parse_args()
    if bool(args.verdi_manifest) != bool(args.vcs_run_manifest):
        p.error('Supply BOTH --verdi-manifest and --vcs-run-manifest to label VCS/Verdi provenance')
    try:
        diagram, meta = convert(args.vcd, args.clock, args.signals, args.cycles, args.start, args.end)
    except (ValueError, OSError) as ex:
        p.error(str(ex))
    if args.verdi_manifest:
        try:
            conversion = json.loads(args.verdi_manifest.read_text(encoding='utf-8'))
            run = json.loads(args.vcs_run_manifest.read_text(encoding='utf-8'))
            if conversion.get('stage') != 'convert' or run.get('stage') != 'run':
                raise ValueError('Expected convert/run stage manifests')
            if not all(m.get('executed') and m.get('status') == 'PROCESS_EXIT_0_UNQUALIFIED'
                       for m in (conversion, run)):
                raise ValueError('VCS/Verdi commands did not finish with process exit 0')
            if conversion.get('vcd_sha256') != meta['vcd_sha256']:
                raise ValueError('Verdi conversion manifest hash differs from the supplied VCD')
            if not conversion.get('fsdb_sha256') or conversion['fsdb_sha256'] != run.get('fsdb_sha256'):
                raise ValueError('FSDB hash is missing or differs between VCS and Verdi manifests')
            if not run.get('fsdb_exists'):
                raise ValueError('VCS run manifest lacks FSDB output evidence')
            diagram['head']['text'] = 'VCS/Verdi 波形'
            meta['provenance'] = 'VCS/VERDI-OBSERVED (command/hash chain, no functional proof)'
            meta['fsdb_sha256'] = conversion['fsdb_sha256']
            meta['fsdb_path'] = conversion.get('fsdb')
            meta['verdi_manifest'] = str(args.verdi_manifest.resolve())
            meta['vcs_run_manifest'] = str(args.vcs_run_manifest.resolve())
            meta['functional_correctness'] = 'UNVERIFIED — inspect self-checking TB assertions/results'
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as ex:
            p.error(f'Verdi/VCS provenance check failed: {ex}')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(diagram, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    metadata_path = args.out.with_suffix('.meta.json')
    metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Extracted {meta["number_of_edges"]} edges; {len(meta["signals"])} selected paths')
    print(f'Wrote: {args.out} and {metadata_path}')
    if args.svg:
        from render_wavedrom import render
        render(args.out, args.svg)
        print(f'Wrote: {args.svg}')

if __name__ == '__main__':
    main()
