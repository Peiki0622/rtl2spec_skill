# As-implemented specification contract

**Scope:** This is reverse documentation of *actual RTL*, not an implementation proposal, security certification, or a reconstruction from a requirement document. Work from the resolved compiled configuration. Every nontrivial timing fact needs an exact source location and, where possible, a verification record.

## Design discovery

- The module inventory is a heuristic lexical index. Recover compilation units, package order, top module, filelist recursion, macros and parameter overrides from the project or an elaborator; note unsupported conditions.
- Resolve instance names, port maps, generated blocks and hierarchy. Do not assume that a module's file name equals the module name, or that unreferenced modules are always the top.
- A parameter-dependent or `ifdef`-dependent behavior is only claimed for the analyzed configuration. List configuration explicitly.
- If proprietary IP, encrypted RTL, DPI, memory models, clock-domain controls or blackboxes block analysis, mark their internal behavior **unknown**, not inferred.

## Module spec headings (keep these headers for validation)

### `## Function`
Purpose and actual externally observable behavior, not intent.

### `## Parameters`
Name, effective/default value, units/meaning, constraints, selected configuration, proof source.

### `## Interface`
Port, direction, *exact expression* of bit width, semantics, cycle sampling/driving, active level, source. Explicitly describe ready/valid, credit, bus timing if present. Don't label something AXI/AMBA if RTL doesn't implement the contract.

### `## Clock and Reset`
Domains, active polarity, synchronous/asynchronous sensitivity, reset priority/values, release assumptions, CDC concerns. Explicitly differentiate asynchronous `or negedge rst_n` from synchronous `if (!rst_n)` inside `@(posedge clk)`.

### `## State and Algorithm`
Register names and update conditions, FSM encoding/transition table, combinational datapath operations and priority; distinguish old state from next state for `<=`. List blackboxes and unsupported assertions. Use Mermaid for substantial FSMs.

### `## Cycle Timing`
Declare cycle 0 and sampling convention; quantify input acceptance, data availability, valid visibility, stalls, throughput and reset latency only when derivable. Include a cycle-by-cycle transaction table: cycle, inputs/handshake, state before/after, outputs, RTL references. Include consecutive transactions and corner cases when applicable.

### `## Waveform Scenarios`
List referenced `.json5` and `.svg` files, **illustrative or VCD-observed** class, scenario purpose, source lines and simulation provenance, plus a short note explaining the illustrated behavior. Required at least one scenario for a fully documented top IP; if missing, explain why, and strict validation will flag it.

### `## Source Evidence`
Use `rtl/path/module.sv:42` (backticks acceptable) for each nontrivial interface behavior, state update and timing claim. Distinguish behavior derived across multiple lines by citing the range in prose (`rtl/m.sv:42-51`). Paths must be relative to repository root and evidence should be checked against the **current** source snapshot. A conceptual diagram without traceable claims is not evidence.

### `## Unknowns and Verification`
Record unresolved behavior, missing definitions, untested configurations, lint/simulation tool availability and **precise run commands/results**. List `NOT RUN` or `UNVERIFIED` when appropriate; never claim a fabricated pass.

## IP spec headings (keep these headers for validation)

- `## Overview`: IP name, as-implemented feature summary, configuration and behavior limitations.
- `## Hierarchy and Architecture`: Mermaid block diagram with all resolved design modules and their source locations; avoid invented connections.
- `## Interfaces`: external port table and protocol constraints, not merely a list of names.
- `## Clock and Reset Domains`: domain table, CDC notes, reset synchrony and priority.
- `## Behavior and Timing`: algorithms/operations, sequencing, exact latency contract, throughput (only if supported), interrupt/error responses when present.
- `## Waveform Scenarios`: examples with images and cycle tables, provenance labels, separate observed vs illustrative.
- `## Verification`: reproducible commands, tool versions, actual evidence and scope, warnings and failed checks.
- `## Assumptions and Open Questions`: all unverified choices, external modules and ambiguous timing.
- `## Source Evidence`: cross-reference inventory and key RTL line citations.

## Wording / claim integrity

- `RTL-DERIVED`: inferred by inspecting code and explaining semantics. May be wrong; confirm carefully.
- `TOOL-ELABORATED`: hierarchy/widths determined by a real elaborator for a recorded configuration.
- `ILLUSTRATIVE`: waveform drawn from manual/agent analysis, not executed.
- `VCD-OBSERVED`: signal transitions read from an actual file. Its provenance may still be unknown.
- `SIMULATION-PASS`: only if a recorded run has a self-checking pass criterion that was checked. A simulator exit code of 0 alone may not test behavior.
- `FORMALLY-PROVEN`: only if formal results actually support stated property under declared assumptions.

Do not use `SIMULATION-PASS`, `FORMALLY-PROVEN`, or `TESTED` as a synonym for reading or rendering a waveform.
