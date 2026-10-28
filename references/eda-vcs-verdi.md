# Synopsys VCS + Verdi: mandatory primary EDA workflow

**Scope:** Proprietary software requiring a valid local installation/license. No vendor binary/library is packaged in this Skill. `scripts/vcs_verdi.py` wraps **existing licensed tools**; it never installs them. Its default is **dry-run**; `--execute` is needed for each stage. Do not run new simulation code or change repository sources without normal user authorization.

## 1. Tools, compilation and provenance

VCS is the primary SystemVerilog compilation, elaboration and RTL simulation engine. Verdi is the primary FSDB waveform viewer/analysis tool; its `fsdb2vcd` utility is used *only as an export bridge* to the Skill's VCD-to-WaveDrom converter. Example VCS compile flags: `-full64 -sverilog -kdb -debug_access+all -f rtl.f -top tb_top -o ... -Mdir=... -l ...`. Options must be reconciled with your exact VCS/Verdi version, project compile flow, encrypted models, licenses, package order, `+incdir+`, defines and library setup. `-kdb` supports Verdi debug databases; debug visibility/options can affect compile/memory/runtime.

Tool verification:

```bash
python3 <skill>/scripts/doctor.py
python3 <skill>/scripts/vcs_verdi.py doctor
```

Copy `assets/templates/vcs_verdi_config.json` into the RTL project and customize (paths resolve **relative to the JSON file directory**):

```json
{
  "project_root": ".", "filelist": "rtl.f", "dut_top": "ip_top",
  "tb_top": "tb_ip_top", "output_dir": "docs/rtl_spec/eda",
  "fsdb": "docs/rtl_spec/eda/waves.fsdb",
  "vcd": "docs/rtl_spec/eda/waves.vcd",
  "fsdb_dump_mode": "ucli", "compile_extra": [], "run_extra": [],
  "convert_extra": [], "timeout_seconds": 1800
}
```

`-f` filelist must contain the DUT and its testbench, or supply the testbench in `compile_extra` (one argv item per token). Filelist paths/`+incdir+` are resolved by VCS relative to the design working directory. Some EDA projects use custom scripts, VHDL/DPI or special environment modules; in those cases use the **project's own validated VCS compile/run commands**, and record them manually rather than claiming the adapter covers every build. The `dut_top` field is documentation metadata; **`tb_top` is the simulation -top**. Use VCS elaboration and compile logs to confirm active hierarchy; the lexical inventory alone does not.

Dry-run plan (always possible without EDA tools):

```bash
python3 <skill>/scripts/vcs_verdi.py --config vcs_verdi.json plan
python3 <skill>/scripts/vcs_verdi.py --config vcs_verdi.json compile
```

Real execution (only where licensed/installed and authorized):

```bash
python3 <skill>/scripts/vcs_verdi.py --config vcs_verdi.json --execute compile
python3 <skill>/scripts/vcs_verdi.py --config vcs_verdi.json --execute run
python3 <skill>/scripts/vcs_verdi.py --config vcs_verdi.json --execute convert
```

Writes `docs/rtl_spec/eda/{compile,run,convert}_manifest.json` with argv, UTC date, tool, executed flag, process status, filelist hash and optional `simv`, `fsdb`, `vcd` hashes. Logs are under the same output tree. This is **command execution evidence**, not automatic test correctness evidence. To call a testcase `SIMULATION-PASS`, examine self-checking assertions / scoreboard result and explicitly link the test and its failure criteria; a clean VCS process exit is not sufficient.

## 2. Obtaining FSDB without modifying DUT RTL

Default recommended VCS/Verdi waveform is **FSDB**. Choose exactly one:

- `fsdb_dump_mode = "testbench"`: reuse an existing testbench containing something equivalent to `initial begin $fsdbDumpfile("..."); $fsdbDumpvars(0, tb_top); end`. Keep dump statements in testbench (not in source DUT). The testbench path must produce FSDB at the configured output path, or reconcile where it actually writes it. The adapter does not inject source changes.
- `fsdb_dump_mode = "ucli"`: run VCS via `simv -ucli -do <generated-script>` with UCLI script `call {$fsdbDumpfile("/absolute/output.fsdb")}`, `call {$fsdbDumpvars(0, tb_top)}`, `run`, `quit`. The adapter generates the script under `eda/fsdb_dump.ucli`, not inside RTL. Scope syntax / PLI linkage varies by installed versions; when it fails, use your site's documented VCS/Verdi method. The adapter requires a pre-existing `simv` from the compile stage.

