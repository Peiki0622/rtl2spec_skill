#!/usr/bin/env python3
"""Synopsys VCS + Verdi bridge for RTL-to-Spec.

The default is DRY RUN. Each execution requires --execute. Do not edit RTL or
infer functional correctness from exit code, FSDB presence, or conversion.
This is an adapter for *locally licensed* vendor tools, not a simulator.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def binary(command: str, env: dict[str, str] | None = None) -> str:
    """Pick an installed binary if available; for dry-run preserve command."""
    if os.path.isabs(command):
        return command
    found = shutil.which(command)
    if found:
        return found
    home = (env or os.environ).get('VERDI_HOME', '')
    if command in ('verdi', 'fsdb2vcd') and home:
        maybe = Path(home) / 'bin' / command
        if maybe.is_file():
            return str(maybe)
    return command


def load_config(path: Path, *, workdir: Path | None = None) -> dict:
    raw = json.loads(path.read_text(encoding='utf-8'))
    required = ('filelist', 'tb_top')
    for name in required:
        if not isinstance(raw.get(name), str) or not raw[name].strip():
            raise ValueError(f'config requires nonempty {name}')
    for name in ('compile_extra', 'run_extra', 'convert_extra'):
        if not isinstance(raw.get(name, []), list) or not all(isinstance(x, str) for x in raw.get(name, [])):
            raise ValueError(f'{name} must be a list of argv strings; not a shell command')
    base = (workdir or path.resolve().parent).resolve()
    root = (base / raw.get('project_root', '.')).resolve()
    if not root.is_dir():
        raise ValueError(f'project_root does not exist: {root}')
    filelist = (root / raw['filelist']).resolve()
    if not filelist.is_file():
        raise ValueError(f'VCS filelist is missing: {filelist}')
    out_dir = (root / raw.get('output_dir', 'docs/rtl_spec/eda')).resolve()
    if not out_dir.is_relative_to(root):
        raise ValueError('output_dir must stay inside project_root')
    # Do not write build artifacts into RTL source directories.
    if out_dir == root:
        raise ValueError('output_dir may not be project_root')
    fsdb = (root / raw.get('fsdb', str(Path(raw.get('output_dir', 'docs/rtl_spec/eda')) / 'waves.fsdb'))).resolve()
    vcd = (root / raw.get('vcd', str(Path(raw.get('output_dir', 'docs/rtl_spec/eda')) / 'waves.vcd'))).resolve()
    if not fsdb.is_relative_to(out_dir) or not vcd.is_relative_to(out_dir):
        raise ValueError('FSDB/VCD paths must stay inside output_dir')
    return {**raw, 'root': root, 'filelist_path': filelist,
            'out': out_dir, 'fsdb_path': fsdb, 'vcd_path': vcd,
            'simv_path': out_dir / 'build' / 'simv'}


def make_commands(cfg: dict) -> dict[str, list[str]]:
    out = cfg['out']; binpath = cfg['simv_path']
    vcs = binary(cfg.get('vcs_binary', 'vcs'))
    verdi = binary(cfg.get('verdi_binary', 'verdi'))
    converter = binary(cfg.get('fsdb2vcd_binary', 'fsdb2vcd'))
    compile_argv = [vcs, '-full64', '-sverilog', '-kdb', '-debug_access+all',
                    '-f', str(cfg['filelist_path']), '-top', cfg['tb_top'],
                    '-o', str(binpath), '-Mdir=' + str(out / 'build' / 'csrc'),
                    '-l', str(out / 'vcs_compile.log'), *cfg.get('compile_extra', [])]
    run_argv = [str(binpath), '-l', str(out / 'vcs_run.log'), *cfg.get('run_extra', [])]
    if cfg.get('fsdb_dump_mode', 'testbench') == 'ucli':
        run_argv += ['-ucli', '-do', str(out / 'fsdb_dump.ucli')]
    elif cfg.get('fsdb_dump_mode', 'testbench') != 'testbench':
        raise ValueError('fsdb_dump_mode must be testbench or ucli')
    return {
        'compile': compile_argv,
        'run': run_argv,
        'convert': [converter, str(cfg['fsdb_path']), '-o', str(cfg['vcd_path']), *cfg.get('convert_extra', [])],
        'open': [verdi, '-ssf', str(cfg['fsdb_path']), '-nologo'],
    }


def save_ucli_dump(cfg: dict) -> Path:
    """Generate a UCLI recipe without changing the existing testbench/DUT."""
    top = cfg['tb_top']
    if not all(c.isalnum() or c in '._$' for c in top):
        raise ValueError('tb_top is not valid for a simple UCLI scope')
    fsdb = str(cfg['fsdb_path'])
    if '"' in fsdb or '\n' in fsdb or '\\' in fsdb:
        raise ValueError('FSDB path cannot be quoted safely in UCLI')
    dest = cfg['out'] / 'fsdb_dump.ucli'
    dest.write_text('call {$fsdbDumpfile("' + fsdb + '")}\n'
                    'call {$fsdbDumpvars(0, ' + top + ')}\n'
                    'run\nquit\n', encoding='utf-8')
    return dest


def summarize_tools() -> dict:
    tools = {'vcs': binary('vcs'), 'verdi': binary('verdi'),
             'fsdb2vcd': binary('fsdb2vcd')}
    return {'tools': {key: {'resolved': value,
                            'available': Path(value).is_file() or shutil.which(value) is not None}
                      for key, value in tools.items()},
            'verdi_home_set': bool(os.getenv('VERDI_HOME')),
            'license_status': 'NOT CHECKED',
            'notes': 'Vendor licenses and compatibility require an on-premises run.'}


def action(cfg: dict, stage: str, execute: bool = False) -> dict:
    commands = make_commands(cfg)
    command = commands[stage]
    cwd = cfg['root']
    if stage == 'convert' and not execute:
        note = 'FSDB must be generated by a real VCS run; conversion does not test behavior.'
    elif stage == 'open':
        note = 'Verdi GUI needs an available display; do not claim any review based on an unlaunched GUI.'
    else:
        note = 'Exit code alone is NOT a testbench functional PASS.'
    record = {'stage': stage, 'tool': 'Synopsys VCS' if stage in ('compile','run') else 'Synopsys Verdi',
              'requested_at_utc': datetime.now(timezone.utc).isoformat(),
              'command': command, 'cwd': str(cwd),
              'filelist_sha256': sha256(cfg['filelist_path']),
              'executed': False, 'status': 'DRY_RUN', 'functional_check': 'NOT_ASSESSED',
              'fsdb': str(cfg['fsdb_path']), 'note': note}
    if not execute:
        return record
    if stage in ('run', 'convert', 'open'):
        needed = cfg['simv_path'] if stage == 'run' else cfg['fsdb_path']
        if not needed.is_file():
            raise FileNotFoundError(f'{stage}: missing prerequisite: {needed}')
    if stage == 'open' and not (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
        raise RuntimeError('Verdi GUI requires DISPLAY/WAYLAND_DISPLAY')
    if not (Path(command[0]).is_file() or shutil.which(command[0])):
        raise FileNotFoundError(f'{stage}: executable not found: {command[0]}')
    cfg['out'].mkdir(parents=True, exist_ok=True)
    (cfg['out'] / 'build').mkdir(exist_ok=True)
    if stage == 'run' and cfg.get('fsdb_dump_mode') == 'ucli':
        save_ucli_dump(cfg)
    record['executed'] = True
    try:
        proc = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                              errors='replace', timeout=cfg.get('timeout_seconds', 1800),
                              check=False)
        record['returncode'] = proc.returncode
        (cfg['out'] / f'{stage}.stdout.log').write_text(proc.stdout + '\n' + proc.stderr, encoding='utf-8')
        record['status'] = 'PROCESS_EXIT_0_UNQUALIFIED' if proc.returncode == 0 else 'PROCESS_FAILED'
        if stage == 'run':
            record['fsdb_exists'] = cfg['fsdb_path'].is_file()
            if record['fsdb_exists']:
                record['fsdb_sha256'] = sha256(cfg['fsdb_path'])
            else:
                record['note'] += ' FSDB not found at configured output path; confirm TB/UCLI dump scope.'
        if stage == 'convert' and cfg['vcd_path'].is_file():
            record['fsdb_sha256'] = sha256(cfg['fsdb_path'])
            record['vcd_sha256'] = sha256(cfg['vcd_path'])
            record['vcd_path'] = str(cfg['vcd_path'])
        if stage == 'compile' and cfg['simv_path'].is_file():
            record['simv_sha256'] = sha256(cfg['simv_path'])
    except subprocess.TimeoutExpired as exc:
        record['status'] = 'TIMEOUT'; record['error'] = str(exc)
    # Never stamp a process exit as SIMULATION-PASS. Explicit checker analysis is a separate action.
    (cfg['out'] / f'{stage}_manifest.json').write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
    return record


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, help='JSON with project_root, filelist, tb_top and output settings')
    p.add_argument('--execute', action='store_true', help='Really invoke a licensed EDA tool (default: plan only)')
    p.add_argument('stage', choices=('doctor', 'plan', 'compile', 'run', 'convert', 'open'))
    args = p.parse_args()
    if args.stage == 'doctor':
        print(json.dumps(summarize_tools(), indent=2, ensure_ascii=False)); return 0
    if not args.config:
        p.error('--config is mandatory except for doctor')
    try:
        cfg = load_config(args.config)
        if args.stage == 'plan':
            result = {'dry_run': True, 'commands': make_commands(cfg),
                      'fsdb_dump_mode': cfg.get('fsdb_dump_mode', 'testbench'),
                      'status': 'NOT RUN', 'functional_check': 'NOT_ASSESSED'}
        else:
            result = action(cfg, args.stage, args.execute)
    except (ValueError, OSError, RuntimeError, json.JSONDecodeError) as exc:
        p.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result.get('status') in ('PROCESS_FAILED', 'TIMEOUT'):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
