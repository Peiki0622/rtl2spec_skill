# rtl-to-spec v0.2.0 — Codex Formal IP Specification Skill

将现有 Verilog/SystemVerilog RTL **反向生成正式的、可审阅的 IP Specification**，包括编号章节、修订历史、文档控制、架构、顶层接口、时钟复位、模块状态、寄存器/存储器映射、周期级协议时序、WaveDrom/SVG 时序图、验证证据矩阵及源码追溯。

**EDA 主链指定为 Synopsys VCS + Synopsys Verdi**：VCS 负责编译/展开与仿真，Verdi 负责 FSDB 浏览/波形分析及通过 `fsdb2vcd` 导出给文档图片生成器。没有安装许可证也能用静态分析生成 `DRAFT` 文档，但不得声称完成 VCS 仿真或 Verdi 检查。该 Skill 是 Agent 指令与自有辅助脚本的组合，不是第三方商业 EDA 软件的开源替代品。

## 安装到 Codex

```bash
# 克隆本仓库
mkdir -p ~/.agents/skills
git clone https://github.com/Peiki0622/rtl2spec_skill.git ~/.agents/skills/rtl-to-spec
# 或将仓库放在目标 RTL 工程下的 .agents/skills/rtl-to-spec/
```

进入 RTL 项目目录，使用 Codex：

```text
使用 $rtl-to-spec 为当前项目生成正式的中文 IP Specification，Top 为 my_dut。
不要修改 RTL。使用真实 filelist/宏/参数，生成编号的 IP 与模块文档、
完整端口表、架构、寄存器/状态机及所有支持场景的周期级 WaveDrom 图。
EDA 优先且必须采用 Synopsys VCS + Verdi；若许可证可用，运行真实 TB，
使用 FSDB/Verdi 形成验证证据；不可用则标注 NOT RUN，严禁伪称通过。
每项关键结论给出源码路径和行号，最终输出 docs/rtl_spec/。
```

## 正式文档固定章节

**IP Spec（`ip_spec.md`）：**

| 序号 | 固定章节（正文可用中文） | 主要内容 |
| --- | --- | --- |
| 1 | Document Control | 文档号、版本、状态、修订历史、审批 |
| 2 | Scope and References | 文档边界、技术参考 |
| 3 | IP Overview and Features | IP 功能特性与限制 |
| 4 | Configuration and Deliverables | 编译参数、filelist、交付项 |
| 5 | Architecture and Hierarchy | IP 架构/模块层次/数据流 |
| 6 | External Interface Specification | 全量端口与接口时序协议 |
| 7 | Clocks, Resets and CDC | 时钟域、复位、CDC 假设 |
| 8 | Functional Operation | 各种工作模式与内部算法 |
| 9 | Timing and Waveform Scenarios | 正常、复位、连续、阻塞、异常等时序图 |
| 10 | Register and Memory Map | 软件可见寄存器/地址/存储器；没有则注明 N/A |
| 11 | Exceptions, Constraints and Integration | 异常、系统集成与使用限制 |
| 12 | Verification and Evidence | VCS/Verdi 编译、仿真、FSDB、断言证据 |
| 13 | Traceability and Open Issues | Spec → RTL 的源代码映射与问题清单 |
| A/B | Module Index / Glossary | 模块文档目录与术语 |

每个模块使用独立的九章 Module Design Specification。所有关键图表采用 `Figure 9-1` / `Table 6-1` 这种章节内编号。**详细格式请看** [`references/spec-contract.md`](references/spec-contract.md)，模板位于 `assets/templates/`。

## EDA 使用：VCS + Verdi

**准备：** VCS/Verdi 必须由用户所在 EDA 环境安装并授权；建议配置 `VERDI_HOME`。Skill 不包含也不会安装商业软件。建议有实际可编译 filelist 与 testbench。

```bash
SKILL=~/.agents/skills/rtl-to-spec
python3 "$SKILL/scripts/doctor.py"
python3 "$SKILL/scripts/vcs_verdi.py" doctor

# 在 RTL 项目根目录复制示例配置（放在项目根目录，方便解析相对路径）
cp "$SKILL/assets/templates/vcs_verdi_config.json" vcs_verdi.json
# 修改 filelist、tb_top、dut_top、output_dir、编译参数等字段
python3 "$SKILL/scripts/vcs_verdi.py" --config vcs_verdi.json plan

# 以下需要真实 VCS + Verdi 和授权；显式 --execute 才实际调用
python3 "$SKILL/scripts/vcs_verdi.py" --config vcs_verdi.json --execute compile
python3 "$SKILL/scripts/vcs_verdi.py" --config vcs_verdi.json --execute run
python3 "$SKILL/scripts/vcs_verdi.py" --config vcs_verdi.json --execute convert

# 如果需要人工 Verdi 查看 FSDB（GUI / DISPLAY 必须可用）
python3 "$SKILL/scripts/vcs_verdi.py" --config vcs_verdi.json --execute open
```

