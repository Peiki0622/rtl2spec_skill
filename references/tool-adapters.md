# Optional EDA adapters and source attributions

Bundled scripts use Python 3.10+ standard library only. The Codex host does the semantic RTL reasoning. Use external tools when present; do not silently install or modify a user's environment.

| Capability | Suggested tool | How to use |
| --- | --- | --- |
| Full/SystemVerilog elaboration | Verilator `--lint-only` and/or pyslang | Supply project's actual `-f` filelist, `+incdir+`, `-D`, parameters and `--top-module`; resolve diagnostics, then cite compiled configuration. |
| Quick Verilog RTL simulation | Icarus (`iverilog`, `vvp`) | Reuse existing testbenches first; VCD output requires `$dumpvars`. |
| Alternative RTL AST/synthesis | Yosys (`read_verilog`, `hierarchy`) | Only claim semantics for supported Verilog subset and active synthesis parameters. |
| Manual/document waveforms | WaveDrom and included SVG renderer | `.json5` strict-JSON subset (not a general JSON5 parser). |
| Large waveform debug | `wavepeek` or Tencent `wave-mcp` | Optional tools; they do not execute the simulator and cannot alone prove correctness. |
| Automatic VCD → WaveDrom | Included converter or Toroid `vcd2wavedrom` | Require explicit clock/selected signals and publish sampling convention. |

## Inspiration, not vendored dependencies

This skill implements its own scripts and Markdown instructions. No upstream files or library code are bundled/copied. Links to techniques which informed the workflow:

1. [phamcuong21478/rtl-skills](https://github.com/phamcuong21478/rtl-skills) (Apache-2.0): `vexplain` source-grounded module documentation and `vdoc` module-to-IP aggregation. Avoid assuming its Verilog-2005-only, sync-reset, or directory conventions apply to arbitrary designs.
2. [Eriemon/verilog-generator](https://github.com/Eriemon/verilog-generator) (Apache-2.0): spec + WaveDrom handoff and explicit verification provenance. Original primary generation flow is not equivalent to RTL→Spec.
3. [codejunkie99/Gateflow-Plugin](https://github.com/codejunkie99/Gateflow-Plugin): SV understanding, hierarchy and FSM investigation; follow its own license and installation instructions if actually used.
4. [Toroid-io/vcd2wavedrom](https://github.com/Toroid-io/vcd2wavedrom) (MIT): VCD→WaveDrom workflow; included parser is independently authored and intentionally narrower.
5. [Octopustank/wavepeek-master-skill](https://github.com/Octopustank/wavepeek-master-skill) (Apache-2.0): external waveform inspection workflow.
6. [Tencent/wave-mcp](https://github.com/Tencent/wave-mcp) (Apache-2.0): optional richer MCP for FST and SV structure/driver analysis.
7. [WaveDrom](https://github.com/wavedrom/wavedrom): timing-diagram data conventions; renderer bundled here is an independent **subset renderer**, not the WaveDrom implementation.
8. [OpenAI skills documentation](https://learn.chatgpt.com/docs/build-skills): Codex skill packaging and activation.

## Dependency separation

- Always available: lexical inventory, doc templates, offline simple SVG rendering, VCD extraction, spec validation.
- Only if locally installed: full SV elaboration, lint/synthesis, real simulation, FST analysis, waveform MCP.
- Never imply physically measured side-channel or silicon/FPGA verification from a simulation.
