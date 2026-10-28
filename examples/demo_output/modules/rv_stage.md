# Module Design Specification — rv_stage

| Document field | Value |
| --- | --- |
| Module | `rv_stage` |
| Parent IP / configuration | `rv_stage` / `WIDTH=8` |
| Source | `rv_stage.v:2` |
| Revision / status | 0.3-demo / DRAFT |

## 1. Module Function（模块功能）

`rv_stage` 是一个单级数据缓冲模块。它把上游送来的 `in_data` 保存到输出寄存器，并使用 `out_valid` 表示数据是否有效。只要缓冲为空，或者下游准备取走当前数据，模块就能接收下一笔输入（`rv_stage.v:15-25`）。

## 2. Parameters and Build Configuration（参数与编译配置）

**Table 2-1 — Module Parameters**

| Parameter | Default | Effective value | Meaning | RTL source |
| --- | --- | --- | --- | --- |
| `WIDTH` | 8 | 8 | 输入、输出数据总线宽度 | `rv_stage.v:2-4` |

本示例采用源码默认参数 `WIDTH=8`。

## 3. Port and Protocol Definition（端口与协议）

模块有两侧 ready/valid 接口。上游在 `in_valid && in_ready` 成立的上升沿送入新数据；下游在 `out_valid && out_ready` 成立的上升沿取走旧数据。这两个动作可以在同一个上升沿发生（`rv_stage.v:15-25`）。

**Table 3-1 — Module Ports**

| Port | Dir. | Width / type | Clock | Default | Meaning / sampling | RTL source |
| --- | --- | --- | --- | --- | --- | --- |
| `clk` | input | 1 | — | — | 寄存器上升沿时钟 | `rv_stage.v:5`, `rv_stage.v:17` |
| `rst_n` | input | 1 | `clk` | 低有效 | 异步复位 | `rv_stage.v:6`, `rv_stage.v:17` |
| `in_data` | input | `WIDTH` | `clk` | 上游提供 | 接收数据 | `rv_stage.v:7` |
| `in_valid` | input | 1 | `clk` | 上游提供 | 输入有效 | `rv_stage.v:8` |
| `in_ready` | output | 1 | `clk` | 组合计算 | 接收许可 | `rv_stage.v:9`, `rv_stage.v:15` |
| `out_data` | output | `WIDTH` | `clk` | 0 | 寄存器输出数据 | `rv_stage.v:10` |
| `out_valid` | output | 1 | `clk` | 0 | 输出有效 | `rv_stage.v:11` |
| `out_ready` | input | 1 | `clk` | 下游提供 | 下游接收许可 | `rv_stage.v:12` |

## 4. Clock and Reset（时钟与复位）

`always @(posedge clk or negedge rst_n)` 描述了上升沿寄存器和异步低有效复位。`rst_n=0` 时，`out_valid` 和 `out_data` 都清零。复位无效后，只有满足 `in_ready=1` 的时钟沿才会更新寄存器（`rv_stage.v:17-25`）。

## 5. State, Datapath and Register Behavior（状态与数据通路）

**Table 5-1 — Internal State and Registers**

| Register | Width | Reset value | Update / hold | RTL source |
| --- | --- | --- | --- | --- |
| `out_valid` | 1 | 0 | `in_ready=1` 时赋值为 `in_valid`；否则保持 | `rv_stage.v:19-22` |
| `out_data` | `WIDTH` | 0 | `in_ready && in_valid` 时接收 `in_data`；否则保持 | `rv_stage.v:18-24` |

模块没有显式 FSM。组合式 `in_ready = ~out_valid | out_ready` 决定能否更新输出寄存器（`rv_stage.v:15`）。因此缓冲有空、满两种状态，且可以在同一个上升沿输出旧数据并接收新数据。

## 6. Functional and Cycle-Level Operation（功能与周期时序）

**Cycle convention:** 表中的输入条件取 `clk` 上升沿之前的状态；输出是该上升沿完成非阻塞赋值后的状态。

**Table 6-1 — Cycle-Accurate Transaction**

| Cycle | Inputs / pre-edge condition | State before → after | Outputs after edge | RTL source |
| --- | --- | --- | --- | --- |
| C0 | `rst_n=0` | 复位 → 空 | `out_valid=0`, `out_data=0` | `rv_stage.v:17-20` |
| C1 | `in_valid=1`, `in_ready=1`, `in_data=A5` | 空 → 满 | `out_valid=1`, `out_data=A5` | `rv_stage.v:15`, `rv_stage.v:21-24` |
| C2 | `out_ready=0`, `in_ready=0` | 满 → 满 | A5 保持 | `rv_stage.v:15`, `rv_stage.v:21-25` |
| C3 | `out_ready=1`, `in_valid=1`, `in_data=3C` | 满 → 满 | 旧数据被取走，新输出为 3C | `rv_stage.v:15`, `rv_stage.v:21-24` |
| C4 | `out_ready=1`, `in_valid=0` | 满 → 空 | `out_valid=0`，数据保持 3C | `rv_stage.v:21-24` |
| C5 | 无有效新数据 | 空 → 空 | 输出无效 | `rv_stage.v:21-24` |

连续使能且下游始终就绪时，模块每个上升沿都能接收一个数据字。单笔数据在接收上升沿后写入输出寄存器；缓冲满且下游未就绪时，吞吐率降为零（`rv_stage.v:15-25`）。

## 7. Timing and Waveform Scenarios（典型时序）

**Figure 7-1 — 接收、暂停与替换（RTL 推导）**

![rv_stage 接收与停顿波形](../waveforms/accept_stall_illustrative.svg)

图中的 C1 接收 A5，C2 保持 A5，C3 允许下游取走 A5 的同时接收 3C，C4 清除有效标志。原始波形数据保存在 `../waveforms/accept_stall_illustrative.json5`（`rv_stage.v:15-25`）。

## 8. Verification Evidence（验证记录）

**Table 8-1 — Module Verification**

| Check | Tool / input | Artifact | Result |
| --- | --- | --- | --- |
| RTL 接口与寄存器检查 | 源码分析 | `rv_stage.v:2-27` | 已分析 |
| 时序图生成 | WaveDrom 子集渲染器 | `accept_stall_illustrative.svg` | 已生成（RTL 推导） |
| VCD 解析器单测 | 人工构造的 `fixture.vcd` | `fixture_trace.svg` | 解析测试通过 |
| 功能仿真与波形调试 | VCS / Verdi | — | 未执行 |

## 9. RTL Traceability and Open Issues（源码追溯与待确认事项）

- `rv_stage.v:2-4` — 模块声明和参数。
- `rv_stage.v:5-12` — 全部外部端口。
- `rv_stage.v:15` — `in_ready` 组合条件。
- `rv_stage.v:17-25` — 复位、接收和保持逻辑。
- 待确认：`WIDTH` 非默认配置的编译结果，以及 VCS 连续传输和复位覆盖测试。
