#!/usr/bin/env python3
"""Report local Synopsys EDA presence; do not attempt license check or installation."""
import json
import os
from pathlib import Path
import shutil
import sys


def resolve(tool):
    found = shutil.which(tool)
    if not found and tool in ('verdi', 'fsdb2vcd') and os.getenv('VERDI_HOME'):
        candidate = Path(os.environ['VERDI_HOME']) / 'bin' / tool
        if candidate.is_file():
            found = str(candidate)
    return found

if __name__ == '__main__':
    print(json.dumps({'python': sys.version.split()[0],
                      'primary_eda': {t: resolve(t) for t in ('vcs', 'verdi', 'fsdb2vcd')},
                      'verdi_home_set': bool(os.getenv('VERDI_HOME')),
                      'licenses_checked': False,
                      'notes': 'VCS/Verdi are commercial, optional at authoring time but mandatory for vendor-verified claims; static source-backed docs remain possible.'},
                     indent=2, ensure_ascii=False))
