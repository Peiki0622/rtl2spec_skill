#!/usr/bin/env python3
"""Report optional RTL / waveform tooling availability without installing anything."""
import json
import shutil
import sys

TOOLS = ('python3', 'verilator', 'iverilog', 'vvp', 'yosys', 'slang', 'wavepeek',
         'wave-mcp', 'vcd2fst', 'wavedrom-cli', 'dot')

if __name__ == '__main__':
    print(json.dumps({'python': sys.version.split()[0],
                      'tools': {tool: shutil.which(tool) for tool in TOOLS},
                      'notes': 'Optional EDA tools absent: static docs remain possible; do not claim simulation.'},
                     indent=2, ensure_ascii=False))
