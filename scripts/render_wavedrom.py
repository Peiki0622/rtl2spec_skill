#!/usr/bin/env python3
"""Offline SVG renderer for a documented, narrow subset of WaveDrom JSON.

Supported wave chars: p, 0, 1, x, z, =, . . This is NOT upstream WaveDrom.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from xml.etree import ElementTree as ET

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def add(parent, tag, attrs=None, txt=None):
    e = ET.SubElement(parent, '{' + NS + '}' + tag, {k: str(v) for k, v in (attrs or {}).items()})
    if txt is not None:
        e.text = str(txt)
    return e


def expand_wave(row, n):
    s = row['wave']
    if len(s) != n:
        raise ValueError('Inconsistent wave lengths: ' + row['name'])
    data = iter(row.get('data', []))
    expanded = []
    last = None
    for ch in s:
        if ch not in 'p01xz=.':
            raise ValueError(f'Unsupported wave symbol {ch!r}: {row["name"]}; use real WaveDrom renderer')
        if ch == '.':
            if last is None:
                raise ValueError('Wave begins with dot: ' + row['name'])
            expanded.append(last)
        elif ch == '=':
            try:
                label = next(data)
            except StopIteration:
                raise ValueError('Missing data entry for bus: ' + row['name']) from None
            last = ('=', str(label))
            expanded.append(last)
        else:
            last = (ch, None)
            expanded.append(last)
    if next(data, None) is not None:
        raise ValueError('Extra data labels for ' + row['name'])
    return expanded


def render(input_path: Path, output_path: Path) -> None:
    diagram = json.loads(input_path.read_text(encoding='utf-8'))
    rows = diagram.get('signal')
    if not isinstance(rows, list) or not rows:
        raise ValueError('WaveDrom JSON must contain nonempty signal array')
    if any(not isinstance(r, dict) or not isinstance(r.get('wave'), str) or not isinstance(r.get('name'), str)
           for r in rows):
        raise ValueError('Each signal must contain name and wave')
    n = len(rows[0]['wave'])
    if not 1 <= n <= 256:
        raise ValueError('1..256 cycles supported')
    norm = [expand_wave(r, n) for r in rows]
    cwidth, labelw, rh = 76, 250, 45
    total_w, total_h = labelw + n * cwidth + 22, 102 + len(rows) * rh
    svg = ET.Element('{' + NS + '}svg', {'viewBox': f'0 0 {total_w} {total_h}',
                                          'width': str(total_w), 'height': str(total_h),
                                          'role': 'img', 'aria-label': 'RTL timing diagram'})
    add(svg, 'rect', {'width': total_w, 'height': total_h, 'fill': '#ffffff'})
    title = diagram.get('head', {}).get('text', 'RTL Timing Example')
    add(svg, 'text', {'x': 20, 'y': 28, 'font-size': 17, 'font-family': 'Arial, sans-serif',
                      'font-weight': 700, 'fill': '#203049'}, title)
    add(svg, 'text', {'x': 20, 'y': 49, 'font-size': 11, 'font-family': 'Arial, sans-serif',
                      'fill': '#627084'}, 'One column = one clock sample | values shown after sample timestamp')
    start_y = 84
    for col in range(n + 1):
        x = labelw + col * cwidth
        add(svg, 'line', {'x1': x, 'x2': x, 'y1': start_y - 19,
                          'y2': start_y + rh * len(rows) - 1,
                          'stroke': '#dde5ed', 'stroke-dasharray': '3,4', 'stroke-width': 1})
        if col < n:
            add(svg, 'text', {'x': x + cwidth / 2, 'y': start_y - 25,
                              'text-anchor': 'middle', 'font-family': 'Arial, sans-serif',
                              'font-size': 11, 'fill': '#627084'}, str(col))
    for idx, (r, tokens) in enumerate(zip(rows, norm)):
        y = start_y + idx * rh + rh / 2
        if idx % 2 == 0:
            add(svg, 'rect', {'x': 0, 'y': y - rh / 2 + 1, 'width': total_w,
                              'height': rh - 1, 'fill': '#f8fafc'})
        label = r['name']
        if len(label) > 36:
            label = label[:15] + '…' + label[-18:]
        add(svg, 'text', {'x': 19, 'y': y + 4, 'font-family': 'Arial, sans-serif',
                          'font-size': 12, 'fill': '#23364c'}, label)
        for col, token in enumerate(tokens):
            kind, value = token
            x = labelw + col * cwidth
            color = '#16728e' if kind == '=' else '#3160a0'
            top, bottom = y - 10, y + 10
            if kind == 'p':
                points = [(x, bottom), (x + 8, bottom), (x + 8, top),
                          (x + cwidth/2, top), (x + cwidth/2, bottom), (x + cwidth, bottom)]
                add(svg, 'polyline', {'points': ' '.join(f'{a},{b}' for a, b in points),
                                      'fill': 'none', 'stroke': '#3160a0', 'stroke-width': 2})
            elif kind in ('0', '1'):
                level = top if kind == '1' else bottom
                add(svg, 'line', {'x1': x, 'y1': level, 'x2': x + cwidth, 'y2': level,
                                  'stroke': color, 'stroke-width': 2})
                if col > 0 and tokens[col-1][0] in ('0', '1') and tokens[col-1][0] != kind:
                    add(svg, 'line', {'x1': x, 'y1': top, 'x2': x, 'y2': bottom,
                                      'stroke': color, 'stroke-width': 2})
            elif kind == '=':
                # Merge continued bus values so that text is centered over the full segment.
                if col > 0 and tokens[col-1] == token:
                    continue
                span = 1
                while col + span < n and tokens[col + span] == token:
                    span += 1
                w = span * cwidth
                add(svg, 'rect', {'x': x + 2, 'y': top - 4, 'width': w - 4, 'height': 28,
                                  'rx': 5, 'fill': '#e8f5f9', 'stroke': '#1a7390',
                                  'stroke-width': 1.3})
                label_text = value if len(value) < 36 else value[:32] + '…'
                add(svg, 'text', {'x': x + w/2, 'y': y + 5,
                                  'text-anchor': 'middle', 'font-family': 'monospace',
                                  'font-size': 11, 'fill': '#185e78'}, label_text)
            elif kind in ('x', 'z'):
                add(svg, 'rect', {'x': x + 2, 'y': top, 'width': cwidth - 4,
                                  'height': 20, 'fill': '#eef1f6', 'stroke': '#9aa6b5'})
                add(svg, 'text', {'x': x + cwidth/2, 'y': y + 4,
                                  'text-anchor': 'middle', 'font-family': 'monospace',
                                  'font-size': 12, 'fill': '#64748b'}, kind.upper())
    add(svg, 'text', {'x': 20, 'y': total_h - 8, 'font-size': 10,
                      'font-family': 'Arial, sans-serif', 'fill': '#8a96a5'},
        'Generated by rtl-to-spec subset renderer; visual display is not functional verification.')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(svg).write(output_path, encoding='utf-8', xml_declaration=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True, help='Strict JSON WaveDrom file')
    p.add_argument('--output', type=Path, required=True, help='SVG output')
    args = p.parse_args()
    try:
        render(args.input, args.output)
    except (ValueError, OSError, json.JSONDecodeError) as ex:
        p.error(str(ex))
    print(f'Created {args.output}')

if __name__ == '__main__':
    main()
