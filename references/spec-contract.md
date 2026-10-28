# Formal IP Specification contract (v0.2)

The output is a **controlled, implementation-grounded technical document** suitable for design review and external IP hand-off after review/approval. A generated Markdown document is **not automatically an approved specification**, a sign-off artifact or a substitute for verification.

## 1. Output profiles and template stability

- IP deliverable: `ip_spec.md`; per-module deliverable: `modules/<module>.md`. Use `assets/templates/ip_spec.md` and `module_spec.md` respectively.
- Follow exact **numbered English level-2 headings** and the supplied order, even when the explanatory prose is Chinese. Required IP chapters 1–13 and Appendices A–B; module chapters 1–9. Include a revision-history table, document metadata, and explicit review/approval status. Do not invent authors, revisions, tool versions, clock frequencies, or approved release claims.
- Use `**Table X-Y — Title**` immediately before every important table and `**Figure X-Y — Title**` next to architecture, FSM and timing diagrams. Number consecutively within each chapter; use relative document hyperlinks and nonbroken `.svg` images. A waveform requires a figure caption and a cycle-by-cycle explanation; an illustration alone is not a timing contract.
- `N/A` requires a reason and implementation evidence (e.g., no memory-mapped interface); avoid hallucinating unused register-map chapters into invented registers. Unresolved topics remain in Open Issues and document status stays DRAFT or UNDER REVIEW.
- The `validate.py --strict` validator checks format, citations and source snapshot integrity; it does **not** certify truthfulness, design correctness or release approval. Use `--release` for extra evidence/document-state gates; it never automatically approves a document.

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

Use two labels, never conflate:
- `ILLUSTRATIVE — NOT SIMULATED`: Agent derives timing from RTL; Markdown and WaveDrom JSON/SVG.
- `VCS/VERDI OBSERVED — NOT AUTOMATICALLY VERIFIED`: VCS produced FSDB, Verdi inspected or `fsdb2vcd` exported it; converter read the observed VCD. VCS run manifest, FSDB hash, exported VCD hash, sampling interval and selected signals must be linked. A hand-authored fixture is `SYNTHETIC TEST FIXTURE`, never a simulation observation.

## 4. Evidence and release status

Use explicit evidence levels: `RTL-DERIVED` (manual/agent code reasoning), `TOOL-ELABORATED` (recorded VCS compile/elaboration), `ILLUSTRATIVE`, `VCS/VERDI OBSERVED`, `SIMULATION-PASS` (recorded self-checking tests with checked criteria), `FORMALLY-PROVEN` (real proof and assumptions). Simulator exit=0, FSDB existence, Verdi screenshot, and diagram matching alone **do not** prove functional correctness.

`DRAFT` and `UNDER REVIEW` are possible without proprietary tools if gaps are disclosed. `RELEASED` must be explicitly approved by authorized humans, with RTL revision, build, evidence, documentation and reproducibility reconciled; the skill shall never set RELEASED by itself. For proprietary or undisclosed content, do not upload RTL/waveforms to external services.
