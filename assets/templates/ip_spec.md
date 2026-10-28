# IP Specification — {top}

| Document field | Value |
| --- | --- |
| Document ID | [TODO: unique document identifier] |
| IP Name | {top} |
| Top Module | `{top}` |
| Revision | 0.2-draft |
| Status | DRAFT — not approved for release |
| Classification | [TODO: public/internal/confidential] |
| Date | [TODO: ISO date] |
| RTL Source Revision | [TODO: Git commit or source snapshot hash] |
| Configuration ID | [TODO: source filelist, parameters, defines, include paths] |
| Author / Reviewer / Approver | [TODO: actual roles; never fabricate approvals] |

> **Evidence status:** RTL-DERIVED / NOT SIMULATED until real VCS and Verdi evidence has been recorded. This is an **as-implemented IP specification**, not a proposed design.

## 1. Document Control

**Table 1-1 — Revision History**

| Rev. | Date | Changes | Author | Review / approval state |
| --- | --- | --- | --- | --- |
| 0.2-draft | [TODO: date] | Initial RTL-derived specification | [TODO] | Not reviewed |

[TODO: ownership, release/approval policy, confidentiality and distribution; an unapproved document must not be marked RELEASED]

## 2. Scope and References

[TODO: scope of documented IP, analyzed configuration, excluded implementation blocks, standards only if substantiated, related documents; define normative vs informative references]

## 3. IP Overview and Features

[TODO: purpose, user-visible functions, supported configurations, major behavior and explicit non-features; source citations]

## 4. Configuration and Deliverables

**Table 4-1 — Analyzed Configuration**

| Item | Effective value | Provenance / build evidence |
| --- | --- | --- |
| DUT top | `{top}` | [TODO: file:line and elaboration] |
| Active compile filelist | [TODO] | [TODO] |
| `define` set / parameters | [TODO] | [TODO] |
| EDA | Synopsys VCS (simulation), Synopsys Verdi (waveform) | NOT RUN / [TODO: actual versions and logs] |

[TODO: source files, memory images, generated blocks, known black boxes, release deliverables]

## 5. Architecture and Hierarchy

[TODO: source-backed Mermaid top-level block diagram with actual connections and module mapping]

**Figure 5-1 — IP Architecture**

[TODO: diagram and cited RTL files/lines; distinguish resolved hierarchy from lexical candidates]

## 6. External Interface Specification

**Table 6-1 — Top-Level Signal Definitions**

| Signal | Direction | Width / type | Clock domain | Reset / default | Functional meaning | Handshake / timing | RTL evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | [TODO: file:line] |

[TODO: protocol timing contract (only if implemented); packet/data format, sidebands, active-level conventions, backpressure and interoperability]

## 7. Clocks, Resets and CDC

**Table 7-1 — Clock/Reset Summary**

| Name | Domain | Frequency / assumption | Edge / polarity | Synchrony and release | Affected state / RTL evidence |
| --- | --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO: derived or integration-specified] | [TODO] | [TODO] | [TODO] |

[TODO: reset assertion/deassertion, reset-state outputs, clock gating, CDC paths; never invent a frequency or guaranteed timing closure]

## 8. Functional Operation

[TODO: operation phases, transaction rules, state progression, data processing, register updates, ordinary and exceptional behavior; source-backed state machine and algorithm description]

## 9. Timing and Waveform Scenarios

**Table 9-1 — Timing Scenario Coverage**

| Scenario ID | Trigger / initial state | Expected behavior and boundary | Waveform | Evidence class | Verification |
| --- | --- | --- | --- | --- | --- |
| [TODO: T-01] | [TODO] | [TODO] | [TODO: waveforms/*.svg] | ILLUSTRATIVE | NOT RUN |

[TODO: one separately labeled Figure 9-n (embedded SVG), its timing table, clock-edge convention, and source citation for each applicable key scenario: reset, one transaction, pipelined/consecutive, stalls, exceptional flows]

## 10. Register and Memory Map

[TODO: programmer-visible address/register table, access type, reset values, side effects, alignment and behavior with RTL evidence; if no addressable register interface exists state **N/A — no software-visible register interface in this RTL**. Internal registers belong in module specs.]

## 11. Exceptions, Constraints and Integration

[TODO: reset during active transactions, illegal input states, FIFO overflow/underflow if implemented, error/interrupt indications, clock/power assumptions, external IP dependencies, timing and use limitations]

## 12. Verification and Evidence

**Table 12-1 — Verification Evidence Matrix**

| Evidence ID | Scenario / claim | Tool | Config / command | Artifact | Result / confidence |
| --- | --- | --- | --- | --- | --- |
| VE-01 | [TODO: hierarchy and timing] | Synopsys VCS / Verdi | NOT RUN | NOT AVAILABLE | UNVERIFIED |

[TODO: exact VCS compile/run logs, testbench checkers, FSDB provenance, Verdi inspection/export reports, assertions, failures, skips, tool versions. No FSDB alone implies PASS.]

## 13. Traceability and Open Issues

**Table 13-1 — Requirement/Implementation Evidence Index**

| Spec clause | Behavior claim | RTL file:line | EDA evidence | Confidence | Open issue |
| --- | --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | NOT RUN | RTL-DERIVED | [TODO] |

[TODO: open questions, unexpanded configuration, excluded blackboxes, evidence limitations and release blockers]

## Appendix A. Module Index

{module_index}

## Appendix B. Glossary

[TODO: terms and abbreviations actually used; avoid labeling a protocol AXI/AMBA unless the RTL supports it]
