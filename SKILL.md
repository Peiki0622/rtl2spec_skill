---
name: rtl-to-spec
description: Reverse-engineer existing Verilog/SystemVerilog RTL into implementation-grounded IP/module specifications with interfaces, FSM/datapath, cycle timing, evidence-linked WaveDrom/SVG diagrams and optional VCD simulation traces. Use for RTL-to-spec, design documentation, timing examples, or code-to-hardware-spec work; not for writing new RTL.
---

# RTL → Implementation Specification

**Invocation:** Set `SKILL_DIR` to the directory containing this `SKILL.md`; substitute it for `<skill>` in commands below.

**Goal:** Given existing `.v`/`.sv` files, produce a detailed **as-implemented** IP specification. Read-only RTL. By default write under `docs/rtl_spec/` (or a user-specified output directory). Never treat requirements, comments, inferred intent, or schematic conventions as overriding implemented RTL.

## Use this workflow

1. **Establish design boundary and provenance.** Locate repository root, filelists (`.f`), top module, active `define`s, parameter overrides, include dirs, generated files and blackboxes. Run `python3 <skill>/scripts/doctor.py` and `python3 <skill>/scripts/inventory.py --root . --out docs/rtl_spec/inventory.json [--filelist FILE]`. This inventory is a **lexical discovery aid, not elaboration**. Confirm top and instance resolution by reading RTL and, if available, using Verilator/pyslang/Yosys. Never silently infer the top when there is ambiguity.
2. **Make a safe draft.** `python3 <skill>/scripts/scaffold.py --root . --inventory docs/rtl_spec/inventory.json --out docs/rtl_spec --top TOP`. This creates templates but does not overwrite existing files unless explicitly asked. Templates containing `TODO` are *not* completed specs.
3. **Read and analyze real RTL.** Inspect **all relevant** source/modules in the resolved hierarchy. Establish per-module function, parameters, typed ports, clocks/resets (sync/async, polarity, priority), reset values, register enable/update equations, FSM transitions, datapath and arithmetic semantics, handshakes, backpressure, latency and throughput, corner cases, and observable behavior. Derive cycle examples **after** resolving nonblocking-assignment semantics. Check conditional compilation and parameter configurations. Add `file.v:line` or `file.sv:line` evidence next to important claims; classify unknowns, blackboxes, implicit assumptions explicitly. Follow [spec contract](references/spec-contract.md).
4. **Generate real documentation.** Fill `ip_spec.md` and `modules/*.md`; include source-grounded hierarchy diagram (Mermaid), interface tables with explicit width expressions, register/state tables, and cycle-by-cycle transaction tables. Reconcile summaries against module docs and RTL. Explain unsupported/undetermined claims instead of guessing.
5. **Produce waveforms in two clearly separated classes** (see [timing protocol](references/timing-and-validation.md)):
   - **Illustrative / RTL-derived**: Write valid WaveDrom JSON in `waveforms/<scenario>.json5` (strict JSON syntax also valid as JSON5). Include a table of cycle values and RTL citations. Render with `python3 <skill>/scripts/render_wavedrom.py --input ...json5 --output ...svg`. Mark `ILLUSTRATIVE — NOT SIMULATED`.
   - **VCD-observed** (only if a VCD really exists): `python3 <skill>/scripts/vcd_to_wavedrom.py --vcd sim.vcd --clock tb.clk --signals tb.rst_n tb.in_valid tb.in_ready tb.out_valid tb.out_ready tb.out_data --cycles 12 --out docs/rtl_spec/waveforms/transfer.json5 --svg docs/rtl_spec/waveforms/transfer.svg`. The script samples after all value changes at each selected rising-edge timestamp; emits a metadata sidecar. Label `VCD OBSERVED — FUNCTIONAL CORRECTNESS NOT IMPLIED`. Attach simulator command/log only if actually run and passed.
6. **Compare aligned examples when both types exist.** After confirming both waveforms use the *same* edge timestamps, sampling convention, and chosen signals, run `python3 <skill>/scripts/compare_waveforms.py --expected docs/rtl_spec/waveforms/example.json5 --observed docs/rtl_spec/waveforms/observed.json5 --report docs/rtl_spec/waveform_compare_report.json`. A match is only diagram-level consistency, not a correctness proof.
7. **Validate and hand off.** `python3 <skill>/scripts/validate.py --root . --docs docs/rtl_spec --inventory docs/rtl_spec/inventory.json --strict`. Fix missing evidence, missing diagrams, `TODO`s and RTL hash mismatches. List exact checks run, failed, skipped and unverified. Never claim static analysis, waveform capture, or a testbench establishes functional correctness automatically.

**Non-negotiable:** Do not modify any `.v`, `.sv`, `.vh`, `.svh` sources, change build scripts, install dependencies, or run remote programs without ordinary user/host authorization. Do not invent scenarios as observed evidence. Do not overwrite existing documents without permission. If no simulator is available, still deliver complete RTL-grounded docs with clearly labeled illustrative timing, and record the simulation gap.

## Read only the relevant references

- [Specification contract](references/spec-contract.md): mandatory sections, evidence labels, hierarchy, and precise claims.
- [Waveforms and validation](references/timing-and-validation.md): clock-edge semantics, WaveDrom subset, waveform provenance, and simulation integration.
- [Tool adapters and upstream attributions](references/tool-adapters.md): optional Verilator/Icarus/pyslang/wave-mcp/wavepeek, dependencies and limitations.

## Output contract

`docs/rtl_spec/inventory.json`, `ip_spec.md`, `modules/<module>.md`, `waveforms/<scenario>.json5`, `.svg`, optional `.meta.json`, and `validation_report.json`, optional `waveform_compare_report.json`. Put all deliverables inside the requested output tree. Cite source file + line for concrete behavior, and use an explicit `Unknown / Unverified` section. Default explanation language follows the user's language; keep RTL symbol names exact.
