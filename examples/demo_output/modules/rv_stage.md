# Module Design Specification — rv_stage

| Document field | Value |
| --- | --- |
| Module | `rv_stage` |
| Parent IP / configuration | rv_stage / WIDTH=8 |
| Source | `rv_stage.v:2` |
| Revision / status | 0.2-demo / DRAFT — example only |
| Design elaboration | VCS NOT RUN; lexical inventory only |
| Verification | VCS/Verdi NOT RUN; synthetic parser fixture only |

## 1. Module Function

`rv_stage` is a one-slot register stage for data and valid state. The input can be accepted when the output is empty or downstream is ready; during stall the output registers hold (`rv_stage.v:15`, `rv_stage.v:21-25`). No other protocol or address bus is implemented.

## 2. Parameters and Build Configuration

**Table 2-1 — Module Parameters**

| Parameter | Default | Effective value | Constraint | Source |
| --- | --- | --- | --- | --- |
| `WIDTH` | 8 | 8 for this demonstration | Valid positive packed width assumed; not exhaustively checked | `rv_stage.v:2-10` |

No VCS parameter elaboration was executed; actual variant coverage is not established.

## 3. Port and Protocol Definition

**Table 3-1 — Module Ports**

| Port | Dir. | Width/type | Domain | Reset/default | Cycle role | RTL source |
| --- | --- | --- | --- | --- | --- | --- |
| `clk` | input | 1 | clk | N/A | Rising-edge capture | `rv_stage.v:5`, `rv_stage.v:17` |
| `rst_n` | input | 1 | clk/async | active-low | Immediate reset assertion | `rv_stage.v:6`, `rv_stage.v:17` |
| `in_data` | input | WIDTH | clk | external | Capture when input accepted and valid | `rv_stage.v:7`, `rv_stage.v:23` |
| `in_valid` | input | 1 | clk | external | Pre-edge acceptance qualifier | `rv_stage.v:8`, `rv_stage.v:22` |
| `in_ready` | output | 1 | clk | combinational | `!out_valid || out_ready` | `rv_stage.v:9`, `rv_stage.v:15` |
| `out_data` | output | WIDTH | clk | 0 | Stored output data | `rv_stage.v:10`, `rv_stage.v:20-24` |
| `out_valid` | output | 1 | clk | 0 | Stored output valid | `rv_stage.v:11`, `rv_stage.v:19-22` |
| `out_ready` | input | 1 | clk | external | Downstream can consume slot | `rv_stage.v:12`, `rv_stage.v:15` |

The interface is local ready/valid; it is not an AXI interface.

## 4. Clock and Reset

The active event is `posedge clk`; `negedge rst_n` is also in the sensitivity list, making reset **asynchronous and active low** (`rv_stage.v:17`). During reset both data and valid are cleared (`rv_stage.v:18-20`). No deassertion synchronizer is present; system integration must handle reset release.

## 5. State, Datapath and Register Behavior

**Table 5-1 — Register State and Update Conditions**

| Register | Width | Reset value | Update condition | RTL source |
| --- | --- | --- | --- | --- |
| `out_valid` | 1 | 0 | If `in_ready`, assign `in_valid`; otherwise hold | `rv_stage.v:19`, `rv_stage.v:21-22` |
| `out_data` | WIDTH | 0 | If `in_ready && in_valid`, assign `in_data`; otherwise hold | `rv_stage.v:20`, `rv_stage.v:21-24` |

A single registered occupancy bit represents empty/occupied behavior. No separately encoded FSM exists. Data and valid are governed by nonblocking assignments, so register updates become visible after the edge and use pre-edge input/state (`rv_stage.v:17-25`).

## 6. Functional and Cycle-Level Operation

**Cycle convention:** C0–C5 denote values *after* the timestamp of rising edges at 5, 15, 25, 35, 45 and 55 ns in a **hand-authored VCD parser fixture**. The table's transfer decisions depend on **pre-edge handshake**. The fixture is explanatory and is not a VCS simulation result (`rv_stage.v:15`, `rv_stage.v:17-24`).

**Table 6-1 — Cycle-Accurate Example**

| Cycle | Pre-edge inputs / handshake | State before → after | Post-edge output | RTL source |
| --- | --- | --- | --- | --- |
| C0 | `rst_n=0` | reset → empty | `out_valid=0`, `out_data=0` | `rv_stage.v:17-20` |
| C1 | `in_valid=1`, `in_data=A5`, `in_ready=1` | empty → A5 occupied | `out_valid=1`, `out_data=A5`, post `in_ready=0` | `rv_stage.v:15`, `rv_stage.v:21-24` |
| C2 | `in_valid=1`, `out_ready=0`, `in_ready=0` | A5 occupied → A5 occupied | Holds A5 and valid | `rv_stage.v:15`, `rv_stage.v:21` |
| C3 | `out_ready=1`, `in_valid=1`, `in_data=3C` | A5 occupied → 3C occupied | `out_valid=1`, `out_data=3C` | `rv_stage.v:15`, `rv_stage.v:21-24` |
| C4 | `out_ready=1`, `in_valid=0` | 3C occupied → empty | `out_valid=0`, stale `out_data=3C` | `rv_stage.v:21-24` |
| C5 | `in_valid=0` | empty → empty | unchanged | `rv_stage.v:21-24` |

The data is registered on an accepted rising edge. With downstream always ready the stage can accept a word every edge; the output is visible after the acceptance edge, subject to valid. There is no multi-entry FIFO (`rv_stage.v:15-25`).

## 7. Timing and Waveform Scenarios

**Figure 7-1 — Reset, acceptance, stall and replacement (ILLUSTRATIVE — NOT SIMULATED).**

![RTL-derived ready/valid timing](../waveforms/accept_stall_illustrative.svg)

**Figure 7-2 — Handmade parser input, not a VCS trace (SYNTHETIC FIXTURE — NOT SIMULATED).**

![Handmade VCD timing fixture](../waveforms/fixture_trace.svg)

Waveform sources: `../waveforms/accept_stall_illustrative.json5` and `../waveforms/fixture_trace.json5`. They only show post-timestamp samples; a transfer at an edge cannot be inferred from a post-edge `valid && ready` pair without comparing pre-edge conditions (`rv_stage.v:15-25`).

## 8. Verification Evidence

**Table 8-1 — Module Verification Matrix**

| Check | Tool | Observed evidence | Result | Limits |
| --- | --- | --- | --- | --- |
| Register update review | RTL analysis | `rv_stage.v:17-25` | Source-derived only | Not simulator proven |
| SVG rendering | Local renderer | `accept_stall_illustrative.svg` | Diagram generated | Illustration only |
| Parser exercise | VCD converter | Handwritten `fixture.vcd` | Parsing exercise | Synthetic input |
| Licensed simulator/debug | Synopsys VCS + Verdi | NOT RUN | UNVERIFIED | No FSDB/log/run manifests |

A future self-checking VCS testbench must independently assert backpressure hold, transfer replacement and valid behavior; Verdi may then examine actual FSDB events.

## 9. RTL Traceability and Open Issues

- `rv_stage.v:2` — module declaration and WIDTH.
- `rv_stage.v:5-12` — input/output ports.
- `rv_stage.v:15` — in_ready equation.
- `rv_stage.v:17-25` — reset and state updates.
- Open: VCS/Verdi not run, alternative parameters not elaborated, no reset-release integration verification, no timing closure data.
