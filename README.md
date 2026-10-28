# RTL-to-Spec — Codex Skill（中文使用指南）

> GitHub repo: [Peiki0622/rtl2spec_skill](https://github.com/Peiki0622/rtl2spec_skill).\n> Clone this repository and copy the repository directory into `~/.agents/skills/rtl-to-spec` (or `<RTL project>/.agents/skills/rtl-to-spec`).\n\n

将已有 **Verilog/SystemVerilog RTL** 反向整理为设计实际实现的 IP/模块规格文档，包含模块层次、参数/接口、时钟复位、状态机、周期级行为、WaveDrom 示例波形和可选 VCD 观测波形。**不会自动修改 RTL**。

> 这是一个可供 Codex 调用的 **Agent Skill**，不是声称可以不经过 Codex 语义分析就从任意 RTL 一键生成准确 Spec 的独立综合软件。脚本完成确定性的辅助工作；完整规格需要 Codex 逐模块分析。

## 安装（任选一种）

请解压发布的 `rtl-to-spec-codex-skill.zip`，压缩包顶层应包含 `rtl-to-spec/SKILL.md`。

### 项目级（推荐，可纳入 Git 管理）

```bash
mkdir -p /path/to/your-rtl-project/.agents/skills
cp -R rtl-to-spec /path/to/your-rtl-project/.agents/skills/
```

### 用户级（跨项目使用）

```bash
mkdir -p ~/.agents/skills
cp -R rtl-to-spec ~/.agents/skills/
```

Codex CLI 或 Codex IDE 的会话中输入 `$rtl-to-spec`，或通过 `/skills` 查看 Skill。如果加载列表没有刷新，重启 Codex。以上路径依据 Codex 当前公开文档。

## 调用方式

在 RTL 工程根目录启动 Codex，发送：

```text
使用 $rtl-to-spec 分析我的整个 RTL 工程，Top 为 sm4_top。
以现有 RTL 为准，不得修改源代码。输出详细中文 IP Implementation Specification
到 docs/rtl_spec，必须包含模块层次、寄存器与 FSM、接口表、真实周期延迟、
复位/正常事务/连续事务/阻塞等实际存在的示例 WaveDrom/SVG 时序波形。
请对关键结论引用 RTL 文件:行号；如果已有 testbench 则运行仿真生成 VCD，
并将仿真观测波形和静态推导示意波形区分开。
```

**注意：**`sm4_top` 仅是调用示例，请替换为项目实际 Top。若不清楚 Top，要求 Codex 根据 filelist 与实例关系明确候选并确认；不要从文件名凭空猜。

## 工作流 / 自动化工具

脚本依赖 Python **3.10+ 标准库**，不需要联网。假设 Skill 已复制到 `.agents/skills/rtl-to-spec`：

```bash
SKILL=.agents/skills/rtl-to-spec
python3 "$SKILL/scripts/doctor.py"
python3 "$SKILL/scripts/inventory.py" --root . --out docs/rtl_spec/inventory.json
# 对有编译列表的工程，推荐：... --filelist rtl.f
python3 "$SKILL/scripts/scaffold.py" --root . --inventory docs/rtl_spec/inventory.json \
  --out docs/rtl_spec --top YOUR_TOP
# 之后由 Codex 读取 RTL，并把模板中 TODO 填成真实实现分析，生成示意波形
python3 "$SKILL/scripts/render_wavedrom.py" \
  --input docs/rtl_spec/waveforms/reset.json5 \
  --output docs/rtl_spec/waveforms/reset.svg
# 真实 VCD 文件存在时可额外执行
python3 "$SKILL/scripts/vcd_to_wavedrom.py" --vcd sim/run.vcd \
  --clock tb_top.clk --signals tb_top.rst_n tb_top.valid tb_top.ready \
  --cycles 12 --out docs/rtl_spec/waveforms/transfer.json5 \
  --svg docs/rtl_spec/waveforms/transfer.svg
python3 "$SKILL/scripts/compare_waveforms.py" \
  --expected docs/rtl_spec/waveforms/example.json5 \
  --observed docs/rtl_spec/waveforms/transfer.json5 \
  --report docs/rtl_spec/waveform_compare_report.json   # 可选，需先核实对齐
python3 "$SKILL/scripts/validate.py" --root . --docs docs/rtl_spec \
  --inventory docs/rtl_spec/inventory.json --strict
```

- `inventory.py`：候选模块、端口、参数、实例、源文件哈希与行数；**词法级**, 非完整 SystemVerilog elaboration。
- `scaffold.py`：按模板创建草稿，默认不覆盖现有文档。
- `render_wavedrom.py`：离线绘制 `.json5`（需使用严格 JSON 语法、有限的 WaveDrom 符号子集）到 SVG。完整 WaveDrom JSON5 语法请用上游渲染器。
- `vcd_to_wavedrom.py`：处理 VCD 的指定信号，在时钟 0→1 边沿采样，输出 SVG 和带源 VCD 哈希的 `.meta.json`。**VCD 观测 ≠ 仿真通过 ≠ 功能正确性证明**。
- `compare_waveforms.py`：对齐后的逐周期示意图/观测图一致性对照；匹配不等于设计正确。
- `validate.py`：检查文档标题、代码引用路径/行号、波形文件、原 RTL 哈希是否变化、草稿占位符；它不验证行为论断是否为真。

## 设计交付结构

```text
docs/rtl_spec/
├── inventory.json
├── ip_spec.md
├── modules/
│   ├── your_top.md
│   └── your_submodule.md
├── waveforms/
│   ├── reset.json5
│   ├── reset.svg
│   ├── transfer.json5
│   ├── transfer.meta.json
│   └── transfer.svg
└── validation_report.json
```

## 验收与边界

- 正确区分**异步/同步复位**、非阻塞赋值的更新时刻、ready/valid 的**握手发生边沿**和输出 post-edge 的区别。
- 涉及 SV package、interface、generate、宏分支、复杂参数时，必须用现有编译配置和 Verilator / pyslang 等进行核对；否则显示为 **未完整展开 / 未验证**。
- 没有仿真器也可输出参考示意图，但**不可**标注模拟/形式验证已通过。若有 Icarus/Verilator 或可选 `wave-mcp`/`wavepeek`，可额外提取真实观测证据。
- 脚本支持 `.v`、`.sv` 的常用模块声明索引；interface、class、UDP、绑定断言、复杂 macro 和完整 SV 前端超出了内置词法扫描的准确性边界。
- `waveform` SVG 属于源逻辑解释辅助，既不是硬件实测，也不是安全性验证。

## 自检

```bash
python3 -m unittest discover -s rtl-to-spec/tests -v
```

测试用到内附的小型 valid-ready RTL 与**手工构建的 VCD 测试夹具**；该 VCD 仅用于测试解析器，不能充当真实仿真证据。示范输出保存在 `examples/demo_output/`。

## 上游参考及许可

该 Skill 中的 Python 辅助代码和文档为独立实现，按照仓库根目录 `LICENSE`（MIT）授权；没有拷贝上游源文件。借鉴的开源设计思想、链接及许可证详见 [`references/tool-adapters.md`](references/tool-adapters.md)。