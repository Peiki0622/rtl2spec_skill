# Formal IP Specification Skill — implementation design v0.2 (2026-10-28)

## Goal

A Codex skill that reverse-documents **actual** existing Verilog/SystemVerilog into reviewable IP specs with source citations and cycle-accurate timing figures, built around the user's specified commercial EDA stack **Synopsys VCS + Verdi**. No source DUT changes; user output is isolated under `docs/rtl_spec/` by default. No commercial EDA binaries are included.

## Document control layer

- Cover metadata with Document ID, revision, status, author/reviewer/approver (unassigned until real review), configuration ID and source revision.
- IP: mandatory 13 numbered chapters plus module/glossary appendices; individual module: mandatory 9 numbered chapters. Strong interface, clock/reset, state, timing, register map, integration, evidence and traceability structure.
- Number tables/figures by chapter; every key waveform has a cycle table, source location and origin label.
- `validate.py --strict`: structural checks, paths, sections, figure caption, snapshot integrity. `--release`: extra actual VCS + Verdi manifest gate; no automatic approval.

## EDA/data path

1. `inventory.py` generates lexical candidate module/port index and hashes; Codex confirms real hierarchy/parameters via VCS compile and manual RTL reading.
2. `scaffold.py` generates standard Spec drafts. Codex fills with implementation-grounded descriptions and source locations.
3. `vcs_verdi.py` dry-run / optional real `--execute`: VCS `-kdb -debug_access+all` builds simulation binary; VCS `simv` runs existing TB and captures FSDB (TB dump or generated UCLI commands); Verdi inspects FSDB and `fsdb2vcd` converts waveform selection to VCD. Records stage commands, status and FSDB/VCD hashes.
4. `vcd_to_wavedrom.py` groups VCD changes at each rising-edge timestamp (post-timestamp), emits diagrams and metadata; checks both VCS and Verdi manifests before claiming vendor-observed provenance.
5. `render_wavedrom.py` draws independent simple SVG illustrations; `compare_waveforms.py` compares aligned samples; `validate.py` lints docs and source snapshot. Human and testbench assertions are needed for functional sign-off.

## Limits

- Requires licensed VCS/Verdi for actual vendor EDA runs; authorship environment only dry-run verified.
- Vendor compile flags, DPI, PLI, encrypted models, design filelists, licenses and version-specific FSDB methods vary; project configuration must be checked.
- No automatic inference of design intent, no full SV elaborator built into Python index, no guarantee of testbench coverage, no Verdi GUI auto-screenshot/export, no fake simulation PASS.
- Spec can be delivered as DRAFT without vendor EDA if gaps explicitly marked. `RELEASED` requires external review and approval.

## Upstream inspiration

`rtl-skills/vexplain` + `vdoc` for source-first document contract, `verilog-generator` for WaveDrom handoff, Gateflow for SV analysis workflows; independent Python implementation (no vendored third-party source). Refer to `references/tool-adapters.md` and `references/eda-vcs-verdi.md`.
