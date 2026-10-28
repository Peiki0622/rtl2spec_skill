# Changelog

## 0.3.0 — 2026-10-28

- Added a built-in Chinese engineering-writing guide: explain module behavior, handshake conditions and edge timing in straightforward prose.
- Removed repeated defensive disclaimers from the generated Spec templates, timing figure labels and demonstration documents; kept actual EDA provenance and review state in the designated evidence tables/metadata.
- Added bilingual chapter titles and compatible strict validation (the stable numbered English keys remain).
- Added `scripts/style_lint.py` with 6 regression tests for AI-sounding filler and misplaced repeated caveats.
- Rewrote the tiny ready/valid example as a concise Chinese IP/module Spec and regenerated waveform SVGs.
- Preserved Synopsys VCS + Verdi as the EDA backend and source-grounded timing/evidence requirements.


## 0.2.0 — 2026-10-28

- Promoted document templates to numbered, controlled **Formal IP Specification** (13 IP chapters + appendices, 9 module chapters, revision history, interface, timing, map, integration, verification and traceability).
- Required chapter-scoped figure/table captions, document identity/revision/status metadata, and strengthened strict validation; added optional release evidence gate that does not auto-approve.
- Replaced default Icarus/Verilator flow with mandatory primary **Synopsys VCS + Verdi** vendor workflow. Added `scripts/vcs_verdi.py` planner and explicit-execute wrappers for VCS compile/run, Verdi `fsdb2vcd` and Verdi GUI; records command, status and source/FSDB/VCD hashes without falsely calling process exit a functional PASS.
- Added VCD converter manifest-chain validation before a figure may be labelled `VCS/VERDI OBSERVED`.
- Added documented on-premises licensed EDA prerequisites, UCLI FSDB route, example config, local-only data policy, public demo and EDA mock tests; preserved offline source-only documentation.
- Updated ready/valid demo documentation to formal numbering; sample VCD remains a handwritten parser fixture, not real VCS output.

## 0.1.0 — 2026-10-28

- Initial Codex `SKILL.md`, lexical source index, templates, WaveDrom subset renderer, VCD parser, waveform comparison and validation.
- Python standard-library sample tests; no proprietary EDA run claimed.
