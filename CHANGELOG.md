# Changelog

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
