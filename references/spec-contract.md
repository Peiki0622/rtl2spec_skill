# Formal IP Specification contract (v0.3)

The output is a **controlled, implementation-grounded IP specification**. Write the technical content for engineers first; collect review and verification status in their designated chapters. See [writing-style-zh.md](writing-style-zh.md) for the default prose style.

## 1. Output profiles and template stability

- IP deliverable: `ip_spec.md`; per-module deliverable: `modules/<module>.md`. Use `assets/templates/ip_spec.md` and `module_spec.md` respectively.
- Follow numbered level-2 headings and the supplied order. Keep English chapter keys for stable validation; append a concise Chinese subtitle in full-width parentheses when writing Chinese (e.g., `## 8. Functional Operation（工作原理）`). Required IP chapters 1–13 and Appendices A–B; module chapters 1–9. Include document metadata, revision history and review state. Unknown values stay unknown instead of being invented.
- Use `**Table X-Y — Title**` immediately before every important table and `**Figure X-Y — Title**` next to architecture, FSM and timing diagrams. Number consecutively within each chapter; use relative document hyperlinks and nonbroken `.svg` images. Each important waveform needs its figure caption and a clear cycle-by-cycle explanation.
- `N/A` requires a brief reason and implementation evidence (e.g., no memory-mapped interface). Record concrete unresolved topics in Open Issues.
- Run `style_lint.py --strict` for high-confidence prose problems and `validate.py --strict` for format, source citations and snapshot integrity. An authorized reviewer decides release state.

## 2. Source-grounded design analysis

Record concrete **compiled configuration**, not merely lexical candidates: DUT top, testbench top, filelist recursion, package order, include paths, `define`s, parameter overrides, encrypted blocks, libraries and source hash/commit. If VCS compilation/elaboration is unavailable, keep `TOOL-ELABORATED` status *unclaimed*.

Analyze each module: declared ports/widths and timing, reset async vs sync, polarity and release, exact register reset/hold/update conditions, FSM transitions, datapath equations, end-to-end latency / pipeline initiation interval, ready/valid/ack handshakes, exceptional states, interrupt/error semantics, CDC and configuration-dependent behavior. Cite each nontrivial claim using `rtl/path/file.sv:LINE` from the current source snapshot; cite ranges as `file.sv:14-28`.

### IP-level chapters (fixed)

1. **Document Control** — document metadata and revision history; approval tracking; confidentiality.
2. **Scope and References** — supported build and analysis boundaries, references.
3. **IP Overview and Features** — actual supported features / exclusions.
4. **Configuration and Deliverables** — analyzed sources, macros, parameters, EDA stack, external dependencies.
5. **Architecture and Hierarchy** — real hierarchy, block diagram / Mermaid, data/control flows.
6. **External Interface Specification** — exact port table and timing/protocol contracts.
7. **Clocks, Resets and CDC** — clock domain, reset assertion/release, crossing assumptions.
8. **Functional Operation** — state progression and actual algorithms.
9. **Timing and Waveform Scenarios** — per-scenario figure + pre/post edge cycle table + provenance.
10. **Register and Memory Map** — addressable map *if present*, otherwise evidence-based N/A; avoid confusing internal registers with bus registers.
11. **Exceptions, Constraints and Integration** — illegal cases and integration prerequisites, only when implemented.
12. **Verification and Evidence** — VCS/Verdi run commands, logs, testbench pass criteria, FSDB provenance.
13. **Traceability and Open Issues** — spec-to-RTL claims index and unverified assumptions.
**Appendix A. Module Index**, **Appendix B. Glossary**.

### Module-level chapters (fixed)

1. **Module Function**
2. **Parameters and Build Configuration**
3. **Port and Protocol Definition**
4. **Clock and Reset**
5. **State, Datapath and Register Behavior**
6. **Functional and Cycle-Level Operation**
7. **Timing and Waveform Scenarios**
8. **Verification Evidence**
9. **RTL Traceability and Open Issues**

## 3. Scenario selection and waveform requirements

Identify **actual** reset, normal transaction, start/done, consecutive operations, backpressure, stall, flush, error, timeout, invalid input, or CDC scenarios **only if present in this RTL**. Each important supported operation gets: (a) scenario ID and objective, (b) initial conditions and inputs, (c) referenced RTL lines, (d) cycle sample semantics, (e) WaveDrom SVG plus numbered figure, (f) transaction table, (g) evidence label and VCS/Verdi artifact/log if verified. Ensure every state/latency/handshake statement uses pre-edge vs post-NBA definitions consistently.

Use short, honest figure labels:
- **RTL 推导**: example waveform derived from source code; keep `ILLUSTRATIVE` as the internal evidence class.
- **VCS/Verdi 波形**: FSDB recorded by VCS and exported via Verdi `fsdb2vcd`; save manifests and source hashes in the evidence table/sidecar.
- **测试夹具**: hand-authored VCD for parser tests, not a simulator trace.
Do not repeat evidence disclaimers in each narrative paragraph.

## 4. Evidence and release status

Use explicit evidence levels: `RTL-DERIVED` (manual/agent code reasoning), `TOOL-ELABORATED` (recorded VCS compile/elaboration), `ILLUSTRATIVE`, `VCS/VERDI OBSERVED`, `SIMULATION-PASS` (recorded self-checking tests with checked criteria), `FORMALLY-PROVEN` (real proof and assumptions). Only use `SIMULATION-PASS` when self-checking test conditions are recorded and checked.

`DRAFT` and `UNDER REVIEW` are valid document states. `RELEASED` requires actual reviewer approval and reconciled configuration/evidence. Keep proprietary RTL and waves within the project environment.

## 5. Readability acceptance

In chapters 3, 6, 8 and 9, a reader should understand the module purpose, input acceptance rule, clock-edge behavior and output validity without needing to read Verilog. Put the important engineering condition close to the relevant behavior. Avoid repeating VCS/Verdi availability statements outside the verification chapter; write the status once in the evidence table. Retain exact file-line citations, tables, waveforms and figures.
