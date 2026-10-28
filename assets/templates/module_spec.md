# Module Design Specification — {module}

| Document field | Value |
| --- | --- |
| Module | `{module}` |
| Parent IP / configuration | [TODO] |
| Source | `{source}:{line}` |
| Revision / status | 0.3-draft / DRAFT |

## 1. Module Function（模块功能）

[TODO: 先用 2～4 句讲清该模块处理哪些输入、产生什么结果、在系统里起什么作用，引用 `{source}:{line}`。]

## 2. Parameters and Build Configuration（参数与编译配置）

**Table 2-1 — Module Parameters**

| Parameter | Default | Effective value | Purpose / constraint | RTL source |
| --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | [TODO] | `{source}:{line}` |

## 3. Port and Protocol Definition（端口与协议）

[TODO: 先说明接口怎样完成一笔事务，再列出完整端口。]

**Table 3-1 — Module Ports**

| Port | Direction | Width / type | Clock | Reset/default | Meaning / sampling rule | RTL source |
| --- | --- | --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | `{source}:{line}` |

## 4. Clock and Reset（时钟与复位）

[TODO: 明确复位有效电平、同步/异步、复位值、释放后的更新时刻和优先级。]

## 5. State, Datapath and Register Behavior（状态与数据通路）

**Table 5-1 — Internal State and Registers**

| Register / state | Width | Reset value | Update and hold condition | RTL source |
| --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | [TODO] | `{source}:{line}` |

[TODO: 解释 FSM 状态转换、数据寄存器怎样配合、何时保持旧值。先说行为，再给必要公式。]

## 6. Functional and Cycle-Level Operation（功能与周期时序）

**Cycle convention:** [TODO: 指明时钟沿、周期 0、沿前握手和沿后输出]

**Table 6-1 — Cycle-Accurate Transaction**

| Cycle | Inputs / handshake before edge | State before → after | Outputs after edge | RTL evidence |
| --- | --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | [TODO] | `{source}:{line}` |

[TODO: 用一段话概括延迟、吞吐率和停顿条件，不要重复整张周期表。]

## 7. Timing and Waveform Scenarios（典型时序）

[TODO: 插入实际支持场景的 `../waveforms/<name>.svg`，使用 Figure 7-n 图题和「RTL 推导」/「VCS/Verdi 波形」短标签；说明图中的关键边沿。]

## 8. Verification Evidence（验证记录）

**Table 8-1 — Module Verification**

| Check | Tool / input | Artifact | Result |
| --- | --- | --- | --- |
| [TODO] | [TODO] | [TODO] | 未执行 / PASS / FAIL |

## 9. RTL Traceability and Open Issues（源码追溯与待确认事项）

- `{source}:{line}` — 模块定义。
- [TODO: 其余关键行为的源码证据，以及真实存在的待确认事项。]
