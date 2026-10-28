#!/usr/bin/env python3
"""Compare cycle-aligned illustrative WaveDrom rows to VCD-derived rows.

This compares sampled diagrams, NOT RTL truth, raw VCD traces, or protocol acceptance.
Clock/sampling convention and cycle-offset compatibility must be established by Codex.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from render_wavedrom import expand_wave


def has_unknown(token):
    kind, value = token
    if kind in ('x', 'z'):
        return True
    if kind == '=' and value is not None:
        label = str(value).strip()
        # Bus labels "X", "Z", or binary bits containing unknowns are not verified.
        if label.lower().startswith('0x') and all(c in '0123456789abcdef' for c in label[2:].lower()):
            return False
        if label.upper() in ('X', 'Z'):
            return True
        if all(c in '01xXzZ' for c in label) and any(c in 'xXzZ' for c in label):
            return True
    return False


def compare(expected_path: Path, observed_path: Path, signals: list[str] | None = None):
    exp = json.loads(expected_path.read_text(encoding='utf-8'))
    obs = json.loads(observed_path.read_text(encoding='utf-8'))
    exp_rows = {r['name']: r for r in exp['signal']}
    obs_rows = {r['name']: r for r in obs['signal']}
    if signals is None:
        signals = [n for n in exp_rows if n in obs_rows and ' (posedge)' not in n]
    if not signals:
        raise ValueError('No comparable signals (use --signals with exact shared names)')
    if not all(s in exp_rows and s in obs_rows for s in signals):
        raise ValueError(f'Selected signals must exist in both diagrams; exp={list(exp_rows)}, obs={list(obs_rows)}')
    mismatches, inconclusive, matches = [], [], 0
    for s in signals:
        want = exp_rows[s]; got = obs_rows[s]
        expected = expand_wave(want, len(want['wave']))
        observed = expand_wave(got, len(got['wave']))
        if len(expected) != len(observed):
            raise ValueError(f'Cycle lengths differ for {s}: {len(expected)} vs {len(observed)}')
        for i, (a, b) in enumerate(zip(expected, observed)):
            if has_unknown(a) or has_unknown(b):
                inconclusive.append({'signal': s, 'cycle': i, 'expected': a, 'observed': b})
            elif a != b:
                mismatches.append({'signal': s, 'cycle': i, 'expected': a, 'observed': b})
            else:
                matches += 1
    return {'status': 'MISMATCH' if mismatches else 'NO_MISMATCH_IN_SELECTED_CYCLES',
            'expected': str(expected_path), 'observed': str(observed_path),
            'signals': signals, 'matching_cells': matches,
            'mismatches': mismatches, 'inconclusive_cells': inconclusive,
            'disclaimer': 'Requires aligned cycles/clock semantics; matching values do not establish functional correctness.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expected', type=Path, required=True, help='Illustrative WaveDrom')
    p.add_argument('--observed', type=Path, required=True, help='VCD-derived WaveDrom')
    p.add_argument('--signals', nargs='*', help='Exact signal names present in both; default shared signals')
    p.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    try:
        report = compare(args.expected, args.observed, args.signals)
    except (OSError, ValueError, KeyError, TypeError) as e:
        p.error(str(e))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    print(f"{report['status']}: {report['matching_cells']} matched, {len(report['mismatches'])} mismatched, "
          f"{len(report['inconclusive_cells'])} inconclusive; report={args.report}")
    if report['mismatches']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
