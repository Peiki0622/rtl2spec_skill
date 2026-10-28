# 设计实施说明（2026-10-28）

## 目标

提供一个无需 FPGA/商用 EDA 即可启动、可以在 Codex 中直接触发、对已有 RTL 实现生成详细 Spec 的本地 Skill；兼容后续 Verilator、Icarus、pyslang、wavepeek、wave-mcp 的增量集成。

## 分层设计

1. **Discovery** `inventory.py`：文件与粗层级索引、源码 hash、候选 ports、模组来源；不声明解析正确性/可编译性。
2. **Codex analysis** `SKILL.md` + `references/spec-contract.md`：读编译配置，分析模块契约、时序与状态机，生成源代码证据引用。
3. **Document composition** `scaffold.py`：IP + 各模块文档，固定标题以便校验；Agent 填写真实语义和架构图。
4. **Wave artifacts** `render_wavedrom.py`：独立离线绘图；`vcd_to_wavedrom.py`：VCD 观测提取、采样约定、来源 hash。两类图必须标注证据等级。
5. **QA** `compare_waveforms.py` 比较相同边沿/采样约定的示意与观测图；`validate.py`：结构、路径、波形、文件 hash 和占位符静态检查。

## 上游设计的整合方式

- rtl-skills/vexplain/vdoc：源代码优先的模块分析和模块到 IP 文档聚合；避免移植 Claude 专属工具契约。
- verilog-generator：WaveDrom 与 Spec 联动、严格区分分析 vs 实际执行。
- Gateflow：有条件采用更强的 SV elaboration/层次分析，而不假设可用。
- vcd2wavedrom / wavepeek / wave-mcp：可选波形处理及溯源增强，不与离线基础功能强绑定。

## 已实现边界

- Python 标准库可用时，词法索引、草稿、WaveDrom JSON/SVG、VCD 样本、文档结构验证可运行。
- 不内置完整 SV elaborator，不含波形可视化 GUI，不自动综合、安装仿真器或验证设计功能。
- Codex 侧真实任务的最终正确性依赖项目编译配置、Testbench 质量和人工/EDA 核对。

## 下一阶段可选扩展（不属于这次交付已实现功能）

- 利用 pyslang AST 写确定性的接口/层次提取 adapter，取代词法候选。
- 结合 iverilog/verilator 生成通用仿真 harness 和基于 assertions 的周期追踪报告。
- 增加 SVA/形式验证，把关 `post-NBA` 周期级延迟和 ready/valid 不丢包属性。
- 针对多时钟设计输出事件时间轴，而非仅单时钟沿采样。
