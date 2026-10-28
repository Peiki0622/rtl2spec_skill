# Module Design Specification — {module}

| Document field | Value |
| --- | --- |
| Module | `{module}` |
| Parent IP / configuration | [TODO] |
| Source | `{source}:{line}` |
| Revision / status | 0.2-draft / DRAFT |
| Design elaboration | NOT RUN — lexical discovery only |
| Verification | NOT RUN — no VCS/Verdi evidence yet |

## 1. Module Function

[TODO: externally observable function and non-functions; use `{source}:{line}` references]

## 2. Parameters and Build Configuration

**Table 2-1 — Module Parameters**

| Parameter | Default | Effective value | Constraint | Source |
| --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | [TODO] | `{source}:{line}` |

## 3. Port and Protocol Definition

**Table 3-1 — Module Ports**

| Port | Dir. | Exact width / type | Domain | Reset/default | Sampling/driving rule | RTL source |
| --- | --- | --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | `{source}:{line}` |

[TODO: port-level data transfer contract, no unsupported protocol names]

## 4. Clock and Reset

[TODO: sensitivity, async/sync, polarities, priorities, deassertion, state reset values, CDC / clock gating constraints and citations]

## 5. State, Datapath and Register Behavior

**Table 5-1 — Internal Register / State Inventory**

| Register/state | Width | Reset value | Update condition / equation | Source |
| --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | [TODO] | `{source}:{line}` |

[TODO: FSM state encoding and transition table, datapath equations, memory behavior, decision priorities; old-vs-new semantics of nonblocking assignments]

## 6. Functional and Cycle-Level Operation

**Cycle convention:** [TODO: pre-edge handshake vs post-NBA output; clock edge; cycle 0 definition]

**Table 6-1 — Cycle-Accurate Transaction**

| Cycle / edge | Inputs and pre-edge handshake | State before → after | Outputs post-edge | RTL evidence |
| --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | [TODO] | `{source}:{line}` |

[TODO: latency, initiation interval and throughput under explicitly stated ready/stall conditions]

## 7. Timing and Waveform Scenarios

[TODO: Figure 7-1 linked `../waveforms/<name>.svg`, class ILLUSTRATIVE or VCS/VERDI OBSERVED, signal list, scenario start/end and cycle table alignment]

## 8. Verification Evidence

**Table 8-1 — Module Test Evidence**

| Check | Testbench / command | VCS result | Verdi FSDB / conversion | Observed limitations |
| --- | --- | --- | --- | --- |
| [TODO] | NOT RUN | NOT RUN | NOT AVAILABLE | [TODO] |

[TODO: assertions and checker results, simulator exit code vs actual functional checks, FSDB hash, any unresolved failures]

## 9. RTL Traceability and Open Issues

- `{source}:{line}` — module declaration.
- [TODO: trace significant register/interface/timing claims back to actual source lines; unknowns and unsupported variants]
