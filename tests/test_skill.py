"""No EDA tools required. Synthetic VCD checks parsing only, not RTL simulation."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / 'scripts'))
from inventory import get_inventory, strip_comments_and_strings
from scaffold import make_draft
from vcd_to_wavedrom import convert, vcd_samples
from render_wavedrom import render
from validate import validate
from compare_waveforms import compare, has_unknown


class InventoryTests(unittest.TestCase):
    def test_example_module_port_width_and_top(self):
        root = BASE / 'examples' / 'tiny_ip'
        inv = get_inventory(root, root / 'rtl.f')
        self.assertEqual(inv['top_candidates'], ['rv_stage'])
        self.assertEqual(len(inv['modules']), 1)
        mod = inv['modules'][0]
        self.assertEqual(len(mod['ports']), 8)
        self.assertEqual(mod['parameters'], [{'name': 'WIDTH', 'default_expr': '8'}])
        self.assertEqual({p['name']: p['width_expr'] for p in mod['ports']}['in_data'], '[WIDTH-1:0]')

    def test_fake_module_comments_and_strings_removed(self):
        txt = '// module fake; endmodule\n/* module fake2; endmodule */\n$display("module fake3;");\nmodule real; endmodule'
        clean = strip_comments_and_strings(txt)
        self.assertNotIn('module fake', clean)
        self.assertIn('module real', clean)

    def test_child_instance_discovery_heuristic(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'top.sv').write_text('module top(input logic clk);\nchild #(.W(8)) u_child(.clk(clk));\nendmodule\n')
            (root / 'child.sv').write_text('module child #(parameter W=4)(input clk); endmodule')
            inv = get_inventory(root)
            self.assertEqual(inv['top_candidates'], ['top'])
            top = next(m for m in inv['modules'] if m['name']=='top')
            self.assertEqual(top['instantiations'][0]['instance'], 'u_child')
            self.assertEqual(top['instantiations'][0]['confidence'], 'candidate-not-elaborated')

    def test_non_ansi_port_declarations(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'legacy.v').write_text('module legacy(a,b);\ninput [3:0] a;\noutput reg b;\nendmodule\n')
            inv = get_inventory(root)
            ports = {p['name']: p for p in inv['modules'][0]['ports']}
            self.assertEqual(ports['a']['direction'], 'input')
            self.assertEqual(ports['a']['width_expr'], '[3:0]')
            self.assertEqual(ports['b']['direction'], 'output')


class ScaffoldTests(unittest.TestCase):
    def test_preserve_existing_docs_by_default(self):
        root = BASE / 'examples' / 'tiny_ip'
        inv = get_inventory(root, root / 'rtl.f')
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            manifest = workspace / 'inventory.json'
            manifest.write_text(json.dumps(inv))
            out = workspace / 'spec'
            written, skipped = make_draft(root, manifest, out, 'rv_stage')
            self.assertEqual(len(written), 2)
            saved = (out / 'ip_spec.md').read_text()
            written2, skipped2 = make_draft(root, manifest, out, 'rv_stage')
            self.assertEqual(written2, [])
            self.assertEqual(len(skipped2), 2)
            self.assertEqual((out / 'ip_spec.md').read_text(), saved)
            self.assertIn('[TODO:', saved)


class WaveformTests(unittest.TestCase):
    def test_synthetic_vcd_capture_and_clock_alignment(self):
        vcd = BASE / 'examples' / 'tiny_ip' / 'fixture.vcd'
        data, meta = convert(vcd, 'tb_rv_stage.clk',
                             ['tb_rv_stage.out_valid', 'tb_rv_stage.out_data',
                              'tb_rv_stage.in_ready'], cycles=6)
        self.assertEqual(meta['edge_timestamps'], [5, 15, 25, 35, 45, 55])
        by_name = {r['name']: r for r in data['signal']}
        self.assertEqual(by_name['tb_rv_stage.out_valid']['wave'], '01..0.')
        self.assertEqual(by_name['tb_rv_stage.out_data']['data'], ['0x0', '0xa5', '0x3c'])
        self.assertIn('not authenticated', meta['provenance'])

    def test_ambiguous_suffix_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 't.vcd'
            p.write_text('$scope module a $end\n$var wire 1 ! clk $end\n$upscope $end\n'
                         '$scope module b $end\n$var wire 1 ? clk $end\n$upscope $end\n'
                         '$enddefinitions $end\n#0\n0!\n0?\n#5\n1!\n1?\n')
            with self.assertRaisesRegex(ValueError, 'Ambiguous'):
                vcd_samples(p, 'clk', ['a.clk'])

    def test_renderer_svg_and_invalid_data(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            wave = folder / 'example.json5'
            svg = folder / 'example.svg'
            wave.write_text(json.dumps({'signal': [{'name': 'clk', 'wave': 'ppp'},
                                                          {'name': 'bus', 'wave': '=.=','data':['A','B']},
                                                          {'name': 'valid', 'wave': '010'}],
                                               'head': {'text': 'ILLUSTRATIVE'}}))
            render(wave, svg)
            self.assertIn('svg', svg.read_text())
            wave.write_text(json.dumps({'signal': [{'name': 'bus', 'wave': '==', 'data': ['A']}]}))
            with self.assertRaisesRegex(ValueError, 'Missing data'):
                render(wave, svg)


class ComparisonTests(unittest.TestCase):
    def test_aligned_fixture_matches_illustration(self):
        waves = BASE / 'examples' / 'demo_output' / 'waveforms'
        r = compare(waves / 'accept_stall_illustrative.json5', waves / 'fixture_trace.json5')
        self.assertEqual(r['status'], 'NO_MISMATCH_IN_SELECTED_CYCLES')
        self.assertEqual(r['matching_cells'], 42)

    def test_difference_and_unknown_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            e, o = folder/'e.json5', folder/'o.json5'
            e.write_text(json.dumps({'signal':[{'name':'valid','wave':'010'},
                                               {'name':'data','wave':'=..','data':['X']}]}))
            o.write_text(json.dumps({'signal':[{'name':'valid','wave':'000'},
                                               {'name':'data','wave':'=..','data':['0x0']}]}))
            r = compare(e,o)
            self.assertEqual(len(r['mismatches']), 1)
            self.assertEqual(len(r['inconclusive_cells']), 3)
            self.assertTrue(has_unknown(('=', '10x1')))


class ValidationTests(unittest.TestCase):
    def test_demo_report_strict_pass(self):
        root = BASE / 'examples' / 'tiny_ip'
        docs = BASE / 'examples' / 'demo_output'
        report = validate(root, docs, docs / 'inventory.json', True)
        self.assertEqual(report['status'], 'PASS', report['errors'])

    def test_hash_mismatch_detected(self):
        root = BASE / 'examples' / 'tiny_ip'
        docs = BASE / 'examples' / 'demo_output'
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            (tmp / 'rv_stage.v').write_text('module rv_stage; endmodule')
            report = validate(tmp, docs, docs / 'inventory.json', True)
            self.assertEqual(report['status'], 'FAIL')
            self.assertTrue(any('RTL changed' in s for s in report['errors']))

    def test_draft_fails_strict(self):
        root = BASE / 'examples' / 'tiny_ip'
        inv = get_inventory(root, root / 'rtl.f')
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            mf = tmp / 'inventory.json'
            mf.write_text(json.dumps(inv))
            make_draft(root, mf, tmp / 'out', 'rv_stage')
            report = validate(root, tmp / 'out', mf, True)
            self.assertEqual(report['status'], 'FAIL')
            self.assertTrue(any('uncompleted template' in s for s in report['errors']))

if __name__ == '__main__':
    unittest.main()

# Vendor EDA adapter tests use planning/mocked artifacts ONLY: VCS and Verdi are not run.
from vcs_verdi import load_config, make_commands, action, save_ucli_dump
from unittest.mock import patch
import hashlib


class VendorAdapterTests(unittest.TestCase):
    def sample_config(self, root: Path):
        (root / 'rtl.f').write_text('dut.sv\n')
        (root / 'dut.sv').write_text('module dut; endmodule\n')
        c = root / 'cfg.json'
        c.write_text(json.dumps({'project_root': '.', 'filelist': 'rtl.f', 'tb_top': 'tb_dut',
                                  'output_dir': 'docs/rtl_spec/eda', 'fsdb_dump_mode': 'ucli',
                                  'compile_extra': ['tb_dut.sv'], 'run_extra': [],
                                  'convert_extra': []}))
        return c

    def test_config_anchor_is_config_parent_not_current_cwd(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            cfg = load_config(self.sample_config(p))
            self.assertEqual(cfg['root'], p.resolve())
            self.assertEqual(cfg['filelist_path'], (p/'rtl.f').resolve())
            self.assertEqual(cfg['simv_path'], p/'docs/rtl_spec/eda/build/simv')

    def test_vendor_command_pipeline_and_dry_run(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = load_config(self.sample_config(Path(d)))
            commands = make_commands(cfg)
            vcs = commands['compile']
            self.assertIn('-kdb', vcs)
            self.assertIn('-debug_access+all', vcs)
            self.assertEqual(vcs[vcs.index('-top') + 1], 'tb_dut')
            self.assertEqual(vcs[vcs.index('-f') + 1], str(cfg['filelist_path']))
            self.assertTrue(any(x.startswith('-Mdir=') for x in vcs))
            self.assertIn('fsdb2vcd', commands['convert'][0])
            self.assertIn('-ssf', commands['open'])
            self.assertEqual(action(cfg, 'compile')['status'], 'DRY_RUN')
            self.assertFalse(cfg['out'].exists())

    def test_ucli_fsdb_dump_has_no_rtl_source_changes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            cfg = load_config(self.sample_config(p))
            before = (p/'dut.sv').read_bytes()
            cfg['out'].mkdir(parents=True)
            tcl = save_ucli_dump(cfg).read_text()
            self.assertIn('$fsdbDumpfile', tcl)
            self.assertIn('$fsdbDumpvars(0, tb_dut)', tcl)
            self.assertIn('run\nquit', tcl)
            self.assertEqual((p/'dut.sv').read_bytes(), before)

    def test_reject_output_path_escaping_project(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            path = self.sample_config(p)
            data = json.loads(path.read_text()); data['output_dir'] = '../not_allowed'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'inside project_root'):
                load_config(path)

    def test_reject_shell_command_string_in_argv(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            path = self.sample_config(p)
            data = json.loads(path.read_text()); data['compile_extra'] = '&& rm -rf rtl'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'argv strings'):
                load_config(path)

    def test_release_gate_rejects_demo_without_real_vendor_evidence(self):
        root = BASE / 'examples' / 'tiny_ip'
        docs = BASE / 'examples' / 'demo_output'
        report = validate(root, docs, docs / 'inventory.json', True, release=True)
        self.assertEqual(report['mode'], 'release')
        self.assertEqual(report['status'], 'FAIL')
        self.assertTrue(any('release gate: missing Synopsys' in e for e in report['errors']))

    def test_verdi_manifest_hash_requirement_rejects_mismatch(self):
        import subprocess
        root = BASE / 'examples' / 'tiny_ip'
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            bad_conv = {'stage':'convert','executed':True,'status':'PROCESS_EXIT_0_UNQUALIFIED',
                        'vcd_sha256':'0'*64,'fsdb_sha256':'f'*64}
            fake_run = {'stage':'run','executed':True,'status':'PROCESS_EXIT_0_UNQUALIFIED',
                        'fsdb_exists':True,'fsdb_sha256':'f'*64}
            conv = p/'convert_manifest.json'; run = p/'run_manifest.json'
            conv.write_text(json.dumps(bad_conv)); run.write_text(json.dumps(fake_run))
            proc = subprocess.run([sys.executable, str(BASE/'scripts/vcd_to_wavedrom.py'),
                                   '--vcd', str(root/'fixture.vcd'), '--clock','tb_rv_stage.clk',
                                   '--signals','tb_rv_stage.out_valid',
                                   '--verdi-manifest',str(conv), '--vcs-run-manifest',str(run),
                                   '--out',str(p/'out.json5')], capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('hash differs', proc.stderr)

    def test_missing_one_of_vendor_manifests_is_rejected(self):
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); mf = p/'convert.json'; mf.write_text('{}')
            proc = subprocess.run([sys.executable, str(BASE/'scripts/vcd_to_wavedrom.py'),
                                   '--vcd',str(BASE/'examples/tiny_ip/fixture.vcd'),
                                   '--clock','tb_rv_stage.clk', '--signals','tb_rv_stage.out_valid',
                                   '--verdi-manifest',str(mf), '--out',str(p/'out.json5')],
                                   capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('BOTH', proc.stderr)