默认配置使用 VCS UCLI `call {$fsdbDumpfile(...)}; call {$fsdbDumpvars(0, TB_TOP)}` 导出 FSDB，不修改原 RTL。若项目 TB 已自行导出 FSDB，设置 `fsdb_dump_mode: "testbench"`；必须保证 FSDB 输出路径与配置一致。需根据公司 VCS 版本和项目脚本调整选项。日志和运行/转换 manifest 在 `docs/rtl_spec/eda/`。**所有实际运行的进程状态仅记录为 PROCESS_EXIT_0_UNQUALIFIED 或失败**，必须结合自检查断言/scoreboard 判定测试是否通过。

真实 FSDB 用 Verdi `fsdb2vcd` 转换后（避免转换不必要的超大波形区间），可生成文档示例图：

```bash
python3 "$SKILL/scripts/vcd_to_wavedrom.py" \
  --vcd docs/rtl_spec/eda/waves.vcd --clock tb_top.clk \
  --signals tb_top.rst_n tb_top.valid tb_top.ready \
  --cycles 12 \
  --verdi-manifest docs/rtl_spec/eda/convert_manifest.json \
  --vcs-run-manifest docs/rtl_spec/eda/run_manifest.json \
  --out docs/rtl_spec/waveforms/sample_observed.json5 \
  --svg docs/rtl_spec/waveforms/sample_observed.svg
```

`VCS/VERDI OBSERVED` 标签必须通过 VCS FSDB 和 Verdi 导出的 VCD 哈希链检查。没有两份真实 manifest 的外来 VCD，只能标记为 `VCD OBSERVED — FILE SOURCE NOT AUTHENTICATED`。使用 WaveDrom 静态推导的内容始终标记 `ILLUSTRATIVE — NOT SIMULATED`。

详细见 [`references/eda-vcs-verdi.md`](references/eda-vcs-verdi.md)。

## RTL → 文档命令

```bash
SKILL=~/.agents/skills/rtl-to-spec
python3 "$SKILL/scripts/inventory.py" --root . --filelist rtl.f --out docs/rtl_spec/inventory.json
python3 "$SKILL/scripts/scaffold.py" --root . --inventory docs/rtl_spec/inventory.json \
  --out docs/rtl_spec --top your_dut
# 接着由 Codex 读 RTL、完善所有章节和 WaveDrom 场景（草稿含 [TODO]，不能视作交付版）。
python3 "$SKILL/scripts/validate.py" --root . --docs docs/rtl_spec \
  --inventory docs/rtl_spec/inventory.json --strict
```

- `scripts/inventory.py`：词法索引、端口候选、文件 SHA256，**不能代替 VCS 完整编译展开**。
- `scripts/scaffold.py`：创建正式的 IP/模块模板，默认不覆盖。
- `scripts/render_wavedrom.py`：无联网依赖的严格 JSON 波形 SVG 子集渲染。
- `scripts/vcs_verdi.py`：有意使用 **VCS + Verdi** 的 dry-run/执行、FSDB/VCD 哈希证据记录。
- `scripts/vcd_to_wavedrom.py`：解析来自 Verdi 导出 VCD 的时钟采样值并生成 `.json5`/SVG。
- `scripts/compare_waveforms.py`：已对齐的示意图和观测图逐周期对照，不是功能证明。
- `scripts/validate.py`：章节、图表编号、引用、文件哈希等静态检验；`--release` 是额外的证据门槛，不构成人工审批。

## 示例与测试

- `examples/tiny_ip/`：8 位 ready/valid 寄存器切片、一份 testbench、VCS/Verdi 示例配置和一个**人工制作的 VCD 解析器夹具**。
- `examples/demo_output/`：已填好的正式 IP Spec + 模块 Spec + 示例 WaveDrom SVG；其 VCD **不是由 VCS 仿真得到的**，仅用于脚本测试。不可把它作为证明。
- `tests/`：Python 标准库单元测试，包含无商业 EDA 条件下的 dry-run、hash chain 和格式检验。

```bash
python3 -m unittest discover -s tests -v
```

## 许可及边界

代码和文档使用仓库根目录 MIT 许可证；不包含 VCS、Verdi、FSDB 库或上游 Skill 的源文件。所借鉴的开源项目及说明见 [`references/tool-adapters.md`](references/tool-adapters.md)。仓库公开发布的是本 Skill 本身；不要将用户工程、商业 IP、FSDB 或机密仿真结果提交到仓库。
