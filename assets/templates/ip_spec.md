# IP Specification — {top}

| Document field | Value |
| --- | --- |
| Document ID | [TODO: unique document identifier] |
| IP Name | {top} |
| Top Module | `{top}` |
| Revision | 0.3-draft |
| Status | DRAFT |
| Classification | [TODO: public/internal/confidential] |
| Date | [TODO: ISO date] |
| RTL Source Revision | [TODO: Git commit or source snapshot hash] |
| Configuration ID | [TODO: source filelist, parameters, defines, include paths] |
| Author / Reviewer / Approver | [TODO: actual roles or N/A] |

## 1. Document Control（文档信息）

**Table 1-1 — Revision History**

| Rev. | Date | Changes | Author | Review status |
| --- | --- | --- | --- | --- |
| 0.3-draft | [TODO: date] | [TODO: scope of this revision] | [TODO] | DRAFT |

## 2. Scope and References（适用范围）

[TODO: 本文覆盖的 IP、使用配置和相关资料。只列真正影响使用或集成的边界。]

## 3. IP Overview and Features（功能概述）

[TODO: 第一段用 2～4 句说明 IP 做什么、处理什么输入、输出什么结果，以及通常如何启动/结束。不以免责提示开头。]

[TODO: 简洁列出真实 RTL 支持的主要功能/模式，关键结论引用 RTL 文件与行号。]

## 4. Configuration and Deliverables（配置与交付内容）

**Table 4-1 — Analyzed Configuration**

| Item | Effective value | Source |
| --- | --- | --- |
| DUT top | `{top}` | [TODO: file:line] |
| Filelist | [TODO] | [TODO] |
| Parameters / defines | [TODO] | [TODO] |
| Simulation / debug tools | Synopsys VCS / Verdi | [TODO: actual version, or 未执行] |

[TODO: 编译配置、源码组织和交付文件；不反复解释工具未运行的含义。]

## 5. Architecture and Hierarchy（整体架构）

[TODO: 先解释关键模块怎样配合处理一次事务，再插入基于 RTL 的模块连接图。]

**Figure 5-1 — IP Architecture**

[TODO: Mermaid architecture and actual module/connection evidence]

## 6. External Interface Specification（外部接口）

[TODO: 用一段话解释主要接口的分组、传输方式和关键握手条件。]

**Table 6-1 — Top-Level Signal Definitions**

| Signal | Direction | Width / type | Clock | Reset / default | Meaning | Timing / condition | RTL source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | [TODO: file:line] |

## 7. Clocks, Resets and CDC（时钟与复位）

**Table 7-1 — Clock/Reset Summary**

| Name | Domain | Frequency / condition | Active edge / level | Behavior | RTL source |
| --- | --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | [TODO] |

[TODO: 明确复位时哪些寄存器被清零、何时恢复工作；如存在 CDC，说明具体跨域机制与使用条件。]

## 8. Functional Operation（工作原理）

[TODO: 按功能流程解释：触发条件 → 数据处理 → 状态更新 → 结果输出。给出状态/运算条件，不要逐行复述 RTL。]

## 9. Timing and Waveform Scenarios（时序与波形）

**Table 9-1 — Timing Scenario Coverage**

| Scenario | Start condition | Key behavior | Figure | Source | Verification |
| --- | --- | --- | --- | --- | --- |
| [TODO: T-01] | [TODO] | [TODO] | [TODO: waveforms/*.svg] | RTL 推导 | [TODO: 记录在第 12 章] |

[TODO: 对每种实际存在的关键操作，先用 2～3 句解释时序，再给逐周期表和 SVG。每张图题简写为「（RTL 推导）」或「（VCS/Verdi 波形）」。说明采样沿和有效信号条件。]

## 10. Register and Memory Map（寄存器与存储器）

[TODO: 如果有软件可见寄存器，给出地址/读写/复位/副作用；若无，写一条「N/A：本 IP 没有软件可访问的寄存器接口」，并引用端口定义。内部状态寄存器放模块 Spec。]

## 11. Exceptions, Constraints and Integration（异常与集成要求）

[TODO: 只写具体影响集成的条件：复位中断事务、非法输入、握手停顿、时钟/外设依赖等。写清「条件 → 行为/影响」，不写笼统免责段落。]

## 12. Verification and Evidence（验证记录）

**Table 12-1 — Verification Evidence Matrix**

| Evidence ID | Check | Tool | Input / condition | Artifact | Result |
| --- | --- | --- | --- | --- | --- |
| VE-01 | [TODO: check] | VCS / Verdi / RTL review | [TODO] | [TODO] | 未执行 / PASS / FAIL |

[TODO: 将未执行、未知配置、FSDB/VCD 追踪等信息集中放这里。不要在前面 11 个章节重复说明。]

## 13. Traceability and Open Issues（源码追溯与待确认事项）

**Table 13-1 — Spec-to-RTL Traceability**

| Clause | Behavior | RTL source | Verification evidence | Open item |
| --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO: file:line] | [TODO] | [TODO] |

[TODO: 只列具体的未解决问题，不追加泛泛而谈的「不保证正确性」。]

## Appendix A. Module Index（模块索引）

{module_index}

## Appendix B. Glossary（术语）

[TODO: 首次出现且可能产生歧义的专业缩写，例如 FSM、CDC、FSDB、valid/ready。]