With modern VCS+Verdi installations, setting `VERDI_HOME` and compiling with `-debug_access` generally enables FSDB dumping without an explicit legacy `-P novas.tab pli.a`; if the site setup needs explicit PLI/link flags, configure them through `compile_extra` instead of guessing paths. Do not automatically add obsolete flags (e.g. `+memcbk`) to modern VCS versions.

## 3. Verdi examination and FSDB export

GUI, **explicit user request and display server required**:

```bash
python3 <skill>/scripts/vcs_verdi.py --config vcs_verdi.json open        # plan
python3 <skill>/scripts/vcs_verdi.py --config vcs_verdi.json --execute open # GUI
```

The generated GUI command resembles `verdi -ssf path/to/waves.fsdb -nologo`. Merely launching Verdi does not certify human inspection; if a signal/clock mapping was manually reviewed, record the actual reviewer, inspected scopes and time window.

FSDB is not readable by the bundled VCD parser. The flow **uses Verdi's `fsdb2vcd` utility**, then the included converter. `convert_extra` may include Verdi-version-supported scope/time filters such as `-s /tb_top/dut`, `-bt`, `-et` after checking site version help; whole-design conversion may be huge. `fsdb2vcd` should be taken from a licensed Verdi installation (`VERDI_HOME/bin` when available). It is not an open-source tool and not provided here.

Example after successful actual VCS/Verdi runs:

```bash
python3 <skill>/scripts/vcd_to_wavedrom.py \
  --vcd docs/rtl_spec/eda/waves.vcd --clock tb_top.clk \
  --signals tb_top.rst_n tb_top.dut.req tb_top.dut.ready \
  --cycles 12 \
  --verdi-manifest docs/rtl_spec/eda/convert_manifest.json \
  --vcs-run-manifest docs/rtl_spec/eda/run_manifest.json \
  --out docs/rtl_spec/waveforms/transfer_observed.json5 \
  --svg docs/rtl_spec/waveforms/transfer_observed.svg
```

The converter validates the VCD hash against the Verdi conversion manifest and FSDB hash against the VCS run manifest **before labeling a figure VCS/VERDI OBSERVED**. The VCD sample after timestamp changes is distinct from the **pre-edge** handshaking decision. Document sample semantics and every trace window. An FSDB or VCD file from an unknown origin may still be analyzed, but remains untrusted provenance and must not receive the verified command-chain label.

## 4. Reliability and security

- No copying RTL, FSDB, logs, test vectors, encrypted IP or waveform snapshots to a third-party service.
- `--execute` needs local executable access, a valid license, build space and permission; no unattended installation/license activation.
- Preserve the original design. Compile artifacts go to configured output, but project-defined VCS source hooks may still produce extra side effects; review custom build scripts and filelists first.
- Internal sources may be confidential; generated GitHub repo should contain **only the Skill**, not proprietary project outputs.
- If tools are absent or fail, mark `VCS/VERDI NOT RUN` with actual reason, keep illustration `ILLUSTRATIVE — NOT SIMULATED`, do not substitute Icarus/Verilator as the default and do not pretend the flow ran.

## References (vendor documentation and public details)

- Synopsys VCS verification solution: https://www.synopsys.com/verification/simulation/vcs.html
- Synopsys Verdi Waveform Utilities (FSDB reports and 2vcd): https://www.synopsys.com/blogs/chip-design/verdi-waveform-utilities.html
- Intel/Altera VCS RTL simulation command examples: https://resources.altera.com/quartushelp/17.0/eda/simulation/vcs/eda_pro_vcs_func_sim.htm
- VCS V-2023.12 User Guide (vendor manual mirrored externally; consult your licensed copy for authoritative installed-version syntax): https://device.report/m/21147a58a2161729f264107c63437223e00ed7e3bf0dc09504e86cb06b5da352
- Verdi fsdb2vcd examples (manual mirrored externally; syntax may differ by version): https://iccircle.com/static/upload/img20241018151608.pdf
