# Module: rv_stage

**Status:** source-reviewed demonstration; no RTL simulator run  
**Source:** `rv_stage.v:2`  
**Configuration:** `WIDTH=8` in the example; parameters/other configurations have not been elaborated by an external EDA tool.

## Function

`rv_stage` implements a single-slot ready/valid register stage. When the slot is empty or the downstream is ready, it may accept a new item; if downstream is blocked and the slot holds an item, both `out_data` and `out_valid` remain unchanged (`rv_stage.v:15`, `rv_stage.v:21`). The interface does **not** include a separate `start` or `done` signal.

## Parameters

| Parameter | Default / effective value | Meaning | RTL evidence |
| --- | --- | --- | --- |
| `WIDTH` | `8` / `8` in example | Data bus width; no explicit supported range asserted | `rv_stage.v:2-10` |

## Interface

| Port | Dir. | Width expression | Function / timing | RTL evidence |
| --- | --- | --- | --- | --- |
| `clk` | input | 1 | Rising-edge capture clock | `rv_stage.v:5`, `rv_stage.v:17` |
| `rst_n` | input | 1 | Active-low asynchronous reset | `rv_stage.v:6`, `rv_stage.v:17-20` |
| `in_data` | input | `WIDTH` | Data captured on rising edge if `in_ready & in_valid` | `rv_stage.v:7`, `rv_stage.v:21-24` |
| `in_valid` | input | 1 | Input item valid | `rv_stage.v:8`, `rv_stage.v:22` |
| `in_ready` | output | 1 | `!out_valid || out_ready` (combinational) | `rv_stage.v:9`, `rv_stage.v:15` |
| `out_data` | output | `WIDTH` | Registered captured data, retains previous value when invalid | `rv_stage.v:10`, `rv_stage.v:20-24` |
| `out_valid` | output | 1 | Registered valid bit | `rv_stage.v:11`, `rv_stage.v:19-22` |
| `out_ready` | input | 1 | Downstream permission to remove/replace item | `rv_stage.v:12`, `rv_stage.v:15` |

## Clock and Reset

`always @(posedge clk or negedge rst_n)` causes an **asynchronous active-low reset**. Assertion of `rst_n=0` clears `out_valid` and `out_data` without waiting for `clk`; otherwise state changes on `clk` rising edges (`rv_stage.v:17-25`). `in_ready` is combinational and can change with `out_ready` or updated `out_valid` (`rv_stage.v:15`). The RTL itself does not implement a reset deassertion synchronizer or specify setup/hold timing; these remain integration assumptions.

## State and Algorithm

`out_valid` is the occupancy bit. On reset it clears (`rv_stage.v:18-20`). Otherwise, if `in_ready=1`, `out_valid` takes `in_valid`; when `in_valid=1`, `out_data` takes `in_data`. If `in_ready=0`, **both registers hold** (`rv_stage.v:21-25`). If `in_ready=1 && in_valid=0`, `out_valid` clears while `out_data` retains its previous bits. This old-data retention is legal only when consumers heed `out_valid`.

## Cycle Timing

**Cycle definition:** C0..C5 represent **post-timestamp values after** `clk` rising edges at t=5,15,25,35,45,55 ns in the synthetic VCD fixture. Transaction acceptance uses signals *before* each active edge. Registered outputs are observed after the edge. `in_ready` can update in the same timestamp as `out_valid` (`rv_stage.v:15`, `rv_stage.v:17-24`).

| Cycle | Inputs / handshake (pre-edge) | State before → after edge | Post-edge output | Evidence |
| --- | --- | --- | --- | --- |
| C0, t5 | `rst_n=0` | reset → empty | `out_valid=0`, `out_data=0` | `rv_stage.v:17-20` |
| C1, t15 | `in_valid=1`, A5; `in_ready=1` | empty → A5 occupied | `out_valid=1`, `out_data=A5`; post `in_ready=0` | `rv_stage.v:15`, `rv_stage.v:21-24` |
| C2, t25 | `in_valid=1`, 3C; `out_ready=0`, `in_ready=0` | A5 occupied → same | A5 held, `out_valid=1` | `rv_stage.v:15`, `rv_stage.v:21` |
| C3, t35 | `out_ready=1`, `in_valid=1`, 3C; `in_ready=1` | A5 occupied → 3C occupied | `out_valid=1`, `out_data=3C` | `rv_stage.v:15`, `rv_stage.v:21-24` |
| C4, t45 | `out_ready=1`, `in_valid=0` | 3C occupied → empty | `out_valid=0`, `out_data=3C` (stale) | `rv_stage.v:21-24` |
| C5, t55 | `in_valid=0` | empty → empty | unchanged | `rv_stage.v:21-24` |

Latency is one rising-edge register capture: accepted `in_data` becomes registered `out_data` after that edge. Under continuously ready downstream, the stage can accept a new item each cycle. The RTL provides no multi-entry FIFO.

## Waveform Scenarios

**ILLUSTRATIVE — NOT SIMULATED**: stall and replacement transaction, manually sourced from `rv_stage.v:15-24`:

![Illustrative ready-valid timing](../waveforms/accept_stall_illustrative.svg)

The synthetic VCD fixture is included solely to exercise the converter. **VCD-OBSERVED IN A HAND-AUTHORED FILE — NOT A REAL RTL SIMULATION**:

![Handmade VCD parser fixture](../waveforms/fixture_trace.svg)

The WaveDrom source files are `../waveforms/accept_stall_illustrative.json5` and `../waveforms/fixture_trace.json5`. In the sampled diagram, ready/valid reflect **post-edge** levels, not the handshake decision made immediately before the edge.

## Source Evidence

- `rv_stage.v:2` — module declaration / parameterization.
- `rv_stage.v:5` — clock port.
- `rv_stage.v:15` — combinational `in_ready` formula.
- `rv_stage.v:17-25` — asynchronous reset and register updates.

## Unknowns and Verification

- **NOT RUN:** real Icarus/Verilator simulation, lint, synthesis, formal or hardware tests.
- The VCD is a hand-authored test fixture, not a captured simulator run; expected behavior is matched by code inspection, not testbench assertions.
- CDC, electrical timing, and parameterized width corner cases are outside this demonstration.
