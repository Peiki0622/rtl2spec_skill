# Timing diagrams, edge semantics and verification

## Required scenario selection

Start with reset assertion/release, first transaction, normal completion, consecutive transactions, and any **actual** stall/backpressure/flush/error behavior. Do not invent missing protocol features. Multi-clock examples need domain-specific edge definitions; do not promise deterministic asynchronous crossing latency without evidence.

## Edge timing rules

- For `always_ff` or `always @(posedge clk)` and nonblocking `<=`, state transitions depend on old state at the edge; new register values appear in the nonblocking-update region. Label **pre-edge handshake acceptance** separately from **post-edge registered outputs**.
- This Skill's converter samples VCD values **after all recorded changes at each rising-edge timestamp** (last value at timestamp). It does **not** reconstruct all simulation scheduling regions or setup/hold behavior. A `posedge` clock row is a cycle marker rather than a full waveform.
- Asynchronous reset may take effect *between* clock edges; do not use only posedge snapshots to claim reset assertion latency. Preserve X/Z and missing signals; do not coerce to zero.

## Diagram format and provenance

Output strict JSON (subset of WaveDrom JSON5) with one `signal` row per selected trace; wave symbol subset `0`, `1`, `x`, `z`, `=`, `.`, `p`, and bus `data` labels. Render offline with `scripts/render_wavedrom.py`. For advanced WaveDrom effects use a separately licensed/installed official renderer rather than claiming this subset implements all JSON5 syntax.

Every figure requires `**Figure 9-n — ...**` (IP) or `**Figure 7-n — ...**` (module), an SVG, scenario purpose, source citation and cycle table. **Show short labels to readers**; preserve the machine-readable evidence status in the verification chapter and metadata:

- **RTL 推导** (`ILLUSTRATIVE`): timing derived from the current RTL.
- **VCS/Verdi 波形** (`VCS/VERDI-OBSERVED`): actual FSDB recorded by VCS, exported with Verdi and checked against conversion manifests.
- **VCD 观测** (`VCD-OBSERVED`): a VCD input without complete VCS/Verdi provenance.
- **测试夹具** (`SYNTHETIC TEST FIXTURE`): synthetic VCD used for parser tests.

Skip lengthy reassurance/denial in the body. Capture command, FSDB/VCD hashes, sampling convention and test result in chapter 12.

**Example of a simple illustrative diagram:**

```json
{
  "signal": [
    {"name": "clk (posedge)", "wave": "pppppp"},
    {"name": "rst_n", "wave": "01...."},
    {"name": "req", "wave": "0.10.."},
    {"name": "state", "wave": "=.=..=", "data": ["IDLE", "BUSY", "IDLE"]}
  ],
  "head": {"text": "示例时序 · RTL 推导"}
}
```

## Synopsys verification flow

Read [VCS + Verdi workflow](eda-vcs-verdi.md) and invoke `vcs_verdi.py`. Normal tool outputs: `eda/vcs_compile.log`, `eda/vcs_run.log`, `eda/waves.fsdb`, `eda/waves.vcd`, `eda/{compile,run,convert}_manifest.json`. Real VCS simulation requires a testbench; if none exists, make one in generated/output tree only with authorization, or mark `NOT RUN`. Never edit DUT RTL for a waveform.

With FSDB converted to VCD, use `vcd_to_wavedrom.py` and **both** `--verdi-manifest` and `--vcs-run-manifest` when claiming the VCS/Verdi observation chain. Use `compare_waveforms.py` only after explicit timestamp, edge and sample alignment; matches are a diagnostic, not a functional proof.

## Final document gate

Run `style_lint.py --strict` for prose and `validate.py --strict` for formatting, including section numbers, document metadata, revision history, figure captions, file:line citations, SVG links and RTL snapshot hash. `--release` additionally checks evidence manifests and human-marked document Status; it **does not** produce an approval or sign-off. Humans must review function, coverage, legal/confidentiality classification, quality of VCS testbench checkers and Verdi waveform interpretation.
