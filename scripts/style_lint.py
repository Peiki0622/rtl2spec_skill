#!/usr/bin/env python3
"""Check generated Chinese RTL specifications for robotic phrasing and repeated disclaimers.

A *writing* linter: it does not decide technical truth or replace RTL inspection.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

# These expressions flag generic prose, not technical terms or legitimate constraints.
FILLER = re.compile(
    r'需要注意的是|值得注意的是|值得一提的是|综上所述|总而言之|总体而言|'
    r'从某种意义上(?:讲)?|众所周知|如前所述|显而易见|'
    r'从(?:整体|架构|实现)层面(?:的角度)?来看|切实提升|赋能|提质增效|'
    r'充分体现|全面保障|重要意义|本模块旨在'
)
DEFENSIVE = re.compile(
    r'不构成.{0,24}(?:正确性|证明|保证)|不能证明.{0,24}(?:正确|功能)|'
    r'不代表.{0,24}(?:功能|正确性)|仅供参考|'
    r'NOT A CORRECTNESS PROOF|NOT AUTOMATICALLY VERIFIED|NOT SIMULATED',
    flags=re.I,
)
# It is appropriate to record genuine gaps exactly once in the verification chapters.
EVIDENCE_CHAPTERS = (
    'Document Control', 'Verification and Evidence', 'Traceability and Open Issues',
    'Verification Evidence', 'RTL Traceability and Open Issues',
)


def review_text(content: str, path: str = '<text>') -> list[dict]:
    findings: list[dict] = []
    heading = ''
    fenced = False
    for no, raw in enumerate(content.splitlines(), start=1):
        line = raw.strip()
        if line.startswith('```') or line.startswith('~~~'):
            fenced = not fenced
            continue
        if fenced or not line or line.startswith(('|', '![', '<!--')):
            continue
        if line.startswith('## '):
            heading = line[3:]
            continue
        if line.startswith('#'):
            continue
        # Code spans, file references and links are not writing prose.
        prose = re.sub(r'`[^`]*`', '', line)
        prose = re.sub(r'\]\([^)]*\)', ']', prose)
        for kind, expression in (('empty_phrase', FILLER), ('repeated_disclaimer', DEFENSIVE)):
            if kind == 'repeated_disclaimer' and any(x in heading for x in EVIDENCE_CHAPTERS):
                continue
            match = expression.search(prose)
            if match:
                findings.append({'file': path, 'line': no, 'kind': kind,
                                 'fragment': match.group(0), 'text': line[:180]})
    return findings


def review_docs(docs: Path) -> dict:
    files = sorted([docs / 'ip_spec.md', *list((docs / 'modules').glob('*.md'))])
    results: list[dict] = []
    for f in files:
        if f.is_file():
            results.extend(review_text(f.read_text(encoding='utf-8'), str(f)))
    return {'status': 'REVIEW' if results else 'PASS', 'files_checked': sum(f.is_file() for f in files),
            'findings': results,
            'scope': 'Writing style only; no RTL functional verification'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docs', type=Path, required=True)
    parser.add_argument('--strict', action='store_true', help='Nonzero exit code for flagged prose')
    parser.add_argument('--json-out', type=Path, help='Optional JSON report path')
    args = parser.parse_args()
    report = review_docs(args.docs)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{report["status"]}: checked {report["files_checked"]} documents, '
          f'{len(report["findings"])} style findings')
    for item in report['findings']:
        print(f'  {item["file"]}:{item["line"]} [{item["kind"]}] {item["fragment"]}')
    raise SystemExit(1 if args.strict and report['findings'] else 0)


if __name__ == '__main__':
    main()
