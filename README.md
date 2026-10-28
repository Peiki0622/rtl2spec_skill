# rtl-to-spec v0.3.0 — Codex IP Specification Skill

读取现有 Verilog/SystemVerilog RTL，生成**清晰、可审阅的中文 IP Specification**。文档包括模块架构、接口、状态/寄存器、时钟复位、周期级时序、WaveDrom/SVG 波形以及源码追溯。

v0.3.0 着重优化表达方式：**先把电路工作过程说清楚，再呈现表格和证据**。常见的「需要注意的是」「本模块旨在」「不能保证完整正确性」等套话不会在正文里反复出现；VCS/Verdi 状态集中放在验证章节。

## 安装

```bash
git clone https://github.com/Peiki0622/rtl2spec_skill.git ~/.agents/skills/rtl-to-spec
```

也可克隆到 RTL 项目的 `.agents/skills/rtl-to-spec/`，供该项目单独使用。Codex 中可用 `$rtl-to-spec` 调用。

## 在 Codex 中使用

在 RTL 项目根目录输入：

```text
使用 $rtl-to-spec 分析当前 RTL 工程，Top 为 my_dut，输出中文 IP Specification。
像一位有经验的 RTL 工程师向团队解释设计那样写：先说明模块做什么，
再说具体信号条件、时钟沿、寄存器更新和输出时序；技术细节必须准确。
每个关键接口给端口表、典型传输例子和 WaveDrom 时序图，附上 RTL 文件行号。
VCS/Verdi 的编译、仿真及波形证据放验证章节，未执行的项目写「未执行」即可。
不要在正文重复免责说明，不要修改 RTL。
```

Skill 默认自动启用 [`references/writing-style-zh.md`](references/writing-style-zh.md)，**不需要再单独安装 Humanizer**。已有中文 Spec 可以用同一个 Skill 请求「只修改叙述语言，不改技术事实、波形和表格数据」。

## Spec 交付结构

| 文档 | 主要内容 |
| --- | --- |
| `ip_spec.md` | 13 章 + 2 个附录：功能、架构、外部接口、时钟复位、时序、配置、集成、验证记录、源码追溯 |
| `modules/<name>.md` | 每个模块单独 9 章，详细解释参数、状态/寄存器及周期行为 |
| `waveforms/*.json5`, `*.svg` | 典型操作波形；图题简记「RTL 推导」或「VCS/Verdi 波形」 |
| `inventory.json` | RTL 文件、模块、端口索引与源码哈希 |
| `validation_report.json` | 章节、引用和波形文件检查结果 |
| `style_report.json`（可选） | 套话与重复免责语句的写作检查结果 |

章节采用固定英文编号键加中文小标题，例如 `## 8. Functional Operation（工作原理）`，因此既方便机器检查，也方便中文工程师阅读。模板在 [`assets/templates/`](assets/templates/)，具体章节要求在 [`references/spec-contract.md`](references/spec-contract.md)。

## 手动执行辅助脚本

以下命令展示 Codex 在内部可使用的工具链。以当前 RTL 工程为工作目录：

```bash
SKILL=~/.agents/skills/rtl-to-spec
python3 "$SKILL/scripts/doctor.py"
python3 "$SKILL/scripts/inventory.py" --root . --filelist rtl.f \
  --out docs/rtl_spec/inventory.json
python3 "$SKILL/scripts/scaffold.py" --root . \
  --inventory docs/rtl_spec/inventory.json --out docs/rtl_spec --top my_dut
# Codex 根据真实 RTL 完成模板内容、绘制波形，之后运行：
python3 "$SKILL/scripts/style_lint.py" --docs docs/rtl_spec --strict \
  --json-out docs/rtl_spec/style_report.json
python3 "$SKILL/scripts/validate.py" --root . --docs docs/rtl_spec \
  --inventory docs/rtl_spec/inventory.json --strict
```

`style_lint.py` 检查有明显 AI 腔的固定句式和散落在功能章节里的重复免责语句；它不会自动修改 RTL 或 Spec。修改完成后重新运行即可。用词检查只是辅助，关键的时序语义仍需对照 RTL。

## Synopsys VCS + Verdi

**VCS 是默认编译/仿真工具，Verdi 是默认 FSDB 波形调试工具。** 在已安装并取得授权的环境中，填写配置后运行：

```bash
cp "$SKILL/assets/templates/vcs_verdi_config.json" ./vcs_verdi.json
# 设置 filelist、tb_top、dut_top、output_dir 等
python3 "$SKILL/scripts/vcs_verdi.py" --config vcs_verdi.json plan
python3 "$SKILL/scripts/vcs_verdi.py" --config vcs_verdi.json --execute compile
python3 "$SKILL/scripts/vcs_verdi.py" --config vcs_verdi.json --execute run
python3 "$SKILL/scripts/vcs_verdi.py" --config vcs_verdi.json --execute convert
```

VCS 仿真可生成 FSDB，Verdi 的 `fsdb2vcd` 将选定信号转换为 VCD，再由 `vcd_to_wavedrom.py` 输出 SVG。编译日志、仿真运行记录及波形哈希保存在 `docs/rtl_spec/eda/`，由第 12 章（模块第 8 章）引用。若当前工程没有 VCS/Verdi 条件，文档依然可以基于 RTL 生成，验证表里记为「未执行」。

详细工具说明见 [`references/eda-vcs-verdi.md`](references/eda-vcs-verdi.md)。

## 示例和测试

- [`examples/tiny_ip/`](examples/tiny_ip/)：单级 ready/valid 寄存器缓冲及示例 testbench。
- [`examples/demo_output/ip_spec.md`](examples/demo_output/ip_spec.md)：已按新版风格编写的中文 IP Spec。
- [`examples/demo_output/modules/rv_stage.md`](examples/demo_output/modules/rv_stage.md)：对应模块 Spec。
- [`examples/demo_output/waveforms/accept_stall_illustrative.svg`](examples/demo_output/waveforms/accept_stall_illustrative.svg)：接收、暂停和替换的示例波形。
- `examples/tiny_ip/fixture.vcd` 是人工测试数据，用于检查 VCD 解析器；当前仓库不包含 VCS/Verdi 实际仿真记录。

运行离线测试：

```bash
python3 -m unittest discover -s tests -v
```

## 借鉴的开源项目

工作流参考 [`rtl-skills`](https://github.com/phamcuong21478/rtl-skills)、[`verilog-generator`](https://github.com/Eriemon/verilog-generator)；中文写作规则借鉴 [`humanizer-zh`](https://github.com/ai-zixun/humanizer-zh)、[`blader/humanizer`](https://github.com/blader/humanizer) 和简明工程写作原则。所有脚本与模板均在本仓库中独立实现，未复制上述 Skill 的源码。项目使用 MIT 许可证。
