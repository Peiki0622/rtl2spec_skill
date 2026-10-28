# Tool policy and upstream attributions (v0.3)

## Primary EDA — mandatory

**Synopsys VCS** is the default simulator/elaborator and **Synopsys Verdi** is the default waveform/debug platform. Use `scripts/vcs_verdi.py` and follow [VCS + Verdi workflow](eda-vcs-verdi.md). Files are never passed to unapproved remote services. Both tools require the user's licensed, configured installation. The included Python converter and SVG renderer are **post-processing utilities**, not substitute EDA engines.

| Capability | Tool | Guarantee / qualification |
| --- | --- | --- |
| Build, elaborate, simulate SystemVerilog | **VCS** (`vcs`, `simv`) | Must use actual source filelist / TB / macros and record logs; exit=0 is not correctness. |
| Waveform recording and debugging | **Verdi FSDB** (`$fsdbDumpvars`, Verdi nWave) | FSDB is an observation database; can contain X/unknown and incomplete scopes. |
| FSDB export for document figures | **Verdi `fsdb2vcd`** | Vendor tool, requires license/installation; retain FSDB+VCD SHA256 chain. |
| Documentation diagrams | **Included WaveDrom subset renderer** | Fully offline; illustrations are not simulated, VCD-derived diagrams only represent sampled values. |
| Inventory/template/validation | **Included Python scripts** | Deterministic text processing, not full SystemVerilog parsing or verification. |

**Do not make Icarus, Verilator, Yosys or waveform MCP backends part of the default verification path**. If a user separately requests one as an additional cross-check, report it as an optional independent tool, never a replacement for the required VCS/Verdi provenance.

## Inspiration, not vendored dependencies

This Skill implements its own scripts and Markdown instructions. No upstream files or libraries are bundled. Design patterns informed by these projects:

1. [phamcuong21478/rtl-skills](https://github.com/phamcuong21478/rtl-skills) (Apache-2.0): source-grounded `vexplain` and `vdoc`.
2. [Eriemon/verilog-generator](https://github.com/Eriemon/verilog-generator) (Apache-2.0): WaveDrom/spec contract and provenance distinction; its primary generator is not an RTL→Spec analyzer.
3. [codejunkie99/Gateflow-Plugin](https://github.com/codejunkie99/Gateflow-Plugin): hierarchy and FSM investigation; follow upstream licensing if independently used.
4. [Toroid-io/vcd2wavedrom](https://github.com/Toroid-io/vcd2wavedrom) (MIT): conceptual VCD→WaveDrom flow; our parser is independently authored.
5. [WaveDrom](https://github.com/wavedrom/wavedrom): diagram syntax; our renderer supports only a documented subset.
6. [Synopsys VCS](https://www.synopsys.com/verification/simulation/vcs.html) and [Synopsys Verdi](https://www.synopsys.com/blogs/chip-design/verdi-waveform-utilities.html): commercial user-installed proprietary tools — **not bundled or relicensed**.

## Natural technical prose

The Skill's Chinese writing guide draws general principles from [blader/humanizer](https://github.com/blader/humanizer) and [ai-zixun/humanizer-zh](https://github.com/ai-zixun/humanizer-zh), combined with domain rules specific to RTL: preserve signal names, clock edges, register semantics and source citations. These upstream Skills are optional and not vendored into this repository; `style_lint.py` and our templates are original implementations.
