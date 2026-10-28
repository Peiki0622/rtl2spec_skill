"""Regression tests for readable engineering prose; no external EDA tools required."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from style_lint import review_text, review_docs
from scaffold import make_draft
from inventory import get_inventory
from vcd_to_wavedrom import convert


class WritingQualityTests(unittest.TestCase):
    def test_anti_boilerplate_and_repeated_disclaimer(self):
        text = ('## 8. Functional Operation（工作原理）\n'
                '需要注意的是，本模块旨在实现数据传输。\n'
                '这不构成对功能正确性的保证。\n')
        issues = review_text(text)
        self.assertTrue(any(x['kind'] == 'empty_phrase' for x in issues))
        self.assertTrue(any(x['kind'] == 'repeated_disclaimer' for x in issues))

    def test_verification_notes_are_allowed(self):
        text = ('## 12. Verification and Evidence（验证记录）\n'
                'VCS 未执行，这不构成对功能正确性的保证。\n'
                '## 8. Functional Operation（工作原理）\n'
                '当 `valid` 与 `ready` 同时为 1，完成一次传输。\n')
        self.assertEqual(review_text(text), [])

    def test_concise_rtl_behavior_is_allowed(self):
        text = ('## 8. Functional Operation（工作原理）\n'
                '当 `in_valid && in_ready` 为 1 时，模块在上升沿保存 `in_data`。'
                '下游未就绪时，保持 `out_data`。见 `rv_stage.v:15-25`。')
        self.assertEqual(review_text(text), [])

    def test_complete_example_passes_style_review(self):
        report = review_docs(ROOT / 'examples/demo_output')
        self.assertEqual(report['status'], 'PASS', report['findings'])
        self.assertEqual(report['files_checked'], 2)

    def test_scaffold_includes_concise_chinese_prompts_and_bilingual_headings(self):
        tiny = ROOT / 'examples/tiny_ip'
        inventory = get_inventory(tiny, tiny / 'rtl.f')
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            mf = td / 'inventory.json'; mf.write_text(json.dumps(inventory))
            make_draft(tiny, mf, td / 'docs', 'rv_stage')
            ip = (td / 'docs/ip_spec.md').read_text()
            self.assertIn('## 8. Functional Operation（工作原理）', ip)
            self.assertNotIn('not a proposed design', ip)
            self.assertNotIn('NOT SIMULATED', ip)

    def test_vcd_diagram_head_is_short_and_provenance_stays_in_metadata(self):
        data, metadata = convert(ROOT/'examples/tiny_ip/fixture.vcd', 'tb_rv_stage.clk',
                                 ['tb_rv_stage.out_valid'], cycles=3)
        self.assertEqual(data['head']['text'], 'VCD 观测 · 来源待核对')
        self.assertIn('VCD-OBSERVED', metadata['provenance'])
        self.assertEqual(metadata['functional_correctness'], 'UNVERIFIED')


if __name__ == '__main__':
    unittest.main()
